from assetic.models.failure_code import FailureCode
import warnings
import six
class Assetic3IntegrationRepresentationsFailureCode(FailureCode):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFailureCode" class is deprecated, use "FailureCode" instead',stacklevel=2)
		super(FailureCode, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
