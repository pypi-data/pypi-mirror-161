from assetic.models.work_type import WorkType
import warnings
import six
class Assetic3IntegrationRepresentationsWorkType(WorkType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkType" class is deprecated, use "WorkType" instead',stacklevel=2)
		super(WorkType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
