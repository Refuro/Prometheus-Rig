extends Node3D
## Co-op prototype entry point: host-authoritative networking over ENet, with a
## stage framework and the round-3 presentation layer (ProtoUI).
##
## Networking pattern (keep it unless the spec needs otherwise):
##   clients send INPUT to the host (submit_input), the host simulates everything
##   (_simulate) and broadcasts STATE every physics tick (receive_state); clients
##   only draw it. The stage index is part of the state, so the host drives
##   stage changes for everyone.
##
## Modes:
##   no arguments on desktop  -> Host / Join menu
##   web build or --preview   -> offline preview with bot players (for screenshots
##                               and quick looks; real play is Host/Join on Windows)
## Command line (after --), used by tools/net_test.py:
##   --host | --join=<ip>   --port=<n>   --bot   --seconds=<n>   --freeze=<n>
##   --report=<path>   --report-at=<n>   --clock=<unix time>   --preview
## Keys: R restart stage (host), H controls, 1-9 jump to stage (host; the
## screenshot tool uses these). All player-facing words live in text.json.

const DEFAULT_PORT: int = 24565
const MAX_PLAYERS: int = 4
const SPEED: float = 5.0
const STAGE_COUNT: int = 3
const PLAYER_COLORS: Array[Color] = [Color("f2c14e"), Color("f28f3b"), Color("e86a92"), Color("c8a2f2")]
const GOAL_COLOR: Color = Color("7bd389")
const GROUND_COLOR: Color = Color("3b4256")

var port: int = DEFAULT_PORT
var ui: ProtoUI
var cam: Camera3D
var players: Dictionary = {}        # peer id -> Node3D (visual on every peer)
var inputs: Dictionary = {}         # peer id -> Vector2 (host only)
var positions: Dictionary = {}      # peer id -> Vector3 (host is the source of truth)
var stage: int = 0
var shown_stage: int = -1
var goal_pos: Vector3 = Vector3.ZERO
var stage_root: Node3D
var preview: bool = false
var preview_bots: Array[int] = []
var bot: bool = false
var report_path: String = ""
var quit_at: float = -1.0
var freeze_at: float = -1.0
var report_at: float = -1.0
var reported: bool = false
var clock_start: float = -1.0
var elapsed: float = 0.0
var ticks: int = 0
var clearing: bool = false
var menu: Control
var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var bot_dirs: Dictionary = {}
var bot_timer: float = 0.0


func _ready() -> void:
	_build_world()
	ui = ProtoUI.new()
	add_child(ui)
	var args: Dictionary = _parse_args()
	bot = args.has("bot")
	if args.has("port"):
		port = int(args["port"])
	report_path = str(args.get("report", ""))
	if args.has("seconds"):
		quit_at = float(args["seconds"])
		freeze_at = quit_at - 2.0
	if args.has("freeze"):
		freeze_at = float(args["freeze"])
	if args.has("report-at"):
		report_at = float(args["report-at"])
	if args.has("clock"):
		clock_start = float(args["clock"])
	multiplayer.peer_connected.connect(_on_peer_connected)
	multiplayer.peer_disconnected.connect(_on_peer_disconnected)
	if args.has("host"):
		host()
	elif args.has("join"):
		join(str(args["join"]))
	elif args.has("preview") or OS.has_feature("web"):
		start_preview()
	else:
		_build_menu()
	print("PROTO_READY")


func _parse_args() -> Dictionary:
	var out: Dictionary = {}
	for a: String in OS.get_cmdline_user_args():
		var kv: PackedStringArray = a.trim_prefix("--").split("=", true, 1)
		out[kv[0]] = kv[1] if kv.size() > 1 else true
	return out


func host() -> void:
	var peer := ENetMultiplayerPeer.new()
	var err: Error = peer.create_server(port, MAX_PLAYERS)
	if err != OK:
		push_error("host failed: %s" % err)
		return
	multiplayer.multiplayer_peer = peer
	_add_player(1)
	_hide_menu()
	load_stage(0)
	print("NET_HOSTING port=%d" % port)


func join(address: String) -> void:
	var peer := ENetMultiplayerPeer.new()
	var err: Error = peer.create_client(address, port)
	if err != OK:
		push_error("join failed: %s" % err)
		return
	multiplayer.multiplayer_peer = peer
	_hide_menu()
	print("NET_JOINING %s" % address)


## Offline: the default OfflineMultiplayerPeer makes this instance the host.
## Bot players stand in for friends so the screen looks like a real session.
func start_preview() -> void:
	preview = true
	_add_player(1)
	for id: int in [2, 3]:
		preview_bots.append(id)
		_add_player(id)
	load_stage(0)


func _on_peer_connected(id: int) -> void:
	if multiplayer.is_server():
		_add_player(id)
		print("NET_PEER_JOINED %d" % id)


func _on_peer_disconnected(id: int) -> void:
	if multiplayer.is_server():
		positions.erase(id)
		inputs.erase(id)


func _add_player(id: int) -> void:
	positions[id] = Vector3(-6.0 + positions.size() * 1.2, 0.5, 4.0)
	inputs[id] = Vector2.ZERO


## Host only: set up stage i. Each stage adds ONE new idea (brief section 4).
func load_stage(i: int) -> void:
	stage = clampi(i, 0, STAGE_COUNT - 1)
	clearing = false
	goal_pos = Vector3(-3.0 + stage * 4.0, 0.0, -3.0)    # EXAMPLE: the goal moves further each stage
	var n: int = 0
	for id: int in positions.keys():
		positions[id] = Vector3(-6.0 + n * 1.2, 0.5, 4.0)
		n += 1


## Every peer: rebuild what's drawn for a stage when it changes.
func _show_stage(i: int) -> void:
	shown_stage = i
	if stage_root:
		stage_root.queue_free()
	stage_root = Node3D.new()
	add_child(stage_root)
	var ring := MeshInstance3D.new()
	var torus := TorusMesh.new()
	torus.inner_radius = 1.4
	torus.outer_radius = 1.7
	ring.mesh = torus
	ring.material_override = _flat(GOAL_COLOR)
	ring.position = goal_pos
	stage_root.add_child(ring)
	ui.goal("stage.%d.goal" % (i + 1))
	ui.banner("stage.%d.name" % (i + 1))


func _physics_process(delta: float) -> void:
	elapsed += delta
	if clock_start > 0.0:
		elapsed = Time.get_unix_time_from_system() - clock_start
	if report_at > 0.0 and elapsed >= report_at and not reported:
		_write_report()
	if quit_at > 0.0 and elapsed >= quit_at:
		_finish()
		return
	if not preview and (multiplayer.multiplayer_peer == null or multiplayer.multiplayer_peer.get_connection_status() != MultiplayerPeer.CONNECTION_CONNECTED):
		return
	var local_input: Vector2 = _read_input(delta)
	if multiplayer.is_server():
		inputs[1] = local_input
		for id: int in preview_bots:
			inputs[id] = _bot_dir(id, delta)
		_simulate(delta)
		ticks += 1
		var snap: Dictionary = _state_snapshot()
		if not preview:
			receive_state.rpc(snap)
		_apply_snapshot(snap)
	else:
		submit_input.rpc_id(1, local_input)


func _read_input(delta: float) -> Vector2:
	if bot:
		return _bot_dir(multiplayer.get_unique_id(), delta)
	if ui.is_blocking():
		return Vector2.ZERO
	var dir: Vector2 = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
	if dir != Vector2.ZERO:
		ui.hint_once("hint.move")
	return dir


func _bot_dir(id: int, delta: float) -> Vector2:
	# Bots stop moving near the end so every peer can settle on the same state.
	if freeze_at > 0.0 and elapsed > freeze_at:
		return Vector2.ZERO
	bot_timer -= delta
	if bot_timer <= 0.0 or not bot_dirs.has(id):
		bot_timer = 0.7
		for k: Variant in bot_dirs.keys() + [id]:
			bot_dirs[k] = Vector2(rng.randf_range(-1, 1), rng.randf_range(-1, 1)).limit_length(1.0)
	return bot_dirs[id]


@rpc("any_peer", "call_remote", "unreliable_ordered")
func submit_input(dir: Vector2) -> void:
	if multiplayer.is_server():
		inputs[multiplayer.get_remote_sender_id()] = dir.limit_length(1.0)


func _simulate(delta: float) -> void:
	## Host only. Replace with the game's rules. EXAMPLE: everyone must stand in the ring.
	var all_in: bool = not positions.is_empty()
	for id: int in positions.keys():
		var d: Vector2 = inputs.get(id, Vector2.ZERO)
		var p: Vector3 = positions[id] + Vector3(d.x, 0.0, d.y) * SPEED * delta
		positions[id] = Vector3(clampf(p.x, -9.5, 9.5), p.y, clampf(p.z, -9.5, 9.5))
		if Vector2(positions[id].x - goal_pos.x, positions[id].z - goal_pos.z).length() > 1.5:
			all_in = false
	if all_in and not clearing and not preview:
		_stage_cleared()


func _stage_cleared() -> void:
	clearing = true
	_celebrate.rpc()
	await get_tree().create_timer(1.4).timeout
	if stage + 1 < STAGE_COUNT:
		load_stage(stage + 1)


@rpc("authority", "call_local", "reliable")
func _celebrate() -> void:
	ui.banner("cleared" if stage + 1 < STAGE_COUNT else "end", 1.4)


func _state_snapshot() -> Dictionary:
	return {"t": ticks, "stage": stage, "goal": goal_pos, "pos": positions.duplicate()}


@rpc("authority", "call_remote", "unreliable_ordered")
func receive_state(state: Dictionary) -> void:
	ticks = int(state["t"])
	stage = int(state["stage"])
	goal_pos = state["goal"]
	_apply_snapshot(state)


func _apply_snapshot(state: Dictionary) -> void:
	if int(state["stage"]) != shown_stage:
		_show_stage(int(state["stage"]))
	var pos: Dictionary = state["pos"]
	for id: int in pos.keys():
		if not players.has(id):
			players[id] = _make_player_visual(id)
		(players[id] as Node3D).position = pos[id]
	for id: int in players.keys():
		if not pos.has(id):
			(players[id] as Node3D).queue_free()
			players.erase(id)
	ui.mark("goal", cam.unproject_position(goal_pos + Vector3(0, 0.5, 0)), GOAL_COLOR)


func _make_player_visual(id: int) -> Node3D:
	var body := MeshInstance3D.new()
	body.mesh = CapsuleMesh.new()
	body.material_override = _flat(PLAYER_COLORS[players.size() % PLAYER_COLORS.size()])
	var hat := MeshInstance3D.new()        # a simple shape so players differ by silhouette too
	var cone := CylinderMesh.new()
	cone.top_radius = 0.0
	cone.bottom_radius = 0.35
	cone.height = 0.5
	hat.mesh = cone
	hat.position = Vector3(0, 1.25, 0)
	hat.material_override = _flat(Color("11141c"))
	body.add_child(hat)
	body.name = "Player%d" % id
	add_child(body)
	return body


func _flat(c: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	return m


func _build_world() -> void:
	RenderingServer.set_default_clear_color(Color("1d2230"))
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(20, 20)
	floor_mesh.mesh = plane
	floor_mesh.material_override = _flat(GROUND_COLOR)
	add_child(floor_mesh)
	cam = Camera3D.new()
	cam.position = Vector3(0, 14, 11)
	add_child(cam)
	cam.look_at(Vector3.ZERO)


func _build_menu() -> void:
	menu = VBoxContainer.new()
	menu.position = Vector2(40, 560)
	var address := LineEdit.new()
	address.placeholder_text = ProtoUI.t("menu.address")
	address.custom_minimum_size = Vector2(360, 0)
	var host_button := Button.new()
	host_button.text = ProtoUI.t("menu.host")
	host_button.pressed.connect(host)
	var join_button := Button.new()
	join_button.text = ProtoUI.t("menu.join")
	join_button.pressed.connect(func() -> void: join(address.text.strip_edges()))
	menu.add_child(host_button)
	menu.add_child(address)
	menu.add_child(join_button)
	var layer := CanvasLayer.new()
	layer.add_child(menu)
	add_child(layer)


func _hide_menu() -> void:
	if menu:
		menu.visible = false


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo) or not multiplayer.is_server():
		return
	var key: Key = (event as InputEventKey).keycode
	if key == KEY_R:
		load_stage(stage)
	elif key >= KEY_1 and key <= KEY_9 and key - KEY_1 < STAGE_COUNT:
		load_stage(key - KEY_1)


func _finish() -> void:
	if not reported:
		_write_report()
	get_tree().quit()


func _write_report() -> void:
	reported = true
	if report_path == "":
		return
	var role: String = "none"
	var my_id: int = 0
	var peers: Array = []
	if multiplayer.multiplayer_peer != null and multiplayer.multiplayer_peer.get_connection_status() == MultiplayerPeer.CONNECTION_CONNECTED:
		role = "host" if multiplayer.is_server() else "client"
		my_id = multiplayer.get_unique_id()
		peers = Array(multiplayer.get_peers())
	var state: Dictionary = {}
	for id: int in players.keys():
		var p: Vector3 = (players[id] as Node3D).position
		state[str(id)] = [p.x, p.y, p.z]
	state["stage"] = [float(stage), 0.0, 0.0]
	var f := FileAccess.open(report_path, FileAccess.WRITE)
	f.store_string(JSON.stringify({"role": role, "id": my_id, "peers": peers, "ticks": ticks, "state": state}))
	f.close()
