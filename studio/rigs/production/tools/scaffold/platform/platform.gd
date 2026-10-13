extends Node
## The one door to Steam. This null version runs everywhere (editor, tests, web, no Steam) and
## records every request so tests can check achievements, presence and cloud saves.
## When GodotSteam is installed, the tech lead adds a Steam-backed version behind the same calls.

var unlocked: Array[String] = []
var presence: Dictionary = {}
var cloud: Dictionary = {}


func is_steam() -> bool:
	return false


func unlock_achievement(id: String) -> void:
	if not unlocked.has(id):
		unlocked.append(id)


func set_presence(key: String, value: String) -> void:
	presence[key] = value


func cloud_write(file_name: String, bytes: PackedByteArray) -> bool:
	cloud[file_name] = bytes
	return true


func cloud_read(file_name: String) -> PackedByteArray:
	return cloud.get(file_name, PackedByteArray())


func reset_for_tests() -> void:
	unlocked.clear()
	presence.clear()
	cloud.clear()
