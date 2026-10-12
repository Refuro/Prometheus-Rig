class_name ProtoUI
extends CanvasLayer
## Title card + contextual hints for prototypes.
## The title card shows res://ABOUT.txt on launch; any key or click closes it, H reopens it.
## Call hint("Drop the cheese near the elephant to lure it") from game code to show a hint.

const HINT_SECONDS: float = 4.0

var _card: PanelContainer
var _hint: Label
var _hint_timer: float = 0.0


func _ready() -> void:
	layer = 100
	_card = PanelContainer.new()
	_card.set_anchors_preset(Control.PRESET_CENTER)
	_card.custom_minimum_size = Vector2(760, 0)
	var text := Label.new()
	text.text = _about_text()
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.add_theme_font_size_override("font_size", 20)
	text.custom_minimum_size = Vector2(700, 0)
	var box := MarginContainer.new()
	for side: String in ["left", "right", "top", "bottom"]:
		box.add_theme_constant_override("margin_" + side, 28)
	box.add_child(text)
	_card.add_child(box)
	add_child(_card)
	_card.position = Vector2(640 - 380, 120)

	_hint = Label.new()
	_hint.add_theme_font_size_override("font_size", 20)
	_hint.position = Vector2(16, 680)
	_hint.visible = false
	add_child(_hint)


func _about_text() -> String:
	var body: String = FileAccess.get_file_as_string("res://ABOUT.txt")
	if body.is_empty():
		body = "ABOUT.txt is missing."
	print("PROTO_ABOUT_CHARS ", body.length())
	return body.strip_edges() + "\n\nPress any key to start. H shows this again. R restarts."


func is_card_open() -> bool:
	return _card.visible


func hint(message: String, seconds: float = HINT_SECONDS) -> void:
	_hint.text = message
	_hint.visible = true
	_hint_timer = seconds


func _process(delta: float) -> void:
	if _hint_timer > 0.0:
		_hint_timer -= delta
		if _hint_timer <= 0.0:
			_hint.visible = false


func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var key: InputEventKey = event as InputEventKey
		if _card.visible:
			_card.visible = false
			get_viewport().set_input_as_handled()
		elif key.keycode == KEY_H:
			_card.visible = true
	elif event is InputEventMouseButton and event.pressed and _card.visible:
		_card.visible = false
		get_viewport().set_input_as_handled()
