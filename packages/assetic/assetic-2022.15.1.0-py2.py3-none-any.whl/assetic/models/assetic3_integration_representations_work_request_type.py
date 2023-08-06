from assetic.models.work_request_type import WorkRequestType
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestType(WorkRequestType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestType" class is deprecated, use "WorkRequestType" instead',stacklevel=2)
		super(WorkRequestType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
