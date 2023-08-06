from assetic.models.cause_sub_code import CauseSubCode
import warnings
import six
class Assetic3IntegrationRepresentationsCauseSubCode(CauseSubCode):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsCauseSubCode" class is deprecated, use "CauseSubCode" instead',stacklevel=2)
		super(CauseSubCode, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
