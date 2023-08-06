from assetic.models.work_request import WorkRequest
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequest(WorkRequest):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequest" class is deprecated, use "WorkRequest" instead',stacklevel=2)
		super(WorkRequest, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val)
