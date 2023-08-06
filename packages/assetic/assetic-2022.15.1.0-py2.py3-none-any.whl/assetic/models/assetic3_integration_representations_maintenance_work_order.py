from assetic.models.maintenance_work_order import MaintenanceWorkOrder
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceWorkOrder(MaintenanceWorkOrder):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceWorkOrder" class is deprecated, use "MaintenanceWorkOrder" instead',stacklevel=2)
		super(MaintenanceWorkOrder, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
