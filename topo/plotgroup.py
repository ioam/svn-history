"""

PlotGroups are containers of Plots that store specific information
about different plot types.  Specifically, a PlotGroup contains the
do_plot_cmd() function that knows how to generate plots.  All
information in these classes must be medium independent.  That is to
say, the bitmaps produced by the groups of plots should be as easily
displayed in a GUI window, as saved to a file.

$Id$
"""
from base import TopoObject
from plot import *
import topo.simulator
import topo
import MLab
from itertools import chain
from Numeric import transpose, array

# Shape of the plotting display used by PlotGroup.  NOTE: INCOMPLETE,
# THERE SHOULD BE MORE TYPES OF SHAPES SUCH AS SPECIFYING X ROWS, OR Y
# COLUMNS, OR GIVING A LIST OF INTEGERS REPRESENTING NUMBER OF PLOTS
# FOR EACH ROW.  Proposed format: If three columns are desired with
# the plots laid out from left to right, then use (None, 3).  If three
# rows are desired then (3, None).  Another method that would work is
# [3,2,4] would have the first row with 3, the second row with 2, the
# third row with 4, etc.  A key should be used to represent (None, INF)
# or somesuch.
FLAT = 'FLAT'

class KeyedList(list):
    """
    
    Extends the built-in type list to superficially behave like a
    dictionary with [] keyed access.  Internal representation is a
    list of (key,value) pairs.  Note: Core functionality has been
    added, but because of the way that [] does not return the name
    tuple, not all list operations may behave properly.

    Redefined functions:
        __getitem__ ([,])
        __setitem__ ([,])
        append
    New functions modeled from dictionaries:
        get
        set
        has_key
    """

    def __getitem__(self,k):
        """ The bracket [] accessor. """
        return self.get(k)

    def __setitem__(self,k,v):
        """
        The bracket [] mutator.
        Will overwrite value if key already exists, otherwise append.
        """
        return self.set(k,v)

    def append(self, (template_name, template_obj)):
        """
        Append the new PlotTemplate object to the end of the existing
        internal plot template list.

        Takes in a 2-tuple, (Name Key of new PlotTemplate, PlotTemplate Object)

        Does not have to be redefined in this subclass, but by forcing
        the tuple in the function parameters, it may catch an
        erroneous assignment.
        """
        super(KeyedList,self).append((template_name,template_obj))

    def get(self, template_name):
        """
        Get the PlotTemplate with the key <template_name>.
        Return None if it does not exist.
        """
        for (name,template_obj) in self:
            if name == template_name:
                return template_obj
        return None

    def set(self, template_name, template_obj):
        """
        If the template_name already exists in the list, change the
        entry, otherwise append the new template_name, template_obj to
        the end of the PlotTemplate list.
        """
        for (k,v) in self:
            if k == template_name:
                i = self.index((k,v))
                self.pop(i)
                self.insert(i,(template_name, template_obj))
                return True
        self.append(self, (template_name, template_obj))
        return True

    def has_key(self,template_name):
        """
        Return True if template_name is a key in the ordered list.
        Return False otherwise.
        """
        for (name,template_obj) in self:
            if name == template_name:
                return True
        return False


class PlotGroupTemplate(TopoObject):
    """
    Container class for a PlotGroup object definition.  This is
    separate from a PlotGroup object since it defines how to create a
    PlotGroup object and should contain a series of PlotTemplates.
    The PlotEngine will create the requested plot group type given the
    template definition.  The templates are used so that standard plot
    types can be redefined at the users convenience.

    The plot_templates member variable can and should be accessed
    directly by outside code.  It is KeyedList (defined in this file)
    so it can be treated like a dictionary using the [] notation, but
    it will preserve ordering.
    """

    def __init__(self, plot_templates=None, **params):
        """
        plot_templates is of the form:
            ( (name_1, PlotTemplate_1), ... , (name_i, PlotTemplate_i) )
        """
        super(PlotGroupTemplate,self).__init__(**params)
        if not plot_templates:
            self.plot_templates = KeyedList()
        else:
            self.plot_templates = KeyedList(plot_templates)
        self.description = self.name
        

class PlotGroup(TopoObject):
    """
    Container that has one or more Plots and also knows how to arrange
    the plots and other special parameters.
    """

    def __init__(self,plot_key=None,sheet_filter_lam=None,plot_list=None,shape=FLAT,**params):
        """
        plot_list can be of two types: 
        1.  A list of Plot objects that can return bitmaps when requested.
        2.  Can also be a function that returns a list of plots so
        that each time plot() is called, an updated list is created for the
        latest list of sheets in the simulation.
        """
        super(PlotGroup,self).__init__(**params)
        self.plot_list = plot_list
        self.all_plots = []
        self.added_list = []
        self.shape = shape
        self.plot_key = plot_key
        self.bitmaps = []
        self.template = None

        if sheet_filter_lam:
            self.sheet_filter_lam = sheet_filter_lam
        else:
            self.sheet_filter_lam = lambda : True

        self.debug('Input type, ', type(self.plot_list))
 

    def do_plot_cmd(self):
        """Subclasses of PlotGroup will need to create this function."""
        pass
    

    def load_images(self):
        """
        Pre:  do_plot_cmd() has already been called, so plots() will return
              valid plots.
        Post: self.bitmaps contains a list of topo.bitmap objects or None if
              no valid maps were available.

        Returns: List of bitmaps.  self.bitmaps also has been updated.
        """
        self.bitmaps = []
        for each in self.plots():
            (r,g,b) = each.matrices
            if r.shape != (0,0) and g.shape != (0,0) and b.shape != (0,0):
                # Crop activation to a maximum of 1.  Will scale brighter
                # or darker, depending.
                #
                # Should report that cropping took place.
                #
                if max(r.flat) > 0: r = MLab.clip(r,0.0,1.0)
                if max(g.flat) > 0: g = MLab.clip(g,0.0,1.0)
                if max(b.flat) > 0: b = MLab.clip(b,0.0,1.0)
                win = topo.bitmap.RGBMap(r,
                                         g,
                                         b)
                win.view_info = each.view_info
                self.bitmaps.append(win)
        return self.bitmaps
    


    def add(self,new_plot):
        """
        new_plot can be a single Plot, or it can be a list of plots.
        Either way, it will be properly added to the end of self.plot_list.
        """
        if isinstance(new_plot,types.ListType):
            if not isinstance(self.plot_list,types.ListType):
                self.warning('Adding to PlotGroup that uses dynamic plotlist')
            self.added_list.extend(new_plot)
        else:
            self.added_list.append(new_plot)


    def release_sheetviews(self):
        """
        Call release_sheetviews() on all Plots in plot list, to free
        up Sheet.sheet_view_dict entries and save memory.  Note, not
        all plots use SheetViews stored in a Sheet dictionary.
        """
        for each in self.all_plots:
            each.release_sheetviews()


    def plots(self):
        """
        Generate the bitmap lists.
        """
        bitmap_list = []
        if isinstance(self.plot_list,types.ListType):
            self.debug('Static plotgroup')
            self.all_plots = flatten(self.plot_list) + self.added_list
        else:       # Assume it's a callable object that returns a list.
            self.debug('Dynamic plotgroup')
            self.all_plots = flatten(self.plot_list()) + self.added_list
            self.debug('all_plots = ' + str(self.all_plots))

        # Eventually a simple list comprehension is not going to be
        # sufficient as outlining and other things will need to be
        # done to each of the matrices that come in from the Plot
        # objects.
        generated_bitmap_list = [each.plot() for each in self.all_plots]

        return generated_bitmap_list



class BasicPlotGroup(PlotGroup):
    """
    PlotGroup for Activation SheetViews
    """

    def __init__(self,plot_key,sheet_filter_lam,plot_list,**params):
        super(BasicPlotGroup,self).__init__(plot_key,sheet_filter_lam,plot_list,
                                            **params)


class WeightsPlotGroup(PlotGroup):
    """
    PlotGroup for Weights UnitViews
    """

    def __init__(self,plot_key,sheet_filter_lam,plot_list,**params):
        super(WeightsPlotGroup,self).__init__(plot_key,sheet_filter_lam,plot_list,
                                              **params)
        self.x = float(plot_key[2])
        self.y = float(plot_key[3])

    def do_plot_cmd(self):
        """
        Lambda function passed in, that will filter out all sheets
        except the one with the name being looked for.
        """
        sheets = topo.simulator.active_sim().get_event_processors()
        for each in sheets:
            if self.sheet_filter_lam(each):
                each.unit_view(self.x,self.y)



class WeightsArrayPlotGroup(PlotGroup):
    """
    PlotGroup for WeightsArray
    """

    def __init__(self,plot_key,sheet_filter_lam,plot_list,**params):
        super(WeightsArrayPlotGroup,self).__init__(plot_key,sheet_filter_lam,
                                                   plot_list,**params)
        self.weight_name = plot_key[1]
        self.density = float(plot_key[2])
        self.shape = (0,0)
        self._sim_ep = [s for s in topo.simulator.active_sim().get_event_processors()
                        if self.sheet_filter_lam(s)][0]


    def _generate_coords(self):
        """
        Evenly space out the units within the sheet bounding box, so
        that it doesn't matter which corner the measurements start
        from.  A 4 unit grid needs 5 segments.  List is in left-to-right,
        from top-to-bottom.
        """
        def rev(x): y = x; y.reverse(); return y
        
        aarect = self._sim_ep.bounds.aarect()
        (l,b,r,t) = aarect.lbrt()
        x = float(r - l) 
        y = float(t - b)
        x_step = x / (int(x * self.density) + 1)
        y_step = y / (int(y * self.density) + 1)
        l = l + x_step
        b = b + y_step
        coords = []
        self.shape = (int(x * self.density), int(y * self.density))
        for j in rev(range(self.shape[1])):
            for i in range(self.shape[0]):
                coords.append((x_step*i + l, y_step*j + b))
        return coords


    def do_plot_cmd(self):
        coords = self._generate_coords()
        
        full_unitview_list = [self._sim_ep.unit_view(x,y) for (x,y) in coords]
        filtered_list = [view for view in chain(*full_unitview_list)
                         if view.projection.name == self.weight_name]

        self._sim_ep.add_sheet_view(self.plot_key,filtered_list)

        for (x,y) in coords: self._sim_ep.release_unit_view(x,y)
        

