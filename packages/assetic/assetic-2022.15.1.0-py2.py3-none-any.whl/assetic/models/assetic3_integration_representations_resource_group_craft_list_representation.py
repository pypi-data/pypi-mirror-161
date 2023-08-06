from assetic.models.resource_group_craft_list_representation import ResourceGroupCraftListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceGroupCraftListRepresentation(ResourceGroupCraftListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceGroupCraftListRepresentation" class is deprecated, use "ResourceGroupCraftListRepresentation" instead',stacklevel=2)
		super(ResourceGroupCraftListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
