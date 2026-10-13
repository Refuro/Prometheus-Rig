extends Node
## Every player-facing string, by id, from res://data/text/ ({"strings": [{"id", "context", "text"}]}).
## Text.t("menu.play"). A missing id shows as [[id]] so it is easy to spot in screenshots.

var _strings: Dictionary = {}


func _ready() -> void:
	for key: Variant in Data.keys():
		var k := str(key)
		if not k.begins_with("text/"):
			continue
		var list: Variant = Data.file(k).get("strings", [])
		if list is Array:
			for s: Variant in list:
				if s is Dictionary and (s as Dictionary).has("id"):
					_strings[str(s["id"])] = str((s as Dictionary).get("text", ""))


func has(id: String) -> bool:
	return _strings.has(id)


func t(id: String) -> String:
	if not _strings.has(id):
		push_warning("text: missing id " + id)
		return "[[" + id + "]]"
	return _strings[id]


func t_or(id: String, fallback: String) -> String:
	return _strings.get(id, fallback)
