from assetic.models.assessment_form_tab_representation import AssessmentFormTabRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormTabRepresentation(AssessmentFormTabRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormTabRepresentation" class is deprecated, use "AssessmentFormTabRepresentation" instead',stacklevel=2)
		super(AssessmentFormTabRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
