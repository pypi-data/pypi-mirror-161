from assetic.models.lowest_maintenance_item import LowestMaintenanceItem
import warnings
import six
class Assetic3IntegrationRepresentationsLowestMaintenanceItem(LowestMaintenanceItem):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsLowestMaintenanceItem" class is deprecated, use "LowestMaintenanceItem" instead',stacklevel=2)
		super(LowestMaintenanceItem, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
