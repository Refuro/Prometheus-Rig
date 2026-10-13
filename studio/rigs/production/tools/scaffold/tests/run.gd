extends Node
## Runs every tests/test_*.gd, prints PASS/FAIL per test and a TESTS summary line, exits 0 or 1.
## godot --headless --path <project> res://tests/run.tscn   (tools/build.py does this)
## Only some tests: add -- --only=<word> (matches file or method names).


func _ready() -> void:
	var only := ""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	var passed := 0
	var failed := 0
	var files := Array(DirAccess.get_files_at("res://tests"))
	files.sort()
	for f: Variant in files:
		var fname := str(f)
		if not (fname.begins_with("test_") and fname.ends_with(".gd")) or fname == "test_case.gd":
			continue
		var script: GDScript = load("res://tests/" + fname)
		for m: Dictionary in script.get_script_method_list():
			var method := str(m["name"])
			if not method.begins_with("test_"):
				continue
			if only != "" and not (only in fname or only in method):
				continue
			var t: Node = script.new()
			add_child(t)
			await t.call(method)
			var fails: Array = t.get("failures")
			if fails.is_empty():
				passed += 1
				print("PASS %s::%s" % [fname, method])
			else:
				failed += 1
				for msg: Variant in fails:
					print("FAIL %s::%s: %s" % [fname, method, str(msg)])
			t.queue_free()
			await get_tree().process_frame
	print("TESTS passed=%d failed=%d" % [passed, failed])
	get_tree().quit(1 if failed > 0 or passed == 0 else 0)
