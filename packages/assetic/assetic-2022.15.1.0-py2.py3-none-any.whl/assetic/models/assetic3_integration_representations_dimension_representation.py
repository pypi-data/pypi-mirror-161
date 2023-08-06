from assetic.models.dimension_representation import DimensionRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDimensionRepresentation(DimensionRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDimensionRepresentation" class is deprecated, use "DimensionRepresentation" instead',stacklevel=2)
		super(DimensionRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
