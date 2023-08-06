from assetic.models.remedy_code import RemedyCode
import warnings
import six
class Assetic3IntegrationRepresentationsRemedyCode(RemedyCode):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRemedyCode" class is deprecated, use "RemedyCode" instead',stacklevel=2)
		super(RemedyCode, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
