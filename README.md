# mal-toolbox-gui
A graphical user interface tool used to create MAL instance models.

## Installation

Install the package from pypi by running `pip install mal-gui`.

## Run

If you have installed the package locally you can run the command `malgui` to run the GUI.

This will open up the graphical user interface.

If you for any reason don't want to install the package, you can run it as a module directly with `python -m mal_gui.app` from this directory.


## How to use the graphical interface

### Starting up

![Start popup](docs/select_lang.png "Select MAL/MAR archive.")

When you start up `malgui` you need to select a MAL-language.

Read the tutorial if you do not know how: https://github.com/mal-lang/mal-toolbox-tutorial.

### Add an asset
When you have started the application you can drag and drop new assets from the object explorer on the left.

### Create associations
To create associations you use SHIFT + Left click to drack and drop between two assets. This lets you select what association they should have.

![Overview of the MAL gui](docs/overview.png "Info on how to do things in malgui.")
