from assetic.models.form_control_representation import FormControlRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormControlRepresentation(FormControlRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormControlRepresentation" class is deprecated, use "FormControlRepresentation" instead',stacklevel=2)
		super(FormControlRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
