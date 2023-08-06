from assetic.models.maintenance_scheduling import MaintenanceScheduling
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceScheduling(MaintenanceScheduling):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceScheduling" class is deprecated, use "MaintenanceScheduling" instead',stacklevel=2)
		super(MaintenanceScheduling, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
