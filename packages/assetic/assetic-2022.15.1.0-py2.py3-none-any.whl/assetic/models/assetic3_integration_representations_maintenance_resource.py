from assetic.models.maintenance_resource import MaintenanceResource
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceResource(MaintenanceResource):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceResource" class is deprecated, use "MaintenanceResource" instead',stacklevel=2)
		super(MaintenanceResource, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
