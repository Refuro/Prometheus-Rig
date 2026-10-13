class_name ProtoUI
extends CanvasLayer
## Presentation layer for prototypes. Rules it supports (brief section 4):
##   - a short splash (title + one-line goal), then straight into play;
##   - a goal bar that always shows what to do right now (short);
##   - hints that appear once, when the player meets something new (short);
##   - markers that point at where the goal is in the world;
##   - a stage banner and a celebration when a stage is cleared;
##   - H opens a controls card (controls only, not rules).
## All player-facing words come from res://text.json via ProtoUI.t("key").

signal splash_closed

const HINT_SECONDS: float = 3.5
const INK: Color = Color(0.96, 0.96, 0.94)
const PANEL: Color = Color(0.08, 0.09, 0.12, 0.82)

static var _text: Dictionary = {}

var _goal: Label
var _hint: Label
var _banner: Label
var _splash: PanelContainer
var _help: PanelContainer
var _markers: Array[Dictionary] = []
var _hint_timer: float = 0.0
var _banner_timer: float = 0.0
var _seen_hints: Dictionary = {}
var _overlay: Control


static func t(key: String) -> String:
	if _text.is_empty():
		var raw: String = FileAccess.get_file_as_string("res://text.json")
		var parsed: Variant = JSON.parse_string(raw)
		if parsed is Dictionary:
			for s: Dictionary in (parsed as Dictionary).get("strings", []):
				_text[str(s.get("id", ""))] = str(s.get("text", ""))
	return str(_text.get(key, "[" + key + "]"))


func _ready() -> void:
	layer = 100
	_overlay = Control.new()
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.draw.connect(_draw_markers)
	add_child(_overlay)
	_goal = _label(24, Vector2(0, 14), true)
	_hint = _label(20, Vector2(0, 660), true)
	_banner = _label(44, Vector2(0, 290), true)
	_goal.visible = false
	_hint.visible = false
	_banner.visible = false
	_splash = _panel(t("splash.title") + "\n\n" + t("splash.goal") + "\n\n" + t("splash.start"), 34)
	_help = _panel(t("help.controls"), 22)
	_help.visible = false


func _label(size: int, pos: Vector2, centered: bool) -> Label:
	var l := Label.new()
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", INK)
	l.add_theme_color_override("font_outline_color", Color.BLACK)
	l.add_theme_constant_override("outline_size", 6)
	l.position = pos
	if centered:
		l.size = Vector2(1280, size * 2)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(l)
	return l


func _panel(body: String, size: int) -> PanelContainer:
	var p := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = PANEL
	style.set_corner_radius_all(14)
	style.set_content_margin_all(32)
	p.add_theme_stylebox_override("panel", style)
	var l := Label.new()
	l.text = body
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", INK)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(640, 0)
	p.add_child(l)
	add_child(p)
	p.position = Vector2(320, 200)
	return p


func is_blocking() -> bool:
	return _splash.visible or _help.visible


## The one line that says what to do right now. Keep it short (budget: goal).
func goal(text_key: String) -> void:
	_goal.text = t(text_key)
	_goal.visible = true


## Shown once per key, the first time the player meets something new.
func hint_once(text_key: String) -> void:
	if _seen_hints.has(text_key):
		return
	_seen_hints[text_key] = true
	_hint.text = t(text_key)
	_hint.visible = true
	_hint_timer = HINT_SECONDS


## Point at a world position (screen coordinates for 2D; use unproject for 3D).
func mark(id: String, screen_pos: Vector2, color: Color = Color(1.0, 0.85, 0.2)) -> void:
	for m: Dictionary in _markers:
		if m["id"] == id:
			m["pos"] = screen_pos
			m["color"] = color
			_overlay.queue_redraw()
			return
	_markers.append({"id": id, "pos": screen_pos, "color": color})
	_overlay.queue_redraw()


func unmark(id: String) -> void:
	_markers = _markers.filter(func(m: Dictionary) -> bool: return m["id"] != id)
	_overlay.queue_redraw()


func banner(text_key: String, seconds: float = 1.6) -> void:
	_banner.text = t(text_key)
	_banner.visible = true
	_banner_timer = seconds


func _draw_markers() -> void:
	var pulse: float = 0.5 + 0.5 * sin(Time.get_ticks_msec() / 180.0)
	for m: Dictionary in _markers:
		var p: Vector2 = m["pos"]
		var c: Color = m["color"]
		_overlay.draw_arc(p, 26.0 + pulse * 8.0, 0.0, TAU, 40, c, 4.0)
		_overlay.draw_colored_polygon(PackedVector2Array([p + Vector2(-12, -58), p + Vector2(12, -58), p + Vector2(0, -38)]), c)


func _process(delta: float) -> void:
	if not _markers.is_empty():
		_overlay.queue_redraw()
	if _hint_timer > 0.0:
		_hint_timer -= delta
		if _hint_timer <= 0.0:
			_hint.visible = false
	if _banner_timer > 0.0:
		_banner_timer -= delta
		if _banner_timer <= 0.0:
			_banner.visible = false


func _input(event: InputEvent) -> void:
	var pressed: bool = (event is InputEventKey and event.pressed and not event.echo) or (event is InputEventMouseButton and event.pressed)
	if not pressed:
		return
	if _splash.visible:
		_splash.visible = false
		get_viewport().set_input_as_handled()
		splash_closed.emit()
	elif _help.visible:
		_help.visible = false
		get_viewport().set_input_as_handled()
	elif event is InputEventKey and (event as InputEventKey).keycode == KEY_H:
		_help.visible = true
		get_viewport().set_input_as_handled()
