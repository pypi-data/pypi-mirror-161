from assetic.models.asset_type_representation import AssetTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetTypeRepresentation(AssetTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetTypeRepresentation" class is deprecated, use "AssetTypeRepresentation" instead',stacklevel=2)
		super(AssetTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
