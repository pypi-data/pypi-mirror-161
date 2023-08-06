from assetic.models.cause_code import CauseCode
import warnings
import six
class Assetic3IntegrationRepresentationsCauseCode(CauseCode):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsCauseCode" class is deprecated, use "CauseCode" instead',stacklevel=2)
		super(CauseCode, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
