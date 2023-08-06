from assetic.models.work_request_sub_type import WorkRequestSubType
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestSubType(WorkRequestSubType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestSubType" class is deprecated, use "WorkRequestSubType" instead',stacklevel=2)
		super(WorkRequestSubType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
