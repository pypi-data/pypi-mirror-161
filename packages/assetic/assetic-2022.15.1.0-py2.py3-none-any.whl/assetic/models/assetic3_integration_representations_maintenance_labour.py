from assetic.models.maintenance_labour import MaintenanceLabour
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceLabour(MaintenanceLabour):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceLabour" class is deprecated, use "MaintenanceLabour" instead',stacklevel=2)
		super(MaintenanceLabour, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
