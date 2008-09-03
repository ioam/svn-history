"""

If your script still doesn't work, try enabling legacy support
(XXX cmd) or submitting it to the Topographica developers.

./topographica -c "from topo.misc.legacy import install_legacy_support; install_legacy_support()" <SCRIPT> -g etc


"""

## >  |  > 6. (optional) Write a python function to update a .ty script using the
## >  |  >    old names to use the new ones; this would go into
## >  |  >    topo/misc/legacy.py.  We'll probably add lots more to such a script
## >  |  >    later, e.g. based on the SVN version number in it, but for now it
## >  |  >    can be very simple search-and-replaces.
## >  |
## >  |  Okay. Here's a start:
## >  |
## >  |  str = open(filename,'r').read()
## >  |  for old,new in replacements:
## >  |      str = new.join(str.split(old))
## >  |  os.rename(filename,filename+'.bak')
## >  |  open(filename,'w').write(str)
## >  |
## >  |  where replacements is list of strings to be replaced and their
## >  |  replacements.
## >
## >  Sounds good.  We can then make a list of replacements with a
## >  corresponding range of SVN version numbers, and then can add something
## >  to search in the str for the __version__, and can filter the
## >  replacements list so that it contains only the right replacements to
## >  apply for that range of versions.
## >
## >  The replacements will presumably need to be regexps eventually.  For
## >  this task it's fine for them to be strings, but in general we'll
## >  provably have to do some fancier patching.  Anyway, the version above
## >  looks like all we need for now.

## The main issue is to get a list of all the renaming or moving that
## you've done; do you have that?

import os
import sys

# should be ordered most to least specific, but it isn't yet
replacements = [
    ('weights_shape'                 , 'cf_shape'),
    ('topo.outputfns.homeostatic'    , 'topo.outputfn'),
    ('topo.sheets.generatorsheet'    , 'topo.sheet'),
    ('topo.base.parameterizedobject' , 'topo.param.parameterized'),
    
    ('topo.commands'                 , 'topo.command'),
    ('topo.patterns'                 , 'topo.pattern'),
    ('topo.misc.traces'              , 'topo.misc.trace'),
    ('topo.misc.utils'               , 'topo.misc.util'),
    ('topo.misc.patternfns'          , 'topo.misc.patternfn'),
    ('topo.misc.numbergenerators'    , 'topo.misc.numbergenerator'),
    ('topo.misc.filepaths'           , 'topo.misc.filepath'),
    ('topo.base.functionfamilies'    , 'topo.base.functionfamily'),
    ('topo.base.arrayutils'          , 'topo.base.arrayutil'),
    ('topo.sheet.generatorsheet'     , 'topo.sheet.generator'),
    ('topo.patterns'                 , 'topo.pattern'),
    ('topo.projections'              , 'topo.projection'),
    ('topo.sheets'                   , 'topo.sheet'),
    ('topo.eps'                      , 'topo.ep'),
    ('topo.coordmapperfns'           , 'topo.coordmapperfn'),
    ('topo.learningfns'              , 'topo.learningfn'),
    ('topo.outputfns'                , 'topo.outputfn'),
    ('topo.responsefns'              , 'topo.responsefn'),
#   ('topo.learningfns.projfns'      , 'topo.learningfn.projfn'),
#   ('topo.outputfns.projfns'        , 'topo.outputfn.projfn'), 
#   ('topo.responsefns.projfns'      , 'topo.responsefn.projfn'),    
    ('.projfns'                      , '.projfn'),
    ('ParameterizedObject'           , 'Parameterized'),
    ('parameterizedobject'           , 'parameterized'),
    ('topo.base.parameterclasses'    , 'topo.param'),
    ('BooleanParameter'              , 'Boolean'),
    ('StringParameter'               , 'String'),
    ('CallableParameter'             , 'Callable'),
    ('CompositeParameter'            , 'Composite'),
    ('SelectorParameter'             , 'Selector'),  
    ('ObjectSelectorParameter'       , 'ObjectSelector'),
    ('ClassSelectorParameter'        , 'ClassSelector'),  
    ('ListParameter'                 , 'List'),  
    ('DictParameter'                 , 'Dict'),
    ('topo.base.functionfamilies'    , 'topo.base.functionfamily'),
    ('topo.misc.numbergenerators'    , 'topo.numbergen'),
    ('topo.misc.patterns'            , 'topo.misc.pattern'),
    ('topo.misc.traces'              , 'topo.misc.trace')
    ]



removals = [
    'from topo.base.parameterclasses import DynamicNumber',
    'DynamicNumber()' # i.e. need to remove Dynamic( and then )
    ]
 

filename = sys.argv[1] 
#os.rename(filename,filename+'.bak')

str = open(filename,'r').read()


### REPLACEMENTS
for old,new in replacements:
    str = new.join(str.split(old))


### REMOVALS
# not yet implemented 


#print str
open(filename+'_0.9.5','w').write(str)
