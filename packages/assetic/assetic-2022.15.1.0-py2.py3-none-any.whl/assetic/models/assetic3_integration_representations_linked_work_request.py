from assetic.models.linked_work_request import LinkedWorkRequest
import warnings
import six
class Assetic3IntegrationRepresentationsLinkedWorkRequest(LinkedWorkRequest):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsLinkedWorkRequest" class is deprecated, use "LinkedWorkRequest" instead',stacklevel=2)
		super(LinkedWorkRequest, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
