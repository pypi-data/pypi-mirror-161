from assetic.models.maintenance_work_task import MaintenanceWorkTask
import warnings
import six
class Assetic3IntegrationRepresentationsMaintenanceWorkTask(MaintenanceWorkTask):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsMaintenanceWorkTask" class is deprecated, use "MaintenanceWorkTask" instead',stacklevel=2)
		super(MaintenanceWorkTask, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
