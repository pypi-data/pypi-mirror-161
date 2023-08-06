from assetic.models.form_control_combobox_item_representation import FormControlComboboxItemRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormControlComboboxItemRepresentation(FormControlComboboxItemRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormControlComboboxItemRepresentation" class is deprecated, use "FormControlComboboxItemRepresentation" instead',stacklevel=2)
		super(FormControlComboboxItemRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
