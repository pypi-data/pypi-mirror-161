from assetic.models.asset_type_list_representation import AssetTypeListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetTypeListRepresentation(AssetTypeListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetTypeListRepresentation" class is deprecated, use "AssetTypeListRepresentation" instead',stacklevel=2)
		super(AssetTypeListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
