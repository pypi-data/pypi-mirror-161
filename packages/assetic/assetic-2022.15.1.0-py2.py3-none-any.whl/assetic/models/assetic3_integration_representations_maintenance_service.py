from assetic.models.maintenance_service import MaintenanceService
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceService(MaintenanceService):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceService" class is deprecated, use "MaintenanceService" instead',stacklevel=2)
		super(MaintenanceService, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
