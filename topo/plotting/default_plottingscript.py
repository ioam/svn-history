from topo.commands.analysis import *
#from topo.plotting.plotfilesaver import PlotFileSaver
import os, topo, __main__

os.chdir(__main__.__dict__["output_directory"]+topo.sim.name)
save_plotgroup("Orientation Preference");
save_plotgroup("Projection",projection_name="LGNOnAfferent",sheet_name="V1");
#save_plotgroup("Projection",projection_name="V1Afferent",sheet_name="V2");
os.chdir('../../')