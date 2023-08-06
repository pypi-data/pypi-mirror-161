from assetic.models.assessment_form_page_representation import AssessmentFormPageRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormPageRepresentation(AssessmentFormPageRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormPageRepresentation" class is deprecated, use "AssessmentFormPageRepresentation" instead',stacklevel=2)
		super(AssessmentFormPageRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
