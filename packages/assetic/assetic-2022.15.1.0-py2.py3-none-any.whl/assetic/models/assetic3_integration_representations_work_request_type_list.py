from assetic.models.work_request_type_list import WorkRequestTypeList
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestTypeList(WorkRequestTypeList):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestTypeList" class is deprecated, use "WorkRequestTypeList" instead',stacklevel=2)
		super(WorkRequestTypeList, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
