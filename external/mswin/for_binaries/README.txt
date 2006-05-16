Making a Windows installation package
=====================================

(1) First you need to be using a copy that has been setup to
    work under CVS. This means you have run setup.bat in the
    Topographica root directory and can use Topographica.

(2) Run 'prepare_for_binaries.bat'
    - creates setup subdirectory in root topographica directory
    - deletes setup.bat from root topographica directory
    - copies this directory's setup.bat to setup/ subdirectory
    - cleans files that aren't needed for the binary version

(3) I use 'Inno Setup 5', an open-source installation package creator.
    (See http://www.jrsoftware.org/isinfo.php)
    The script topographica.iss will create a .exe installation file.