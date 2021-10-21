# Finds and generates a code reference from gdscript files.
tool
extends SceneTree

var warnings_regex := RegEx.new()


func _init() -> void:
	var pattern := "^\\s?(warning-ignore(-all|):\\w+|warnings-disable)\\s*$"
	var error := warnings_regex.compile(pattern)
	if error != OK:
		printerr("Failed to compile '%s' to a regex pattern." % pattern)


# Returns a list of file paths found in the directory.
#
# **Arguments**
#
# - dirpath: path to the directory from which to search files.
# - patterns: an array of string match patterns, where "*" matches zero or more
#   arbitrary characters and "?" matches any single character except a period
#   ("."). You can use it to find files by extensions. To find only GDScript
#   files, ["*.gd"]
# - is_recursive: if `true`, walks over subdirectories recursively, returning all
#   files in the tree.
func find_files(
	dirpath := "", patterns := PoolStringArray(), is_recursive := false, do_skip_hidden := true
) -> PoolStringArray:
	var file_paths := PoolStringArray()
	var directory := Directory.new()

	if not directory.dir_exists(dirpath):
		printerr("The directory does not exist: %s" % dirpath)
		return file_paths
	if not directory.open(dirpath) == OK:
		printerr("Could not open the following dirpath: %s" % dirpath)
		return file_paths

	directory.list_dir_begin(true, do_skip_hidden)
	var file_name := directory.get_next()
	var subdirectories := PoolStringArray()
	while file_name != "":
		if directory.current_is_dir() and is_recursive:
			var subdirectory := dirpath.plus_file(file_name)
			file_paths.append_array(find_files(subdirectory, patterns, is_recursive))
		else:
			for pattern in patterns:
				if file_name.match(pattern):
					file_paths.append(dirpath.plus_file(file_name))
		file_name = directory.get_next()

	directory.list_dir_end()
	return file_paths


# Saves text to a file.
func save_text(path := "", content := "") -> void:
	var dirpath := path.get_base_dir()
	var basename := path.get_file()
	if not dirpath:
		printerr("Couldn't save: the path %s is invalid." % path)
		return
	if not basename.is_valid_filename():
		printerr("Couldn't save: the file name, %s, contains invalid characters." % basename)
		return

	var directory := Directory.new()
	if not directory.dir_exists(dirpath):
		directory.make_dir(dirpath)

	var file := File.new()

	file.open(path, File.WRITE)
	file.store_string(content)
	file.close()
	print("Saved data to %s" % path)


# Parses a list of GDScript files and returns a list of dictionaries with the
# code reference data.
#
# If `refresh_cache` is true, will refresh Godot's cache and get fresh symbols.
func get_reference(files := PoolStringArray(), refresh_cache := false) -> Dictionary:
	var version := "n/a"
	if ProjectSettings.has_setting("application/config/version"):
		version = ProjectSettings.get_setting("application/config/version")  
	var data := {
		name = ProjectSettings.get_setting("application/config/name"),
		description = ProjectSettings.get_setting("application/config/description"),
		version = version,
		classes = []
	}
	var workspace = Engine.get_singleton('GDScriptLanguageProtocol').get_workspace()
	for file in files:
		if not file.ends_with(".gd"):
			continue
		if refresh_cache:
			workspace.parse_local_script(file)
		var symbols: Dictionary = workspace.generate_script_api(file)
		if symbols.has("name") and symbols["name"] == "":
			symbols["name"] = file.get_file()
		remove_warning_comments(symbols)
		data["classes"].append(symbols)
	return data


# Directly removes 'warning-ignore', 'warning-ignore-all', and 'warning-disable'
# comments from all symbols in the `symbols` dictionary passed to the function.
func remove_warning_comments(symbols: Dictionary) -> void:
	symbols["description"] = remove_warnings_from_description(symbols["description"])
	for meta in ["constants", "members", "signals", "methods", "static_functions"]:
		for metadata in symbols[meta]:
			metadata["description"] = remove_warnings_from_description(metadata["description"])
	
	for sub_class in symbols["sub_classes"]:
		remove_warning_comments(sub_class)


func remove_warnings_from_description(description: String) -> String:
	var lines := description.strip_edges().split("\n")
	var clean_lines := PoolStringArray()
	for line in lines:
		if not warnings_regex.search(line):
			clean_lines.append(line)
	return clean_lines.join("\n")


func print_pretty_json(reference: Dictionary) -> String:
	return JSON.print(reference, "  ")
