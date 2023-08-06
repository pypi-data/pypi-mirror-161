from assetic.models.asset_category_configuration_representation import AssetCategoryConfigurationRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation(AssetCategoryConfigurationRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetCategoryConfigurationRepresentation" class is deprecated, use "AssetCategoryConfigurationRepresentation" instead',stacklevel=2)
		super(AssetCategoryConfigurationRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
