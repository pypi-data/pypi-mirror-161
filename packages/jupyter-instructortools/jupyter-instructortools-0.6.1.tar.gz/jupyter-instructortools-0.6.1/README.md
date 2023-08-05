## jupyter-instructortools
[Introduction](#introduction) | [Current Menu Items](#current-menu-items) | 
[Typical workflow](#typical-workflow) | [Installation](#installation) | 
[Change log](#change-log) | [Issues or Comments](#issues-or-comments) | 
[License](#this-software-is-distributed-under-the-gnu-v3-licensehttpsgnuorglicenses)
### Introduction
This adds a menu to Jupyter that automates some useful tasks an
instructor might want to do while building a notebook template for an 
assignment. This is part of the
[Jupyter Physical Science Lab project](https://jupyterphysscilab.github.io/Documentation/).

#### Current Menu Items:
The menu is activated by the python command `import InstructorTools`.
* Create a data input table.
    * Table column and row labels can be locked once set.
    * Number of rows and columns must be chosen on initial creation.
    * Table will survive deletion of all cell output data.
    * Default setting is to make the code cell that creates the table
      protected.
    * Table creation code will work without this package installed in the
      Jupyter kernel. Tables are viewable, but not editable in a plain vanilla
      Jupyter install.
    * This uses the `jupyter-datainputtable` package.
* Add some highlight bars to a selected markdown cell. These can be removed by 
  deleting the associated`<div>`:
  * A vertical cyan bracket at the left of the cell.
  * A vertical red bracket at the left of the cell.
  * A horizontal green start bar (fading down to yellow). Useful for indicating
    the beginning of an instruction block.
  * A horizontal brown stop bar (fading down from yellow to brown). Useful 
    for indicating the end of an instruction block.
* Protect/unprotect selected cells. Protected cells cannot be 
  edited or deleted by the user. This is a good way to prevent instructions
  and example code from being damaged by students.
* Set/un-set selected cells as allowed to be hidden. This can be used to mark
  cells to hide before producing a pdf to turn in.
* Set/un-set selected cells to hide code before printing.
* Set/un-set selected cells to hide code in JPSL.
* Temporarily highlight each kind of "hidden/hide" cell.
* Delete instructor tools from a notebook before making the
  worksheet available.
* Delete instructor tools and prevent reinstallation in the
  notebook.
* Insert code to automatically timestamp the notebook and 
  collect names from students. The code is inserted at the end of the 
  currently selected cell. The cell becomes protected
  against editing and deletion. This is a good cell to include initialization
  imports in.
* Insert a markdown cell with boilerplate instructions on initializing a
  notebook. This cell will be inserted below the selected cell. Insert this 
  immediately above the initialization and timestamping cell. Then edit to 
  meet your needs.
  
#### Typical workflow
Work in a virtual environment that includes this tool plus all the tools
the students will have access to. This is probably best done using the 
[JPSLInstructor pseudo package](https://github.com/JupyterPhysSciLab/JPSLInstructor).
If you want to do this in pieces see [Installation](#installation)
for information on setting up a virtual environment and installing just 
this package.

1. Start the jupyter notebook server (from the command line `jupyter 
   notebook`).
2. Open a new notebook and type `import InstructorTools` into the first 
   cell. Run the cell.
3. Build the exercise including instructions, examples, tables (use the menu) 
   and imports.
4. Collect all the necessary imports into a code cell that will be the 
   first code cell in the worksheet. You may want introductory material 
   before this cell.
5. Use the menu to add to this initialization cell the command to get the 
   student names and timestamp the notebook. This will simultaneously 
   protect the cell.
6. Use the menu to protect any cells you do not want students to 
   accidentally alter.
7. Use the menu to tag cells so they can be hidden. This allows students to 
   print a compressed version of the notebook for grading. Consider hiding 
   most of the instructions.
8. Restart the kernel and clear all cell outputs. Delete or emtpy any cells 
   that have things you want the students to be filling in.
9. Save the notebook and make a duplicate of it. Continue working with the 
   duplicate.
10. Work through the notebook as if you were a student, make adjustments as 
    you go. Iterate restarting the kernel, clearing the cell outputs, saving,
    duplicating and working though until satisfied.
11. Save the final version of the worksheet. Duplicate it.
12. Open the duplicate worksheet. Make sure all the appropriate cell data is 
    cleared. Then select `!deactivate permanently!` from the Instructor Tools
    menu. This will deactivate the menu and block students from easily 
    reinstalling it. Save the notebook and distribute this copy to students.
   
### Installation
#### _Production_
__Option 1__: Recommended as this will install all of the Jupyter Physical 
Science Lab packages an Instructor needs. Use the
[JPSLInstructor pseudo package](https://github.com/JupyterPhysSciLab/JPSLInstructor).

__Option 2__: Installing just this package and its requirements.

Installation using pip into a virtual environment is recommended.
1. If not installed, install pipenv:` pip3 install --user pipenv`. You may
need to add `~/.local/bin` to your `PATH` to make `pipenv`
available in your command shell. More discussion: 
[The Hitchhiker's Guide to Python](https://docs.python-guide.org/dev/virtualenvs/).
1. Navigate to the directory where this package will be installed.
1. Start a shell in the environment ` pipenv shell`.
1. Install using pip.
    1. ` pip install jupyter-instructortools`. This will install Jupyter into the same virtual
    environment if you do not already have it on your machine. If Jupyter is already
    installed the virtual environment will use the existing installation. This takes
    a long time on a Raspberry Pi. It will not run on a 3B+ without at least 1 GB of
    swap. See: [Build Jupyter on a Pi](https://www.uwosh.edu/facstaff/gutow/computer-and-programming-how-tos/installing-jupyter-on-raspberrian).
    1. Still within the environment shell test this by starting jupyter
` jupyter notebook`. Jupyter should launch in your browser.
        1. Open a new notebook using the default (Python 3) kernel.
        1. In the first cell import the InstructorTools module:
            `import InstructorTools`
        1. The `InstructorTools` menu should be added to the Jupyter menu bar.
1. _Optional_ You can make this environment available to an alternate Jupyter install as a special kernel when you are the user.
    1. Make sure you are running in your virtual environment ` pipenv shell` in the directory for  virtual
    environment will do that.
    1. Issue the command to add this as a kernel to your personal space: 
    ` python -m ipykernel install --user --name=<name-you-want-for-kernel>`.
    1. More information is available in the Jupyter/Ipython documentation. A simple tutorial from Nikolai Jankiev
    (_Parametric Thoughts_) can be found [here](https://janakiev.com/til/jupyter-virtual-envs/). 
 
 __Option 3__: for use in only one account on a Jupyterhub (Instructor only).
 
 Installation as a folder in the account home directory is recommended.
 
 1. Download the latest version .tar.gz [from PyPi](https://pypi.org/project/jupyter-instructortools/#files) 
 or a .gz [from github](https://github.com/JupyterPhysSciLab/jupyter-instructortools).
 1. Transfer this compressed file to the home directory of the account it will 
 be used in.
 1. Open a terminal and decompress the archive.
 1. Move the folder from the decompressed archive titled "InstructorTools" to
 the home directory of the account. The tools should now be available for
 import into any notebook run in this account.
 
#### _Development_
Simply replace ` pip install jupyter-instructortools` with
` pip install -e ../jupyter-instructortools` in the _Production_ instructions.

### Change Log
  * 0.6.1
    * Updates to requirements to utilize upstream bug fixes.
  * 0.6.0
    * Converted to hierarchical menu that appears in the menu bar rather 
      than the toolbar.
  * 0.5.6.2
    * Simplified styling of highlight bars to reduce chances of markdown 
      cell sanitization making them not show up.
    * Converted highlights to look more like brackets.
    * Added option for a red left bracket highlight.
    * require notebook version >= 6.4.10 for security fix.
  * 0.5.6.1 require notebook version >=6.4.7 for html styling and security 
    fixes.
  * 0.5.6
    * Expanded highlight bar options to insert in markdown cells to: 
      horizontal green start; horizontal brown stop; left vertical 
      chrome-blue highlight (only works well in Chrome browser).
    * Pin the notebook version to 6.4.0 because 6.4.1+ has started 
      stripping all html styling from markdown cells.
  * 0.5.5
    * Added option to flag cells as hide_code_on_print.
    * Added option to flag cells as hide_code (auto-hidden in
    JPSL).
    * Added ability to highlight these cells.
  * 0.5.4 Minor bug fixes and interface tweaks.
  * 0.5.3 
    * Added options to flag cells as allowed to be hidden.
    * Added ability to test hide/show of cells.
    * Added ability to place light blue highlight bar at left of markdown 
      cells.
    * README updates.
  * 0.5.2 Better messages and Readme updates.
  * 0.5.1
    * Added permanently deactivate menu option.
    * Added get names and timestamp option.
    * Added insert boilerplate about initializing notebook option.
    * Began using
      [JPSLUtils](https://github.com/JupyterPhysSciLab/JPSLUtils)
      for tools used across JupyterPhysSciLab.
    * Updated README, included suggested workflow, license and more details.
  * 0.5.0 Initial release.
### Issues or comments

Issues or bugs should be reported via the project's [issues pages](https://github.com/JupyterPhysSciLab/jupyter-instructortools/issues).


##### [This software is distributed under the GNU V3 license](https://gnu.org/licenses)
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

Copyright - Jonathan Gutow, 2020, 2021.