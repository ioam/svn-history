"""
Container for manipulating a PropertiesFrame so that a Parameter can
be manipulated.  Written to remove code from inputparampanel.py with
the goal of eventually turning into a more general file.

$Id$
"""
import propertiesframe
from Tkinter import Frame, TOP, LEFT, RIGHT, BOTTOM, YES, N,S,E,W,X
from topo.base.utils import eval_atof


class ParameterFrame(Frame):
    def __init__(self, parent=None,**config):
        self.parent = parent
        self.prop_frame = propertiesframe.PropertiesFrame(self.parent,string_translator=eval_atof)
        Frame.__init__(self,parent,config)
        self.tparams = {}

        ### JABHACKALERT!
        ###
        ### There can't be any list of valid parameters defined in
        ### this class; the user needs to be able to add any arbitrary
        ### parameter to a new PatternGenerator of his or her own design.
        ### So all the information below needs to be stored with the
        ### PatternGenerator or some lower-level entity, preferably as
        ### part of the Parameter definition.  Some of the values here
        ### are just hints, while others are absolute maximum or
        ### minimums, and the Parameter definition would need to
        ### distinguish between those two cases.
        
        #                name          min-value    max-value  init-value
        #
        self.tparams['theta'] = \
          self.add_slider( 'theta',         "0"       , "PI*2",  "0"      )
        self.tparams['x'] = \
          self.add_slider( 'x',             "-1"      , "1"   ,  "0"      )
        self.tparams['y'] = \
          self.add_slider( 'y',             "-1"      , "1"   , "0"       )
        self.tparams['min'] = \
          self.add_slider( 'min',           "0"       , "1"   , "0"       )
        self.tparams['max'] = \
          self.add_slider( 'max',           "0"       , "1"   , "1"       )
        self.tparams['width'] = \
          self.add_slider( 'width',         "0.000001", "1"   , "0.2"     )
        self.tparams['height'] = \
          self.add_slider( 'height',        "0.000001", "1"   , "0.2"     )
        self.tparams['frequency'] = \
          self.add_slider( 'frequency',     "0.01"    , "7"   ,  "5"      )
        self.tparams['phase'] = \
          self.add_slider( 'phase',         "0"       , "PI*2",  "PI/2"   )
        self.tparams['disk_radius'] = \
          self.add_slider( 'disk_radius',   "0"       , "1"   ,  "0.2"    )
        self.tparams['gaussian_width'] = \
          self.add_slider( 'gaussian_width',"0.000001", "1"   ,  "0.15"   )

        self.prop_frame.pack(side=TOP,expand=YES,fill=X)


    def add_slider(self,name,min,max,init):
        return self.prop_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.6f')


