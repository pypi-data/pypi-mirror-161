from assetic.models.assessment_project_type_representation import AssessmentProjectTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentProjectTypeRepresentation(AssessmentProjectTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentProjectTypeRepresentation" class is deprecated, use "AssessmentProjectTypeRepresentation" instead',stacklevel=2)
		super(AssessmentProjectTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
