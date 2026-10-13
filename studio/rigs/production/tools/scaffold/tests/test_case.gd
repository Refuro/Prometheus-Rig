extends Node
## Base for tests. A test file: tests/test_<area>.gd, extends "res://tests/test_case.gd",
## with methods named test_<what>(). Methods may await. Failures are collected, not thrown.

var failures: Array[String] = []


func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)


func check_eq(actual: Variant, expected: Variant, message: String) -> void:
	if actual != expected:
		failures.append("%s: expected %s, got %s" % [message, str(expected), str(actual)])


func check_near(actual: float, expected: float, tolerance: float, message: String) -> void:
	if absf(actual - expected) > tolerance:
		failures.append("%s: expected %s ± %s, got %s" % [message, str(expected), str(tolerance), str(actual)])


func check_between(actual: float, low: float, high: float, message: String) -> void:
	if actual < low or actual > high:
		failures.append("%s: expected %s..%s, got %s" % [message, str(low), str(high), str(actual)])
