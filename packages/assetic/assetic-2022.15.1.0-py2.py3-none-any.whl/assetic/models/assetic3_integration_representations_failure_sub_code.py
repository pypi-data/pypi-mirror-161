from assetic.models.failure_sub_code import FailureSubCode
import warnings
import six
class Assetic3IntegrationRepresentationsFailureSubCode(FailureSubCode):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFailureSubCode" class is deprecated, use "FailureSubCode" instead',stacklevel=2)
		super(FailureSubCode, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
