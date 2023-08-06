from assetic.models.form_layout_pattern_representation import FormLayoutPatternRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternRepresentation(FormLayoutPatternRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternRepresentation" class is deprecated, use "FormLayoutPatternRepresentation" instead',stacklevel=2)
		super(FormLayoutPatternRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
