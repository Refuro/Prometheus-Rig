extends Control
## Placeholder first screen. The tech lead replaces it with the real boot flow.

@onready var _title: Label = $Title


func _ready() -> void:
	_title.text = Text.t_or("game.title", str(ProjectSettings.get_setting("application/config/name")))
	DevTools.register_shot("title", _shot_title)
	DevTools.announce_ready()


func _shot_title() -> void:
	pass
