from assetic.models.maintenance_asset_sub_type import MaintenanceAssetSubType
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceAssetSubType(MaintenanceAssetSubType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceAssetSubType" class is deprecated, use "MaintenanceAssetSubType" instead',stacklevel=2)
		super(MaintenanceAssetSubType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
