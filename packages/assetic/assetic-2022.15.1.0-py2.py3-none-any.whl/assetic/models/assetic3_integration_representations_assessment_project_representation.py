from assetic.models.assessment_project_representation import AssessmentProjectRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentProjectRepresentation(AssessmentProjectRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentProjectRepresentation" class is deprecated, use "AssessmentProjectRepresentation" instead',stacklevel=2)
		super(AssessmentProjectRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
