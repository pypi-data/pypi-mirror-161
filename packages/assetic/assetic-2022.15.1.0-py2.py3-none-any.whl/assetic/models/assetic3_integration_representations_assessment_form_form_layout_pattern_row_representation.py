from assetic.models.form_layout_pattern_row_representation import FormLayoutPatternRowRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternRowRepresentation(FormLayoutPatternRowRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternRowRepresentation" class is deprecated, use "FormLayoutPatternRowRepresentation" instead',stacklevel=2)
		super(FormLayoutPatternRowRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
