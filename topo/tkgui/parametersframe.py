"""
ParametersFrame class.

$Id$
"""
__version__='$Revision $'

import propertiesframe
import topo.base.registry
from Tkinter import Frame, TOP, LEFT, RIGHT, BOTTOM, YES, N,S,E,W,X
from topo.base.utils import eval_atof
from copy import deepcopy

class ParametersFrame(Frame):
    """
    Property list frame for a PatternGenerator Parameter
    (originally intended to be general)
    
    Automatically generates a PropertiesFrame containing all the
    Parameters for the TopoObject.

    Currently limited to supporting PatternGenerator objects only.
    """

    ### JABHACKALERT!  Is not actually coded in a general way; needs
    ### massive rewriting to accept *any* TopoObject.  Nothing should
    ### assume anything about Patterns or PatternGenerators,
    ### everything mentioning sliders should be written for (and
    ### described as) being for widgets instead, and so on.
    
    def __init__(self, parent=None,**config):
        self.__prop_frame = propertiesframe.PropertiesFrame(parent,string_translator=eval_atof)
        Frame.__init__(self,parent,config)
        self.__tparams = {}
        self.__default_values = self.__prop_frame.get_values()
        self.__prop_frame.pack(side=TOP,expand=YES,fill=X)

    ### JABHACKALERT!  This should be made into part of a
    ### PatternGeneratorParameter widget.
    ### GeneratorSheet.input_generator would be declared as a
    ### PatternGeneratorParameter, and such a widget would allow the
    ### user to select a PatternGenerator from the known list.  The
    ### code for that should be done very generally, because we'll
    ### need to do something very similar for learning rules,
    ### activation functions, etc.  Even then, it should probably not
    ### be part of this class, because this class is for the
    ### parameters of one single TopoObject.  At the moment it has a
    ### selection box for choosing such an object, and also includes
    ### its parameters, which is a mess.
    def __pg_parameters(self,pg_classname):
        """
        Return the list of Parameter names and objects for the requested PatternGenerator name.
        """
        pgc = topo.base.registry.pattern_generators[pg_classname] 
        pg = pgc()
        plist = [(k,v)
                 for (k,v)  # ('name':'...', 'density':10000, ...)
                 in pg.get_paramobj_dict().items()
                 if not v.hidden
                 ]
        #print 'plist', plist
        return plist
    

    ### JABHACKALERT!  Needs to be extended to support non-slider
    ### parameters, making a slider only for Numbers, and other
    ### types of widget for other types of Parameter.  Numbers
    ### should work even if they don't have bounds, in which case
    ### they just get a non-slider widget.  *Any* parameter type
    ### should be allowed, using a default text entry expression
    ### widget in the most general case.
    def __make_sliders_from_params(self,params,slider_dict):
        """
        Make a new slider for each name/value in the params list.
        """
        for (k,v) in params:
            (low,high) = v.get_soft_bounds()
            default = v.default
            slider_dict[k] = self.__add_slider(k,str(low),str(high),str(default))
    

    def __add_slider(self,name,min,max,init):
        return self.__prop_frame.add_tagged_slider_property(name,init,
                 min_value=min,max_value=max,width=30,string_format='%.6f')

    def reset_to_defaults(self):
        self.__prop_frame.set_values(self.__default_values)


    def refresh(self):
        for entry in self.__tparams.values():
            if entry[1].need_to_refresh_slider:
                entry[1].set_slider_from_tag()


    def refresh_sliders(self,new_name):
        """
        The visible TaggedSliders will be updated.  The old ones are
        removed, and new ones are added to the screen.  The widgets
        themselves do not change but the grid location does.
        """
        # How to wipe the widgets off the screen
        for (s,c) in self.__tparams.values():
            s.grid_forget()
            c.grid_forget()
        # Make relevant parameters visible.
        new_param_names = self.__pg_parameters(new_name)
        self.__make_sliders_from_params(new_param_names,self.__tparams)
        new_sliders = dict(new_param_names).keys()
        new_sliders.sort()
        for i in range(len(new_sliders)):
            (s,c) = self.__tparams[new_sliders[i]]
            s.grid(row=i,column=0,padx=self.__prop_frame.padding,
                   pady=self.__prop_frame.padding,sticky=E)
            c.grid(row=i,
                   column=1,
                   padx=self.__prop_frame.padding,
                   pady=self.__prop_frame.padding,
                   sticky=N+S+W+E)


    ### JABHACKALERT!  What is this doing in this file?  It has no relevance
    ### to ParametersFrame, and is only useful for inputparamspanel, not other
    ### types of ParametersFrame!  Ideally it would move out of tk/ altogether,
    ### but back into inputparamspanel would at least make more sense.
    ###
    ### JAB: It is not clear how this will need to be extended to support
    ### objects with different parameters in the different eyes, e.g. to
    ### test ocular dominance.
    def create_patterns(self,pg_name,ep_dict):
        """
        Make an instantiation of the current user patterns.

        The new pattern generator will be placed in a passed in
        dictionary for the input sheet under the key 'pattern'.

        If the 'state' is turned off (from a button on the Frame),
        then do not change the currently stored generator.  This
        allows eyes to have different presentation patterns.
        """
        p = self.__prop_frame.get_values()
        # rp = self.relevant_parameters(pg_name)
        rp = dict(self.__pg_parameters(pg_name)).keys()
        ndict = {}
        ### JABHACKALERT!
        ###
        ### How will this work for photographs and other items that need non-numeric
        ### input boxes?  It *seems* to be assuming that everything is a float.
        for each in rp:
            ndict[each] = eval_atof(p[each])
        for each in ep_dict.keys():
            if ep_dict[each]['state']:
                ndict['density'] = ep_dict[each]['obj'].density
                ndict['bounds'] = deepcopy(ep_dict[each]['obj'].bounds)
                pg = topo.base.registry.pattern_generators[pg_name](**ndict)
                ep_dict[each]['pattern'] = pg
        return ep_dict  





