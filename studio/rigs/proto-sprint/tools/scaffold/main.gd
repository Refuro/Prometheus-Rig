extends Node2D
## Prototype entry point with a stage framework. Replace the example stage with
## the game; keep the flow: splash -> stage goal -> play -> cleared (celebrate) ->
## next stage, with instant retry on failure.
##
## Keys: R retry stage, H controls (ProtoUI). Debug: 1-9 jump to a stage
## (the owner and tools/shots.mjs use these; keep them working).
## Every player-facing word is a key in text.json, never a string here.

const STAGE_COUNT: int = 3          # set to the spec's number of stages
const PALETTE := {                  # see art/STYLE.md
	"bg": Color("1d2230"), "ground": Color("3b4256"), "player": Color("f2c14e"),
	"goal": Color("7bd389"), "danger": Color("e4572e"), "neutral": Color("c9ccd5"),
}

var ui: ProtoUI
var stage: int = 0
var world: Node2D
var playing: bool = false
var player: Sprite2D
var goal_pos: Vector2


func _ready() -> void:
	RenderingServer.set_default_clear_color(PALETTE["bg"])
	ui = ProtoUI.new()
	add_child(ui)
	ui.splash_closed.connect(func() -> void: playing = true)
	load_stage(0)
	print("PROTO_READY")


func load_stage(i: int) -> void:
	stage = clampi(i, 0, STAGE_COUNT - 1)
	if world:
		world.queue_free()
	world = Node2D.new()
	add_child(world)
	_build_stage(stage)
	ui.goal("stage.%d.goal" % (stage + 1))
	ui.banner("stage.%d.name" % (stage + 1))


func _build_stage(i: int) -> void:
	## EXAMPLE ONLY: walk the player to the goal. Each stage adds one idea.
	var floor := Polygon2D.new()
	floor.polygon = PackedVector2Array([Vector2(80, 560), Vector2(1200, 560), Vector2(1200, 600), Vector2(80, 600)])
	floor.color = PALETTE["ground"]
	world.add_child(floor)
	player = Sprite2D.new()
	player.texture = load("res://art/player.svg")
	player.position = Vector2(160, 520)
	world.add_child(player)
	goal_pos = Vector2(400 + i * 300, 520)
	ui.mark("goal", goal_pos, PALETTE["goal"])


func _process(delta: float) -> void:
	if not playing or ui.is_blocking():
		return
	var dir: float = Input.get_axis("ui_left", "ui_right")
	if dir != 0.0:
		ui.hint_once("hint.move")
	player.position.x += dir * 320.0 * delta
	if player.position.distance_to(goal_pos) < 30.0:
		stage_cleared()


func stage_cleared() -> void:
	playing = false
	ui.unmark("goal")
	_celebrate(player.position)
	if stage + 1 >= STAGE_COUNT:
		ui.banner("end", 3.0)
		return
	ui.banner("cleared")
	await get_tree().create_timer(1.2).timeout
	load_stage(stage + 1)
	playing = true


func stage_failed() -> void:
	ui.banner("failed", 0.8)
	await get_tree().create_timer(0.6).timeout
	load_stage(stage)


func _celebrate(at: Vector2) -> void:
	var burst := CPUParticles2D.new()
	burst.position = at
	burst.one_shot = true
	burst.amount = 40
	burst.explosiveness = 1.0
	burst.spread = 180.0
	burst.initial_velocity_min = 120.0
	burst.initial_velocity_max = 260.0
	burst.color = PALETTE["goal"]
	add_child(burst)
	burst.emitting = true


func _unhandled_input(event: InputEvent) -> void:
	if not (event is InputEventKey and event.pressed and not event.echo):
		return
	var key: Key = (event as InputEventKey).keycode
	if key == KEY_R:
		load_stage(stage)
	elif key >= KEY_1 and key <= KEY_9 and key - KEY_1 < STAGE_COUNT:
		load_stage(key - KEY_1)
		playing = true
