from assetic.models.component_dimension_list_representation import ComponentDimensionListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComponentDimensionListRepresentation(ComponentDimensionListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComponentDimensionListRepresentation" class is deprecated, use "ComponentDimensionListRepresentation" instead',stacklevel=2)
		super(ComponentDimensionListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
