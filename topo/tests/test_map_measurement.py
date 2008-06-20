"""
Functions to test that map measurements haven't changed.

Use generate() to save data, and test() to check that the data is
unchanged in a later version. Results from generate() are already
checked into svn, so intentional changes to map measurement mean new
data must be generated and committed. E.g.

# ...deliberate change to orientation map measurement...
$ ./topographica -c 'default_density=8' examples/lissom_oo_or.ty -c \
  'topo.sim.run(100)' -c \
  'from topo.tests.test_map_measurement import *' -c \
  'generate(["Orientation Preference"])'
# now commit the resulting data file to the svn repository


plotgroups_to_test is a list of PlotGroups for which these
test functions are expected to be useful.
"""

import pickle
from numpy.testing import assert_array_almost_equal
from topo.misc.filepaths import resolve_path, normalize_path

from topo.commands.analysis import *
from topo.plotting.plotgroup import plotgroups

# CEBALERT: change to be the all-in-one model eventually, and
# uncomment all ocular/disparity/direction groups below.
sim_name = 'lissom_oo_or'

# For or tuning (and possibly others)
topo.commands.analysis.sheet_name = 'V1'

plotgroups_to_test = [
    # Several plotgroups are commented out because I was only thinking
    # about map measurement that results in sheet_views stored for V1.
    # (All could be included if the functions below were to be
    # extended to handle curve_dicts, sheets other than V1, etc.)
    #'Activity',
    #'Connection Fields',
    #'Projection',
    #'Projection Activity',
    #'RF Projection',
    #'RF Projection (noise)',

    'Position Preference',
    # 'Center of Gravity',
    # 'Orientation and Ocular Preference',
    # 'Orientation and Direction Preference',
    # 'Orientation, Ocular and Direction Preference',
    'Orientation Preference',
    #'Ocular Preference',
    'Spatial Frequency Preference',
    #'PhaseDisparity Preference',
    #'Orientation Tuning Fullfield',
    #'Orientation Tuning',
    #'Size Tuning',
    #'Contrast Response',
    #'Direction Preference',

    # commented out because it currently relies on pylabplots (see
    # ALERT in topo.commands.analysis)
    #'Corner OR Preference'
    ]


def generate(plotgroup_names):
    assert topo.sim.name==sim_name
    assert topo.sim['V1'].nominal_density==8
    assert topo.sim.time()==100

    for name in plotgroup_names:
        print "* Generating data for plotgroups['%s']"%name
        topo.sim['V1'].sheet_views = {}
        exec plotgroups[name].update_command

        if topo.sim['V1'].sheet_views=={}:
            print "## WARNING: no sheet view in V1" # i.e. this test needs to support a different sheet, curve_views, or something else...or the command didn't store a sheet_view (an error in the command).
        else:
            f = open(normalize_path('topo/tests/%s_t%s_%s.data'%(sim_name,topo.sim.timestr(),
                                                             name.replace(' ','_'))),'wb')
            pickle.dump((topo.version,topo.sim['V1'].sheet_views),f)
            f.close()
    

def test(plotgroup_names):
    assert topo.sim.name==sim_name
    assert topo.sim['V1'].nominal_density==8
    assert topo.sim.time()==100
    
    for name in plotgroup_names:
        print "\n* Testing plotgroups['%s']:"%name
        topo.sim['V1'].sheet_views = {}
        exec plotgroups[name].update_command

        f = open(resolve_path('topo/tests/%s_t%s_%s.data'%(sim_name,topo.sim.timestr(),
                                                            name.replace(' ','_'))),'r')
        topo_version,previous_sheet_views = pickle.load(f)
        f.close()

        for view_name in previous_sheet_views:
            assert_array_almost_equal(topo.sim['V1'].sheet_views[view_name].view()[0],
                                      previous_sheet_views[view_name].view()[0],
                                      12)
            print '...'+view_name+' array is unchanged since data was generated (%s)'%topo_version
    

