extends Node3D
## Co-op prototype entry point: host-authoritative networking over ENet.
##
## Pattern (keep it unless the spec needs otherwise):
##   clients send INPUT to the host (submit_input), the host simulates
##   everything, and broadcasts STATE to all peers every physics tick
##   (receive_state). Clients only draw what the host says.
## Extend _simulate() and _state_snapshot()/_apply_snapshot() with the game.
##
## Command line (after --), used by tools/net_test.py and handy for testing:
##   --host                 host a game        --join=<ip>   join a host
##   --port=<n>             network port (default 24565)
##   --bot                  random inputs      --seconds=<n> quit after n seconds
##   --freeze=<n>           bots stop moving after n seconds (default: 2 s before quitting)
##   --report=<path>        write a JSON state report on quit (or at --report-at=<n> seconds)
##   --clock=<unix time>    makes --seconds/--freeze/--report-at count from this shared start time,
##                          so several instances act at the same moment (used by net_test.py)
## With no arguments a Host / Join menu is shown.

const DEFAULT_PORT: int = 24565
const MAX_PLAYERS: int = 4
const SPEED: float = 5.0
const COLORS: Array[Color] = [Color(0.9, 0.3, 0.3), Color(0.3, 0.6, 0.95), Color(0.35, 0.85, 0.4), Color(0.95, 0.8, 0.25)]

var port: int = DEFAULT_PORT
var ui: ProtoUI
var players: Dictionary = {}        # peer id -> Node3D (visual on every peer)
var inputs: Dictionary = {}         # peer id -> Vector2 (host only)
var positions: Dictionary = {}      # peer id -> Vector3 (host is the source of truth)
var bot: bool = false
var report_path: String = ""
var quit_at: float = -1.0
var freeze_at: float = -1.0
var report_at: float = -1.0
var reported: bool = false
var clock_start: float = -1.0
var elapsed: float = 0.0
var ticks: int = 0
var menu: Control
var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var bot_dir: Vector2 = Vector2.ZERO
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


func _on_peer_connected(id: int) -> void:
	if multiplayer.is_server():
		_add_player(id)
		print("NET_PEER_JOINED %d" % id)


func _on_peer_disconnected(id: int) -> void:
	if multiplayer.is_server():
		positions.erase(id)
		inputs.erase(id)
	if players.has(id):
		(players[id] as Node3D).queue_free()
		players.erase(id)


func _add_player(id: int) -> void:
	positions[id] = Vector3(players.size() * 1.5 - 2.0, 0.5, 0.0)
	inputs[id] = Vector2.ZERO


func _physics_process(delta: float) -> void:
	elapsed += delta
	if clock_start > 0.0:
		elapsed = Time.get_unix_time_from_system() - clock_start
	if report_at > 0.0 and elapsed >= report_at and not reported:
		_write_report()
	if quit_at > 0.0 and elapsed >= quit_at:
		_finish()
		return
	if multiplayer.multiplayer_peer == null or multiplayer.multiplayer_peer.get_connection_status() != MultiplayerPeer.CONNECTION_CONNECTED:
		return
	var local_input: Vector2 = _read_input(delta)
	if multiplayer.is_server():
		inputs[1] = local_input
		_simulate(delta)
		ticks += 1
		receive_state.rpc(_state_snapshot())
		_apply_snapshot(_state_snapshot())
	else:
		submit_input.rpc_id(1, local_input)


func _read_input(delta: float) -> Vector2:
	if bot:
		# Bots stop moving near the end so every peer can settle on the same state.
		if freeze_at > 0.0 and elapsed > freeze_at:
			return Vector2.ZERO
		bot_timer -= delta
		if bot_timer <= 0.0:
			bot_timer = 0.7
			bot_dir = Vector2(rng.randf_range(-1, 1), rng.randf_range(-1, 1)).limit_length(1.0)
		return bot_dir
	if ui.is_card_open():
		return Vector2.ZERO
	return Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")


@rpc("any_peer", "call_remote", "unreliable_ordered")
func submit_input(dir: Vector2) -> void:
	if multiplayer.is_server():
		inputs[multiplayer.get_remote_sender_id()] = dir.limit_length(1.0)


func _simulate(delta: float) -> void:
	## Host only. Replace with the game's rules.
	for id: int in positions.keys():
		var d: Vector2 = inputs.get(id, Vector2.ZERO)
		var p: Vector3 = positions[id] + Vector3(d.x, 0.0, d.y) * SPEED * delta
		positions[id] = Vector3(clampf(p.x, -9.5, 9.5), p.y, clampf(p.z, -9.5, 9.5))


func _state_snapshot() -> Dictionary:
	return {"t": ticks, "pos": positions.duplicate()}


@rpc("authority", "call_remote", "unreliable_ordered")
func receive_state(state: Dictionary) -> void:
	ticks = int(state["t"])
	_apply_snapshot(state)


func _apply_snapshot(state: Dictionary) -> void:
	var pos: Dictionary = state["pos"]
	for id: int in pos.keys():
		if not players.has(id):
			players[id] = _make_player_visual(id)
		(players[id] as Node3D).position = pos[id]
	for id: int in players.keys():
		if not pos.has(id):
			(players[id] as Node3D).queue_free()
			players.erase(id)


func _make_player_visual(id: int) -> Node3D:
	var mesh := MeshInstance3D.new()
	mesh.mesh = CapsuleMesh.new()
	var mat := StandardMaterial3D.new()
	mat.albedo_color = COLORS[players.size() % COLORS.size()]
	mesh.material_override = mat
	mesh.name = "Player%d" % id
	add_child(mesh)
	return mesh


func _build_world() -> void:
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(20, 20)
	floor_mesh.mesh = plane
	add_child(floor_mesh)
	var cam := Camera3D.new()
	cam.position = Vector3(0, 14, 10)
	add_child(cam)
	cam.look_at(Vector3.ZERO)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, 30, 0)
	add_child(light)


func _build_menu() -> void:
	menu = VBoxContainer.new()
	menu.position = Vector2(40, 560)
	var address := LineEdit.new()
	address.placeholder_text = "Host address (Tailscale IP or name)"
	address.custom_minimum_size = Vector2(360, 0)
	var host_button := Button.new()
	host_button.text = "Host"
	host_button.pressed.connect(host)
	var join_button := Button.new()
	join_button.text = "Join"
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
	if event is InputEventKey and event.pressed and (event as InputEventKey).keycode == KEY_R and multiplayer.is_server():
		for id: int in positions.keys():
			positions[id] = Vector3(0.0, 0.5, 0.0)


func _finish() -> void:
	if not reported:
		_write_report()
	get_tree().quit()


func _write_report() -> void:
	reported = true
	if report_path != "":
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
		var f := FileAccess.open(report_path, FileAccess.WRITE)
		f.store_string(JSON.stringify({"role": role, "id": my_id, "peers": peers, "ticks": ticks, "state": state}))
		f.close()
