from assetic.models.resource_details_group_craft_unit_list_representation import ResourceDetailsGroupCraftUnitListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitListRepresentation(ResourceDetailsGroupCraftUnitListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceDetailsGroupCraftUnitListRepresentation" class is deprecated, use "ResourceDetailsGroupCraftUnitListRepresentation" instead',stacklevel=2)
		super(ResourceDetailsGroupCraftUnitListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
