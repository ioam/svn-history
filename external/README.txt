Makefiles for external dependencies
-----------------------------------

In its original form, external was hosted in an SVN repository and contained source archives (typically tarballs) of external dependencies used by Topographica and its users. When migrating to GitHub, it was decided that hosting large numbers of binary files was not appropriate. For this reason, all versions of these binaries have been removed, hosted on Sourceforge and all historical Makefiles updated.

Every Makefiles in the history has had generic targets appended. These targets fetch the compressed source archives from Sourceforge (https://sourceforge.net/projects/topographica/files/external-full-history/) if the files do not already exist in the directory. This is the expected behaviour when using the Makefile after cloning Topographica from Github.

This approach assumes that all Makefiles in the history correctly list the necessary archive files listed as dependencies for all the desired make targets. If you encounter problems installing external dependencies from an old Makefile in the history, consider either fixing the broken targets or fetching the appropriate SVN revision of Topographica directly from Sourceforge.
