from assetic.models.form_control_calculation_control_representation import FormControlCalculationControlRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormControlCalculationControlRepresentation(FormControlCalculationControlRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormControlCalculationControlRepresentation" class is deprecated, use "FormControlCalculationControlRepresentation" instead',stacklevel=2)
		super(FormControlCalculationControlRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
