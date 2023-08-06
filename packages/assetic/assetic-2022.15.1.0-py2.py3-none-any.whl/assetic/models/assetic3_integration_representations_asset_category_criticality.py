from assetic.models.asset_category_criticality import AssetCategoryCriticality
import warnings
import six
class Assetic3IntegrationRepresentationsAssetCategoryCriticality(AssetCategoryCriticality):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssetCategoryCriticality" class is deprecated, use "AssetCategoryCriticality" instead',stacklevel=2)
		super(AssetCategoryCriticality, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
