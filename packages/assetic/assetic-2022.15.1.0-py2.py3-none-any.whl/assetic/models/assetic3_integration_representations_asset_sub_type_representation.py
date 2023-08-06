from assetic.models.asset_sub_type_representation import AssetSubTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetSubTypeRepresentation(AssetSubTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetSubTypeRepresentation" class is deprecated, use "AssetSubTypeRepresentation" instead',stacklevel=2)
		super(AssetSubTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
