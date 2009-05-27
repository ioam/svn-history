import numpy
from topo import param
from topo.projection.basic import CFProjection, MaskedCFIter
from topo.base.patterngenerator import PatternGenerator
from topo.pattern import Constant

class CFProjectionM(CFProjection):

	strength_generator = param.ClassSelector(PatternGenerator,
		default=Constant(),constant=False,
		doc="""Generate initial strength values.""")

	def __init__(self, **params):
		super(CFProjectionM,self).__init__(**params)
		self.strength_generator.xdensity, self.strength_generator.ydensity = self.activity.shape
		self.strength_matrix = self.strength_generator()

	def activate(self, input_activity):
		"""Activate using the specified response_fn and output_fn."""
		self.input_buffer = input_activity
		self.activity *=0.0
		self.response_fn(MaskedCFIter(self), input_activity, self.activity, self.strength)
		self.activity *= self.strength_matrix

		for of in self.output_fns:
			of(self.activity)
        
