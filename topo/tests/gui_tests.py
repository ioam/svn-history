"""
Functional GUI tests: run_basic() and run_detailed().

$Id$
"""
__version__='$Revision$'

import topo
assert hasattr(topo,'guimain'), "GUI must be running."

import traceback,sys,inspect
from numpy import array
from numpy.testing import assert_array_equal



# typing shortcut
g = topo.guimain

def run_basic():
    """Check that the windows all open ok (i.e. is GUI functioning?)."""
    print "\nRunning basic GUI tests...\n" 
    _initialize()

    s = 'Simulation'
    p = 'Plots'
    
    menu_paths = [ (s,'Test Pattern'),
                   (s,'Command prompt'),
                   (s,'Model Editor'),
                   (p,'Activity'),
                   (p,'Connection Fields'),
                   (p,'Projection'),
                   (p,'Projection Activity'),
                   (p,'Preference Maps','Orientation Preference'),
                   (p,'Tuning Curves','Orientation Tuning') ]
    
    return _run([_menu_item_fn(*x) for x in menu_paths])



def run_detailed():
    """Test that more complex GUI actions are working."""
    print "\nRunning detailed GUI tests...\n"
    _initialize()
    tests = [test_cf_coords,test_test_pattern] # and so on...
    return _run(tests)



######################################################################
# DETAILED TESTS
######################################################################

def test_cf_coords():
    """Check that ConnectionFields window opens with specified coords."""
    cf = g['Plots']['Connection Fields'](x=0.125,y=0.250)
    assert cf.x==0.125
    assert cf.y==0.250
    

def test_test_pattern():
    """Check that test pattern window is working."""
    tp = g['Simulation']['Test Pattern']()
    act = g['Plots']['Activity']()

    
    tp.gui_set_param('pattern_generator','TwoRectangles')
    from topo.patterns.basic import TwoRectangles
    assert isinstance(tp.pattern_generator,TwoRectangles), "Pattern generator did not change."


    preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    two_rectangles = array([[0.,1],[1.,0.]])
    assert_array_equal(preview,two_rectangles,"Incorrect pattern in preview plot.")


    tp.Present()
    gs_view = act.plotgroup.plots[0].view_dict['Activity']
    assert gs_view.src_name=='GS'
    gs_plot_array = gs_view.view()[0]
    assert_array_equal(gs_plot_array,two_rectangles,"Incorrect pattern in activity plot after Present.")


    tp.params_frame.gui_set_param('scale',0.5)
    preview = tp.plotgroup.plots[0].view_dict['Activity'].view()[0]
    assert_array_equal(preview,0.5*two_rectangles,"Changing pattern parameters did not update preview.")

    
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
    assert_array_equal(preview,initial_preview,"Defaults button failed to revert params to default values.")


    # CB: still need to test duration, learning, etc




######################################################################
# UTILITY FUNCTIONS
######################################################################

# make these particular tests simpler

def _initialize():
    """Make a simple simulation."""
    from topo.base.simulation import Simulation
    from topo.base.cf import CFSheet,CFProjection
    from topo.sheets.generatorsheet import GeneratorSheet

    sim=Simulation(register=True,name="test pattern tester")
    sim['GS']=GeneratorSheet(nominal_density=2)
    sim['S'] = CFSheet(nominal_density=2)
    sim.connect('GS','S',connection_type=CFProjection,delay=0.05)
    global g
    g=topo.guimain


def _menu_item_fn(*clicks):
    """Return a wrapper round topo.guimain[click1][click2]...[clickN], with __doc__ set
    to the menu path."""
    menu_path = 'topo.guimain'

    for click in clicks:
        menu_path+='["%s"]'%click

    menu_item = eval(menu_path)

    def test_menu_item():
        menu_item()

    test_menu_item.__doc__ = "%s"%menu_path[12::]

    return test_menu_item




######################################################################
# TEST FRAMEWORK FUNCTIONS
######################################################################

# could be used to call any set of functions

def _run(tests):
    """
    Call all test functions in tests and print the test outcomes.
    """
    errs = {}
    for test in tests:
        test_info = "%s (%s)"%(test.__name__,inspect.getdoc(test))
        error = _run_test(test) 
        if error is None:
            print "PASS: %s"%test_info
        else:
            print "FAIL: %s"%test_info
            errs[(test.__name__,test.__doc__)]=error

    for t,e in errs.items(): print "\n** Error from %s (%s):\n%s\n"%(t[0],t[1],e) 
    print "\nNumber of tests: %s"%len(tests)
    print "Number of errors: %s\n"%len(errs)
    return len(errs)


def _run_test(test):
    """Call test and return None on success, or the exception string on failure."""
    try:
        test()
        return None
    except:
        return traceback.format_exc()
        
