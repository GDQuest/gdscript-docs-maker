# Changelog #

This document lists new features, improvements, changes, and bug fixes in every GDScript docs maker release.

## GDScript Docs Maker 1.2.1 ##

### Changes ###

- Move the pip package's configuration to `setup.cfg`.

### Bug fixes ###

- The tool now outputs regular markdown code blocks instead of hugo shortcodes by default.
- The `Collector.gd` script you can run from Godot's editor now rebuilds the language server cache so you don't need to restart Godot to rebuild the JSON class data.


## GDScript Docs Maker 1.2 ##

*In development*

### Features ###

- Add code highlighting to the `hugo` output format.
- Add `--date` and `--author` command line flags for the hugo front matter output.
- Add support for the `abstract` tag, for abstract base classes.
- Add GDScript code highlighting for the hugo export format.
- Add support for enums.

### Improvements ###

- The documents now only have 1 empty line betweens paragraphs, headings, etc. instead of 2 to 4.

## GDScript Docs Maker 1.1 ##

### Features ###

- New output format for the static website engine [hugo](https://gohugo.io/) with toml front-matter. Use the `--format hugo` option to select it.
- New `--dry-run` command-line option to output debug information.

### Bug fixes ###

- Use code blocks for functions instead of inline code.

## GDScript Docs Maker 1.0 ##

This is the initial release of the program. It can collect and generate a code reference from your Godot GDScript projects.

### Features ###

- Parses and collects docstrings from GDScript files, using Godot 3.2's Language Server. Outputs the data as JSON.
- Converts the JSON data to markdown files.
    - Writes methods, static functions, signals, member variables, and class data.
    - Only writes relevant sections. For example, the tool only creates a "Method Descriptions" section if there are methods in the class.
    - Skips built-in callbacks, i.e. `_process`, `_input`, etc. 
    - Skips the constructor, `_init`, unless it has arguments.
    - Skips private functions and member variables, unless tagged as virtual.
- Supports tags in the source code with the `tags:` keyword followed by comma-separated strings, like `tags: virtual, deprecated`.
    - Currently, the program only takes `virtual` into account, but it does store all the tags.
- There are two shell scripts for POSIX shells (sh, bash, etc.) and Windows CMD, respectively. Use them to generate your code reference instantly.

