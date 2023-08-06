from assetic.models.form_layout_pattern_column_representation import FormLayoutPatternColumnRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternColumnRepresentation(FormLayoutPatternColumnRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormLayoutPatternColumnRepresentation" class is deprecated, use "FormLayoutPatternColumnRepresentation" instead',stacklevel=2)
		super(FormLayoutPatternColumnRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
