from assetic.models.form_control_group_representation import FormControlGroupRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormControlGroupRepresentation(FormControlGroupRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormControlGroupRepresentation" class is deprecated, use "FormControlGroupRepresentation" instead',stacklevel=2)
		super(FormControlGroupRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
