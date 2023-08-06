from assetic.models.assessment_form_detail_representation import AssessmentFormDetailRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormDetailRepresentation(AssessmentFormDetailRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormDetailRepresentation" class is deprecated, use "AssessmentFormDetailRepresentation" instead',stacklevel=2)
		super(AssessmentFormDetailRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
