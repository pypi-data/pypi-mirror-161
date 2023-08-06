from assetic.models.service_activity_list_representation import ServiceActivityListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsServiceActivityListRepresentation(ServiceActivityListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsServiceActivityListRepresentation" class is deprecated, use "ServiceActivityListRepresentation" instead',stacklevel=2)
		super(ServiceActivityListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
