@echo off
:: Usage: windows.bat path\to\project [project-name]
:: Project name is optional - will default to "project"
:: The project location must contain a project.godot file

:: Configuration: Modify ReferenceCollectorCLI.gd with paths relative to the project's res://

IF NOT EXIST "%1\project.godot" (
	echo Godot project not found at %~dp1project.godot
	EXIT /B -1	
)

IF [%2] == [] (
	set project_name=project
) else (
	set project_name=%2
)

IF NOT EXIST %project_name% (
	:: Creates the directory with project name.
	mkdir %project_name%
)

echo Copying collector
:: Copies the CLI gdscript to the project location so godot can find it in res://
copy /Y godot-scripts\ReferenceCollectorCLI.gd %1\ReferenceCollectorCLI.gd
copy /Y godot-scripts\Collector.gd %1\Collector.gd

echo Running godot
:: Runs godot in editor mode, runs the script ReferenceCollectorCLI, and quits
godot -e -q -s --no-window --path %1 ReferenceCollectorCLI.gd >nul

echo Cleaning up
:: Removes the CLI tool from the project.
erase /Q %1\ReferenceCollectorCLI.gd
erase /Q %1\Collector.gd

IF NOT EXIST %1\reference.json (
	echo Collector failed - Json reference file not created
	EXIT /B -1
)

echo Preparing for distribution
:: Moves the dumped json file.
move /Y %1\reference.json %project_name%\reference.json

:: Runs the markdown creator.
:: TODO: Skip the moving by having the python script output dist into the project folder
python -m gdscript-docs-maker %project_name%/reference.json

IF NOT EXIST dist (
	echo Python module failed to create markdown distribution
	EXIT /B -1
)

IF EXIST %project_name%\dist (
	:: Move all files in dist into project name dist
	erase /Q %project_name%\dist
	move /Y dist\* %project_name%\dist >nul
	rmdir /q /s dist
) ELSE (
	:: Puts the resulting distribution result into the project folder.
	move /Y dist %project_name%\dist
)

echo Done. Output now in %~dp0%project_name%\dist