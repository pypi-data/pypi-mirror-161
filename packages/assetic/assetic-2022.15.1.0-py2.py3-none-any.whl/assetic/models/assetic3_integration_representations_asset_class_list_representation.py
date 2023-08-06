from assetic.models.asset_class_list_representation import AssetClassListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetClassListRepresentation(AssetClassListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetClassListRepresentation" class is deprecated, use "AssetClassListRepresentation" instead',stacklevel=2)
		super(AssetClassListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
