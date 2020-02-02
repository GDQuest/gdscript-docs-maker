# Changelog #

This document lists new features, improvements, changes, and bug fixes in every GDScript docs maker release.

## GDScript Docs Maker 1.0 ##

This is the initial release of the program. It can collect and generate a code reference from your Godot GDScript projects.

⚠ This release is a Work in Progress. Even if we're careful, new features can have bugs 🐛

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

