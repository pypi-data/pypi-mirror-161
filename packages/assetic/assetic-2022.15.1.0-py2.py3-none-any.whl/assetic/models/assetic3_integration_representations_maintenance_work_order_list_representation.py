from assetic.models.maintenance_work_order_list_representation import MaintenanceWorkOrderListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceWorkOrderListRepresentation(MaintenanceWorkOrderListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceWorkOrderListRepresentation" class is deprecated, use "MaintenanceWorkOrderListRepresentation" instead',stacklevel=2)
		super(MaintenanceWorkOrderListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
