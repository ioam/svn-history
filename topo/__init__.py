"""
Topographica cortical map simulator package.

Topographica is designed as a collection of packages from which
elements can be selected to model specific systems.  For more
information, see the individual subpackages:

base        - Core Topographica functions and classes
plotting    - Visualization functions and classes
analysis    - Analysis functions and classes (besides plotting)
tkgui       - Tk-based graphical user interface (GUI)
commands    - High-level user commands
misc        - Various useful independent modules

The Topographica primitives library consists of a family of classes
that can be used with the above functions and classes:

sheets      - Sheet classes: 2D arrays of processing units
projections - Projection classes: connections between Sheets
patterns    - PatternGenerator classes: 2D input or weight patterns 
eps         - EventProcessor classes: other simulation objects
outputfns   - Output functions, for e.g. normalization or squashing
responsefns - Calculate the response of a Projection
learningfns - Adjust weights for a Projection


Each of the library directories can be extended with new classes of
the appropriate type, just by adding a new .py file to that directory.
E.g. new PatternGenerator classes can be added to patterns/, and will
then show up in the GUI menus as potential input patterns.

$Id$
"""
__version__='$Revision $'

# The tests and the GUI are omitted from this list, and have to be
# imported explicitly if desired.
__all__ = ['analysis',
           'base',
           'commands',
           'eps',
           'learningfns',
           'misc',
           'outputfns',
           'patterns',
           'plotting',
           'projections',
           'responsefns',
           'sheets']

# gets set by the topographica script
release = ''

# Enable automatic importing of .ty files, treating them just like .py
import topo.misc.tyimputil



# CEBALERT: name and location might be changed.
from topo.base.parameterizedobject import ParameterizedObject,Parameter
import __main__
import inspect
class PickleSupport(object):
    """
    When requested to be pickled, stores topo's PO classes' attributes and
    topo.sim.startup_commands.
    """
    def __getstate__(self):
        """
        Return a dictionary of topo's PO classes' attributes, plus
        topo.sim's startup_commands.

        Subpackages of topo that are not part of the simulation are
        excluded from having their classes' attributes saved: plotting,
        tkgui, and tests.  [CB: can add analysis, etc.]

        Also sets the value of topo.sim.RELEASE.
        """
        # warn that classes & functions defined in __main__ won't unpickle
        import types
        for k,v in __main__.__dict__.items():
            # there's classes and functions...what else?
            if isinstance(v,type) or isinstance(v,types.FunctionType):
                if v.__module__ == "__main__":
                    ParameterizedObject().warning("%s (type %s) has source in __main__; it will only be found on unpickling if the class is explicitly defined (e.g. by running the same script first) before unpickling."%(k,type(v)))

        
        class_attributes = {}
        # For now we just search topo, but it could be extended to all packages.
        self.get_PO_class_attributes(topo,class_attributes,[],exclude=('plotting','tkgui','tests'))

        global sim
        sim.RELEASE=release

        return {'class_attributes':class_attributes,
                'startup_commands':topo.sim.actual_sim.startup_commands}   


    def __setstate__(self,state):
        """
        Execute the startup commands and set class attributes.
        """
        for cmd in state['startup_commands']:
            exec cmd in __main__.__dict__
            
        for class_name,state in state['class_attributes'].items():
            
            # from "topo.base.parameter.Parameter", we want "topo.base.parameter"
            module_path = class_name[0:class_name.rindex('.')]
            exec 'import '+module_path in __main__.__dict__
            
            # now restore class Parameter values
            for p_name,p in state.items():
                __main__.__dict__['val'] = p
                try:
                    exec 'setattr('+class_name+',"'+p_name+'",val)' in __main__.__dict__
                except:
                    ParameterizedObject().warning('Problem restoring parameter %s=%s for class %s; name may have changed since the snapshot was created.' % (p_name,repr(p),class_name))


    # CEBALERT: might could be simplified
    def get_PO_class_attributes(self,module,class_attributes,processed_modules,exclude=()):
        """
        Recursively search module and get attributes of ParameterizedObject classes within it.

        class_attributes is a dictionary {module.path.and.Classname: state}, where state
        is the dictionary {attribute: value}.

        Something is considered a module for our purposes if inspect says it's a module,
        and it defines __all__. We only search through modules listed in __all__.

        Keeps a list of processed modules to avoid looking at the same one
        more than once (since e.g. __main__ contains __main__ contains
        __main__...)

        Modules can be specifically excluded if listed in exclude.
        """
        dict_ = module.__dict__
        for (k,v) in dict_.items():
            if '__all__' in dict_ and inspect.ismodule(v) and k not in exclude:
                if k in dict_['__all__'] and v not in processed_modules:
                    self.get_PO_class_attributes(v,class_attributes,processed_modules,exclude)
                processed_modules.append(v)

            else:
                if isinstance(v,type) and issubclass(v,ParameterizedObject):

                    # Note: we take the class name as v.__name__, not k, because
                    # k might be just a label for the true class. For example,
                    # if Topographica falls back to the unoptimized components,
                    # k could be "CFPRF_DotProduct_opt", but v.__name__
                    # - and the actual class - is "CFPRF_DotProduct". It
                    # is correct to set the attributes on the true class.
                    full_class_path = v.__module__+'.'+v.__name__
                    class_attributes[full_class_path] = {}
                    # POs always have __dict__, never slots
                    for (name,obj) in v.__dict__.items():
                        if isinstance(obj,Parameter):
                            class_attributes[full_class_path][name] = obj


                    


from topo.base.simulation import SimSingleton
sim = SimSingleton()


_picklesupport = PickleSupport()


def about(display=True):
    """Print release and licensing information."""

    ABOUT_TEXT = """
Pre-release version """+release+ \
""" of Topographica; an updated version may be
available from topographica.org.

Copyright 2005-2007 James A. Bednar, Christopher Ball, Christopher
Palmer, Yoonsuck Choe, Julien Ciroux, Judah B. De Paula, Judith Law,
Alan Lindsay, Louise Mathews, Jefferson Provost, Veldri Kurniawan,
Tikesh Ramtohul, Lewis Ng, Ruaidhri Primrose, Foivos Demertzis, Roger
Zhao, and Yiu Fai Sit.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation. This program is distributed
in the hope that it will be useful, but without any warranty; without
even the implied warranty of merchantability or fitness for a
particular purpose.  See the GNU General Public License for more
details.
"""
    if display:
        print ABOUT_TEXT
    else:        
        return ABOUT_TEXT


# Set most floating-point errors to be fatal for safety; see
# topo/misc/patternfns.py for examples of how to disable
# the exceptions when doing so is safe.  Underflow is always
# considered safe; e.g. input patterns can be very small
# at large distances, and when they are scaled by small
# weights underflows are common and not a problem.
from numpy import seterr
old_seterr_settings=seterr(all="raise",under="ignore")

