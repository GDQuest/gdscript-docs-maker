# Collect the reference from the Godot editor #

Godot, since version 3.2, has a tool to create a class reference from GDScript code, through its language server.

This folder contains a tool script, `ReferenceCollector.gd`, to run directly from within your Godot projects and get the class reference as JSON using File->Run in the script editor.

You can find more detailed instructions inside the GDScript code itself.

## CLI version ##

An alternative to running the EditorScript is to use a command-line version of the tool found in the root of the repository. It requires `godot` to be in the PATH environment variable.

- **Windows**

```batch
windows.bat path/to/project project-name
```

`project-name` is optional - it will default to "project", and is the folder the distribution will be output into.

This script will copy the collector CLI script, run godot and quit, run the python module, and output the results into `project-name`.
