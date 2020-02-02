@echo off
:: Usage: windows.bat path\to\project [project-name]
:: Project name is optional - will default to "project"
:: The project location must contain a project.godot file

:: Configuration: Modify ReferenceCollectorCLI.gd with paths relative to the project's res://

where /q godot*
if ERRORLEVEL 1 (
	ECHO "Godot is missing from the PATH environment."
	EXIT /B
)

where /q python*
IF ERRORLEVEL 1 (
	ECHO "Python is missing from the PATH environment."
	EXIT /B
)

for /f "delims=" %%F in ('where godot*') do set godot=%%F

set project_path=%1

IF NOT EXIST "%project_path%\project.godot" (
	echo Could not find a project.godot in %project_path%. This program needs a Godot project to work.
	EXIT /B
)

IF [%2] == [] (
	set project_name=project
) else (
	set project_name=%2
)

IF NOT EXIST "%project_name%" (
	:: Creates the directory with project name.
	mkdir "%project_name%"
)

set gdscript_path=godot-scripts
set gdscript_1=ReferenceCollectorCLI.gd
set gdscript_2=Collector.gd

:: Copies the CLI gdscript to the project location so godot can find it in res://
copy /Y "%gdscript_path%\%gdscript_1%" "%project_path%\ReferenceCollectorCLI.gd" >nul
copy /Y "%gdscript_path%\%gdscript_2%" "%project_path%\Collector.gd" >nul

echo Generating reference...
:: Runs godot in editor mode, runs the script ReferenceCollectorCLI, and quits
%godot% -e -q -s --no-window --path "%project_path%" ReferenceCollectorCLI.gd >nul

:: Removes the CLI tool from the project.
erase /Q "%project_path%\ReferenceCollectorCLI.gd"
erase /Q "%project_path%\Collector.gd"

IF NOT EXIST "%project_path%\reference.json" (
	echo There was an error generating the reference from godot.
	EXIT /B
) else (
	echo Done.
)

:: Empty current version of dist if it exists
if EXIST dist (
	erase /Q dist
)

echo Generating markdown files in %project_name%
:: Runs the markdown creator.
:: TODO: Skip the moving by having the python script output dist into the project folder
python -m gdscript-docs-maker "%project_path%/reference.json"

IF NOT EXIST dist (
	goto :PythonError
) else (
	for /F %%i in ('dir /b "dist\*.*"') do (
		goto :Success
	)
	
	:PythonError
	echo Python module failed to create markdown distribution
	EXIT /B
)

:Success
IF EXIST "%project_name%" (
	:: Move all files in dist into project name dist
	erase /Q "%project_name%"
	move /Y dist\* "%project_name%" >nul
	rmdir /q /s dist
) ELSE (
	:: Puts the resulting distribution result into the project folder.
	move /Y dist "%project_name%"
)