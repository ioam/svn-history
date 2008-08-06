"""
Moved to topo/params/__init__.py
"""

__version__='$Revision: 8792 $'


msg = """
'topo.base.parameterclasses' is deprecated; use 'topo.param'.

For instance, instead of:
 from topo.base.parameterclasses import BooleanParameter,StringParameter
 p1 = BooleanParameter(False)
 p2 = StringParameter('test')
Use:
 from topo import param
 p = param.Boolean(False)
 p = param.String('test')
"""

import warnings
warnings.warn(msg,DeprecationWarning,stacklevel=2)


from topo.param import *

from topo.param import Boolean as BooleanParameter
from topo.param import String as StringParameter
from topo.param import Callable as CallableParameter
from topo.param import Composite as CompositeParameter
from topo.param import Selector as SelectorParameter
from topo.param import ObjectSelector as ObjectSelectorParameter
from topo.param import ClassSelector as ClassSelectorParameter
from topo.param import List as ListParameter
from topo.param import Dict as DictParameter

