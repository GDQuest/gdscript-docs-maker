# Changelog #

This document lists new features, improvements, changes, and bug fixes in every GDScript docs maker release.

## GDScript Docs Maker 1.3.0 ##

### Features ###

- Create an **index page** with a table of contents. To do so, use the new
  command-line option `--make-index`. This generates an extra `index.md` file.
- You can now **link between classes**, including to specific methods and
  properties:
    - Write `[ClassName]`, `[ClassName.symbol]`, or `[symbol_in_this_class]` and
    docs maker will replace it with a link to the corresponding page and
    heading.
- Add support for the **class category**` metadata: this allows you to group
  classes by categories. Add a line with `# category: My Category` in your
  class's docstring to register a category for it.
- Classes now show all ancestors they extend, and the extends list links to
  the reference of parent classes.
- Store and write key project information: name, description, and human-readable
  version string.
    - We get them from the Application Settings in your Godot project.
    - For the project version, in 3.2.0, you need to add it yourself as
      `application/config/version. It must be with the form "1.0.0". Future or
      more recent Godot versions should have this defined by default. Upon
      exporting your game, Godot should also use this version number.

### Improvements ###

- The Windows `generate_reference.bat` command-line script now supports
  command-line flags and arguments. The script also now checks for and prevents
  common errors.
- Remove `extends` line if the class doesn't extend any type.
- Remove properties summary and methods summary if the class respectively
  doesn't have public properties or methods.

### Changes ###

- Changed the default export directory to "export", as we use "dist" to build
  the program's pip package itself.

## GDScript Docs Maker 1.2.1 ##

### Changes ###

- Move the pip package's configuration to `setup.cfg`.
    - The setup now automatically finds packages and data.
    - This improves type checks and imports with mypy.

### Bug fixes ###

- The tool now outputs regular markdown code blocks instead of hugo shortcodes by default.
- The `Collector.gd` script you can run from Godot's editor now rebuilds the language server cache so you don't need to restart Godot to rebuild the JSON class data.
- Fixed an error in markdown conversion when the Godot Language Server generates empty classes in the generated JSON file.
    - If a class doesn't have a name, docs maker will now skip it.

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

