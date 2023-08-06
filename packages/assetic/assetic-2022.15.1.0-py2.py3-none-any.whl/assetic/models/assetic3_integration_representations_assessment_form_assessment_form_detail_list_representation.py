from assetic.models.assessment_form_detail_list_representation import AssessmentFormDetailListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormDetailListRepresentation(AssessmentFormDetailListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormAssessmentFormDetailListRepresentation" class is deprecated, use "AssessmentFormDetailListRepresentation" instead',stacklevel=2)
		super(AssessmentFormDetailListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
