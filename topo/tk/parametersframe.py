"""
Container for manipulating a PropertiesFrame so that a Parameter can
be manipulated.  Written to remove code from inputparampanel.py with
the goal of eventually turning into a more general file.

$Id$
"""
import propertiesframe
import topo.base.registry
from Tkinter import Frame, TOP, LEFT, RIGHT, BOTTOM, YES, N,S,E,W,X
from topo.base.utils import eval_atof


class ParametersFrame(Frame):
    def __init__(self, parent=None,**config):
        self.parent = parent
        self.prop_frame = propertiesframe.PropertiesFrame(self.parent,string_translator=eval_atof)
        Frame.__init__(self,parent,config)
        self.tparams = {}
        self.default_values = self.prop_frame.get_values()

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


# How to access the list of non-hidden Parameters in a PatternGenerator object
#        # Test to find the params and names.
#        pgc = topo.base.registry.pattern_generators[kf_classname] 
#        pg = pgc()
#        plist = [(k,v)
#                 for (k,v)  # ('name':'...', 'density':10000, ...)
#                 in pg.get_paramobj_dict().items()
#                 if not v.hidden
#                 ]
#        print plist



    def add_slider(self,name,min,max,init):
        return self.prop_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.6f')

    def reset_to_defaults(self):
        self.prop_frame.set_values(self.default_values)


    def refresh(self):
        for entry in self.tparams.values():
            if entry[1].need_to_refresh_slider:
                entry[1].set_slider_from_tag()


    def refresh_sliders(self,new_name):
        """
        The visible TaggedSliders will be updated.  The old ones are
        removed, and new ones are added to the screen.  The widgets
        themselves do not change but the grid location does.
        """
        # How to wipe the widgets off the screen
        for (s,c) in self.tparams.values():
            s.grid_forget()
            c.grid_forget()
        # Make relevant parameters visible.
        new_sliders = self.relevant_parameters(new_name)
        for i in range(len(new_sliders)):
            (s,c) = self.tparams[new_sliders[i]]
            s.grid(row=i,column=0,padx=self.prop_frame.padding,
                   pady=self.prop_frame.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.prop_frame.padding,
                   pady=self.prop_frame.padding,
                   sticky=N+S+W+E)


    def relevant_parameters(self,kf_classname):
        """
        Pre:  kf_classname is the string name of a PatternGenerator subclass.
        Post: List of strings that is the Intersection of kf_classname's
              class member keys, and tparams.keys() entries.
        """

        kf_class_keylist = topo.base.registry.pattern_generators[kf_classname].__dict__.keys()
        rlist = [s for s in self.tparams.keys() if s in kf_class_keylist]

        return rlist





