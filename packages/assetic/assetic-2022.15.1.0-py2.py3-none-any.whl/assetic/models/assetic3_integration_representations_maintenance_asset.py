from assetic.models.maintenance_asset import MaintenanceAsset
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceAsset(MaintenanceAsset):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceAsset" class is deprecated, use "MaintenanceAsset" instead',stacklevel=2)
		super(MaintenanceAsset, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
