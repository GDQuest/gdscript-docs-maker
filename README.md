# GDScript Docs Maker #

Docs Maker is a command-line program that parses your Godot GDScript code and outputs a code reference or documentation as JSON.

The program is still a work-in-progress.

## Getting started ##

Call the `gdscript-docs-maker` package directly using the `python -m` option:

```
python -m gdscript-docs-maker files [files ...]
```

The program takes a list of GDScript files to parse. For example, we generate the code reference of our AI framework [Godot Steering Toolkit]() like so with the fish shell:

```fish
python -m gdscript-docs-maker ~/Repositories/godot-steering-toolkit/project/src/**.gd
```

With bash:

```bash
python -m gdscript-docs-maker `find ~/Repositories/godot-steering-toolkit -iname '*.gd'`
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
