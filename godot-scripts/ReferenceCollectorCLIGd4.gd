## Finds and generates a code reference from gdscript files.
@tool
extends SceneTree


var Collector: SceneTree = load("CollectorGd4.gd").new()
## A list of directories to collect files from.
var directories := ["res://"]
## If true, explore each directory recursively
var is_recursive: = true
## A list of patterns to filter files.
var patterns := ["*.gd"]


func _init() -> void:
	var files := PackedStringArray()
	for dirpath in directories:
		files.append_array(Collector.find_files(dirpath, patterns, is_recursive))
	var json: String = Collector.print_pretty_json(Collector.get_reference(files))
	Collector.save_text("res://reference.json", json)
