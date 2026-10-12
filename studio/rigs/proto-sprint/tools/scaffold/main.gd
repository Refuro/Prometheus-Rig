extends Node2D
## Prototype entry point. Replace with the core rule.
## ProtoUI shows ABOUT.txt as a title card; call ui.hint("...") for contextual hints. R restarts.

var ui: ProtoUI


func _ready() -> void:
	ui = ProtoUI.new()
	add_child(ui)
	print("PROTO_READY")


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and (event as InputEventKey).keycode == KEY_R:
		get_tree().reload_current_scene()
