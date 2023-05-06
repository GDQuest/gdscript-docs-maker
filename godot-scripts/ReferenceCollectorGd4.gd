## Finds and generates a code reference from gdscript files.
##
## To use this tool:
##
## - Place this script and Collector.gd in your Godot project folder.
## - Open the script in the script editor.
## - Modify the properties below to control the tool's behavior.
## - Go to File -> Run to run the script in the editor.
@tool
extends EditorScript
class_name ReferenceCollector


var Collector: SceneTree = load("CollectorGd4.gd").new()
## A list of directories to collect files from.
var directories := ["res://src"]
## If true, explore each directory recursively
var is_recursive: = true
## A list of patterns to filter files.
var patterns := ["*.gd"]
## Output path to save the class reference.
var save_path := "res://reference.json"


func _run() -> void:
	var files := PackedStringArray()
	for dirpath in directories:
		files.append_array(Collector.find_files(dirpath, patterns, is_recursive))
	var json: String = Collector.print_pretty_json(Collector.get_reference(files))
	Collector.save_text(save_path, json)
