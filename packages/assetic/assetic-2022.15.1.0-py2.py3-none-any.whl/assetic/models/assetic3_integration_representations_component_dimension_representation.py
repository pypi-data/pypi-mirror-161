from assetic.models.component_dimension_representation import ComponentDimensionRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComponentDimensionRepresentation(ComponentDimensionRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComponentDimensionRepresentation" class is deprecated, use "ComponentDimensionRepresentation" instead',stacklevel=2)
		super(ComponentDimensionRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
