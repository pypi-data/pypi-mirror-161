from assetic.models.asset_spatial_location_representation import AssetSpatialLocationRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetSpatialLocationRepresentation(AssetSpatialLocationRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetSpatialLocationRepresentation" class is deprecated, use "AssetSpatialLocationRepresentation" instead',stacklevel=2)
		super(AssetSpatialLocationRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
