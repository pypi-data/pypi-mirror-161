from assetic.models.resource_representation import ResourceRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceRepresentation(ResourceRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceRepresentation" class is deprecated, use "ResourceRepresentation" instead',stacklevel=2)
		super(ResourceRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
