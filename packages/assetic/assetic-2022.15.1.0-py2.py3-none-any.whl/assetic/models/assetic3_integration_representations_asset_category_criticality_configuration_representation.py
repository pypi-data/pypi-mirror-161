from assetic.models.asset_category_criticality_configuration_representation import AssetCategoryCriticalityConfigurationRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssetCategoryCriticalityConfigurationRepresentation(AssetCategoryCriticalityConfigurationRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetCategoryCriticalityConfigurationRepresentation" class is deprecated, use "AssetCategoryCriticalityConfigurationRepresentation" instead',stacklevel=2)
		super(AssetCategoryCriticalityConfigurationRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
