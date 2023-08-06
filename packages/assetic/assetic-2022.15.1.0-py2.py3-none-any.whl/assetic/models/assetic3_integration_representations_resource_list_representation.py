from assetic.models.resource_list_representation import ResourceListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceListRepresentation(ResourceListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceListRepresentation" class is deprecated, use "ResourceListRepresentation" instead',stacklevel=2)
		super(ResourceListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
