from assetic.models.work_order_meter_representation import WorkOrderMeterRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkOrderMeterRepresentation(WorkOrderMeterRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkOrderMeterRepresentation" class is deprecated, use "WorkOrderMeterRepresentation" instead',stacklevel=2)
		super(WorkOrderMeterRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
