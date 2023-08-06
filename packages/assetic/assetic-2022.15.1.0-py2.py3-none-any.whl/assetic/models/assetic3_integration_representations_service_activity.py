from assetic.models.service_activity import ServiceActivity
import warnings
import six
class Assetic3IntegrationRepresentationsServiceActivity(ServiceActivity):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsServiceActivity" class is deprecated, use "ServiceActivity" instead',stacklevel=2)
		super(ServiceActivity, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
