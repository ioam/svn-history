********************************************
Files for setting up Topographica on Windows
********************************************

Currently, Topographica can be used in two different ways on Windows.

The first is by building Topographica in the MSYS/MinGW environment.
For that, the topographica directory and a working MSYS/MinGW
environment are required. We provide a working MSYS/MinGW setup in the
msys/ subdirectory; apart from that subdirectory, nothing else in
topographica-win is needed to build topographica this way. Further
instructions are provided in the Topographica installation
instructions.

The second method of using Topographica on Windows is by installing
our binary setup .exe file. topographica-win contains the tools
necessary for Topographica developers to create this installer.


To create an .exe installer
===========================

Note: .bat scripts probably always assume they are running from their 
own directory; please make sure you double click on the .bat, or use 
cmd.exe to run the .bat from the directory in which it resides.

(1) If external packages (such as python or numpy) need to be updated,
follow the instructions in create_python_topo/README.txt

(2) Follow the instructions in setup_cvs_copy/README.txt

(3) Follow the instructions in create_installer/README.txt


