from assetic.models.maintenance_material import MaintenanceMaterial
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceMaterial(MaintenanceMaterial):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceMaterial" class is deprecated, use "MaintenanceMaterial" instead',stacklevel=2)
		super(MaintenanceMaterial, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
