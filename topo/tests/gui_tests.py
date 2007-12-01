"""
GUI tests: run_basic() and run_detailed().

$Id$
"""
__version__='$Revision$'

import topo
assert hasattr(topo,'guimain'), "GUI must be running."

# typing shortcut
g = topo.guimain


from numpy import array
from numpy.testing import assert_array_equal



def run_basic():
    """
    Check that the windows all open ok (i.e. is GUI functioning?).
    """
    initialize()
    g['Simulation']['Test Pattern']()
    g['Simulation']['Command prompt']()
    p=g['Plots']
    p['Activity']()
    p['Connection Fields']()
    p['Projection']()
    p['Projection Activity']()
    p['Preference Maps']['Orientation Preference']()
    p['Tuning Curves']['Orientation Tuning']()
    e=g['Simulation']['Model Editor']()
    # model editor not yet TkPO
    [X.show_properties() for X in e.canvas.object_list]


def run_detailed():
    """
    Test that more complex GUI actions are working.
    """
    initialize()
    test_cf_coords()
    test_test_pattern()
    # and so on...


    
######################################################################
# UTILITY FUNCTIONS
######################################################################

def initialize():
    """
    Make a simple simulation
    """
    from topo.base.simulation import Simulation
    from topo.base.cf import CFSheet,CFProjection
    from topo.sheets.generatorsheet import GeneratorSheet

    sim=Simulation(register=True,name="test pattern tester")
    sim['GS']=GeneratorSheet(nominal_density=2)
    sim['S'] = CFSheet(nominal_density=2)
    sim.connect('GS','S',connection_type=CFProjection,delay=0.05)
    global g
    g=topo.guimain




######################################################################
# DETAILED TESTS
######################################################################

def test_cf_coords():
    """
    Check that ConnectionFields window opens with specified coords.
    """
    cf = g['Plots']['Connection Fields'](x=0.125,y=0.250)
    assert cf.x==0.125
    assert cf.y==0.250
    

def test_test_pattern():
    """
    Check that test pattern window is working.
    """
    tp = g['Simulation']['Test Pattern']()
    act = g['Plots']['Activity']()

    
    ### Change pattern generator
    tp.gui_set_param('pattern_generator','TwoRectangles')
    from topo.patterns.basic import TwoRectangles
    assert isinstance(tp.pattern_generator,TwoRectangles)


    ### Check pattern in preview window
    preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    two_rectangles = array([[0.,1],[1.,0.]])
    assert_array_equal(preview,two_rectangles)


    ### Check pattern in activity window
    tp.Present()
    gs_view = act.plotgroup.plots[0].view_dict['Activity']
    assert gs_view.src_name=='GS'
    gs_plot_array = gs_view.view()[0]
    assert_array_equal(gs_plot_array,two_rectangles)


    ### Change some pattern parameters
    tp.params_frame.gui_set_param('scale',0.5)
    preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    assert_array_equal(preview,0.5*two_rectangles)

    
    ### Defaults button

    # first change several more parameters
    initial_preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    
    new_param_values = [('output_fn','Sigmoid'),
                        ('orientation','pi/4')]

    for name,value in new_param_values:
        tp.params_frame.gui_set_param(name,value)

    changed_preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    
    # and check the preview did change
    try:
        assert_array_equal(changed_preview,initial_preview)
    except AssertionError:
        pass
    else:
        raise AssertionError("Test pattern didn't change.")
    
    # test that preview display is correct
    tp.params_frame.Defaults()
    preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    assert_array_equal(preview,initial_preview)


    # CB: still need to test duration, learning, etc



