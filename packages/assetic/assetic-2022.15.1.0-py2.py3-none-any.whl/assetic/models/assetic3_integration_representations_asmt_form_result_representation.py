from assetic.models.asmt_form_result_representation import AsmtFormResultRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAsmtFormResultRepresentation(AsmtFormResultRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAsmtFormResultRepresentation" class is deprecated, use "AsmtFormResultRepresentation" instead',stacklevel=2)
		super(AsmtFormResultRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
