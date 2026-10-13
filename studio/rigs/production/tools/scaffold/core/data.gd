extends Node
## Design data, synced from the design job into res://data/ (never edited by hand).
## Data.file("feel/sim") -> the whole file; Data.value("feel/sim", "tick_hz") -> its "value".

const ROOT := "res://data"

var _files: Dictionary = {}


func _ready() -> void:
	_load_dir(ROOT)


func _load_dir(dir_path: String) -> void:
	for sub: String in DirAccess.get_directories_at(dir_path):
		_load_dir(dir_path.path_join(sub))
	for f: String in DirAccess.get_files_at(dir_path):
		if not f.ends_with(".json") or f == "SYNCED.json":
			continue
		var path := dir_path.path_join(f)
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
		if parsed is Dictionary:
			var key := path.trim_prefix(ROOT + "/").trim_suffix(".json")
			_files[key] = parsed
		else:
			push_error("data: cannot parse " + path)


func has_file(key: String) -> bool:
	return _files.has(key)


func file(key: String) -> Dictionary:
	if not _files.has(key):
		push_error("data: no file " + key)
		return {}
	return _files[key]


func keys() -> Array:
	return _files.keys()


## Returns entry["value"] for {"value": ..., "range": ..., "why": ...} entries, else the entry itself.
func value(key: String, name: String) -> Variant:
	var f := file(key)
	if not f.has(name):
		push_error("data: %s has no %s" % [key, name])
		return null
	var entry: Variant = f[name]
	if entry is Dictionary and (entry as Dictionary).has("value"):
		return (entry as Dictionary)["value"]
	return entry
