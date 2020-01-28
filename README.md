# GDScript Docs Maker #

Docs Maker is a set of tools to parse Godot GDScript code, output a code
reference or documentation as JSON, merge json files together, and convert the
JSON data to markdown.

The program is still a work-in-progress.

## Generating a code reference as JSON ##

To generate code references, we rely on the GDScript language server in Godot 3.2+. This involves running an EditorScript from your Godot project.

For more information and detailed instructions, see [/godot-scripts](./godot-scripts).

## Converting JSON ##

Call the `gdscript-docs-maker` package directly using the `python -m` option:

```
python -m gdscript-docs-maker files [files ...]
```

The program takes a list of JSON files. For example, we generate the code reference of our AI framework [Godot Steering Toolkit](https://github.com/GDQuest/godot-steering-toolkit/) like so with the shell:

```fish
python -m gdscript-docs-maker ~/Repositories/godot-steering-toolkit/src/reference.json
```

## Writing your code reference ##

We document properties and functions with comment blocks placed on the line before their definition:

```gdscript
class_name GSTTargetAcceleration
# A linear and angular amount of acceleration.


# Linear acceleration
var linear: = Vector3.ZERO
# Angular acceleration
var angular: = 0.0


# Resets the accelerations to zero
func reset() -> void:
	linear = Vector3.ZERO
	angular = 0.0
```

Your docstrings can be as long as you want.
