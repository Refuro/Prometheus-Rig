extends Node
## Dev-only hooks. Off in release builds; on in the editor, in tests and in the web build
## (export feature "dev_tools").
## Screenshots: game code registers named shots (DevTools.register_shot("title", callable)); the
## screenshot run (tools/shots.cjs, list in shots.json) calls window.godotShot(name) in the web build,
## the callable sets the scene up, and DevTools prints SHOT_READY <name>.

var enabled: bool = false
var _shots: Dictionary = {}
var _js_callback: Variant = null


func _ready() -> void:
	enabled = OS.has_feature("dev_tools") or OS.has_feature("editor")
	if enabled and OS.has_feature("web"):
		_js_callback = JavaScriptBridge.create_callback(_on_js_shot)
		var window: JavaScriptObject = JavaScriptBridge.get_interface("window")
		window.godotShot = _js_callback


## Call once the first screen is up. The screenshot run waits for this line.
func announce_ready() -> void:
	if enabled:
		print("GAME_READY data_files=%d" % Data.keys().size())


func register_shot(shot_name: String, setup: Callable) -> void:
	_shots[shot_name] = setup


func shot_names() -> Array:
	return _shots.keys()


func run_shot(shot_name: String) -> bool:
	if not _shots.has(shot_name):
		print("SHOT_MISSING " + shot_name)
		return false
	await (_shots[shot_name] as Callable).call()
	await get_tree().process_frame
	await get_tree().process_frame
	print("SHOT_READY " + shot_name)
	return true


func _on_js_shot(args: Array) -> void:
	if args.size() > 0:
		run_shot(str(args[0]))
