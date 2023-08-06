from assetic.models.maintenance_asset_type import MaintenanceAssetType
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceAssetType(MaintenanceAssetType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceAssetType" class is deprecated, use "MaintenanceAssetType" instead',stacklevel=2)
		super(MaintenanceAssetType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
