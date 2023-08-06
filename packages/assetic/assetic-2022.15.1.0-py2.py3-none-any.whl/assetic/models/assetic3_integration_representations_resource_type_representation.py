from assetic.models.resource_type_representation import ResourceTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceTypeRepresentation(ResourceTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceTypeRepresentation" class is deprecated, use "ResourceTypeRepresentation" instead',stacklevel=2)
		super(ResourceTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
