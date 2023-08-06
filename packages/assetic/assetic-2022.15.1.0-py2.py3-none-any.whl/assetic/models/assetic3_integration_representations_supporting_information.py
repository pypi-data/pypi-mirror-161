from assetic.models.supporting_information import SupportingInformation
import warnings
import six
class Assetic3IntegrationRepresentationsSupportingInformation(SupportingInformation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsSupportingInformation" class is deprecated, use "SupportingInformation" instead',stacklevel=2)
		super(SupportingInformation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
