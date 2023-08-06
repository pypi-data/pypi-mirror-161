from assetic.models.asset_sub_class_representation import AssetSubClassRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetSubClassRepresentation(AssetSubClassRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetSubClassRepresentation" class is deprecated, use "AssetSubClassRepresentation" instead',stacklevel=2)
		super(AssetSubClassRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
