from assetic.models.asset_class_representation import AssetClassRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetClassRepresentation(AssetClassRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetClassRepresentation" class is deprecated, use "AssetClassRepresentation" instead',stacklevel=2)
		super(AssetClassRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
