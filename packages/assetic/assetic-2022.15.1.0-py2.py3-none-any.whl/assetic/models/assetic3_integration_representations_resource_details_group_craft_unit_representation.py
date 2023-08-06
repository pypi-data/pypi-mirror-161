from assetic.models.resource_details_group_craft_unit_representation import ResourceDetailsGroupCraftUnitRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitRepresentation(ResourceDetailsGroupCraftUnitRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitRepresentation" class is deprecated, use "ResourceDetailsGroupCraftUnitRepresentation" instead',stacklevel=2)
		super(ResourceDetailsGroupCraftUnitRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
