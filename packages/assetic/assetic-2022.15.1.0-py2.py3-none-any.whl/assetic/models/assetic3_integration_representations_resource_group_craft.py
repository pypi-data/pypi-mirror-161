from assetic.models.resource_group_craft import ResourceGroupCraft
import warnings
import six
class Assetic3IntegrationRepresentationsResourceGroupCraft(ResourceGroupCraft):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsResourceGroupCraft" class is deprecated, use "ResourceGroupCraft" instead',stacklevel=2)
		super(ResourceGroupCraft, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
