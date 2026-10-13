extends "res://tests/test_case.gd"
## Checks the scaffold's plumbing. Keep it; add your own test_<area>.gd files beside it.


func test_data_loads() -> void:
	check(not Data.keys().is_empty(), "res://data has JSON files (run tools/sync_data.py)")


func test_text_ids_resolve() -> void:
	check_eq(Text.t_or("no.such.id", "fallback"), "fallback", "t_or falls back")


func test_platform_records_achievements() -> void:
	Platform.reset_for_tests()
	Platform.unlock_achievement("ACH_TEST")
	Platform.unlock_achievement("ACH_TEST")
	check_eq(Platform.unlocked.size(), 1, "achievement recorded once")
	check(not Platform.is_steam(), "null platform in tests")
	Platform.reset_for_tests()
