#!/usr/bin/env sh

project_directory=$1
output_directory=$2

echo_help() {
    echo "
Generate a code reference from GDScript
Usage:
generate_reference.sh $project_directory (optional)$output_directory

Arguments:

$project_directory -- path to your Godot project directory.
This directory or one of its subdirectories should contain a
project.godot file.

$output_directory -- directory path to output the documentation into.

Flags:

-h/--help -- Display this help message.
"
    exit 0
}

if [ $1 = "-h" ]
then echo_help
fi
if [ $1 = "--help" ]
then echo_help
fi
if [ $1 = "help" ]
then echo_help
fi

# Testing input parameters
if [ -z $project_directory ]
then echo Missing first parameter: project_directory
   exit 1
fi
if ! test -d $project_directory
then echo Directory $project_directory does not exist, exiting.
     exit 1
fi
godot_project_file=`find $project_directory -iname project.godot -print -quit`
if ! test -f $godot_project_file
then echo "Could not find a project.godot file in $target_directory. This program needs a Godot project to work."
     exit 1
fi
if [ -z $output_directory ]
then output_directory="dist"
fi

# Generate reference JSON data from Godot
godot_project_dir=`dirname $godot_project_file`
gdscript_1="godot-scripts/ReferenceCollectorCLI.gd"
gdscript_2="godot-scripts/Collector.gd"

cp -v $gdscript_1 $godot_project_dir
cp -v $gdscript_2 $godot_project_dir

echo Generating reference...
godot3.2 --editor --quit --script --no-window --path $godot_project_dir ReferenceCollectorCLI.gd > /dev/null
echo Done.
if ! test -f $godot_project_dir/reference.json
then echo There was an error generating the reference from Godot.
     exit 1
fi

rm -v $godot_project_dir/`basename $gdscript_1`
rm -v $godot_project_dir/`basename $gdscript_2`

# Generate markdown files
echo Generating markdown files in $output_directory
if ! test -d $output_directory; then mkdir -v $output_directory; fi
python3 -m gdscript_docs_maker $godot_project_dir/reference.json
