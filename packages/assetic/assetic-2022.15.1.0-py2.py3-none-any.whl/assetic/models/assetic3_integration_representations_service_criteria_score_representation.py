from assetic.models.service_criteria_score_representation import ServiceCriteriaScoreRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsServiceCriteriaScoreRepresentation(ServiceCriteriaScoreRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsServiceCriteriaScoreRepresentation" class is deprecated, use "ServiceCriteriaScoreRepresentation" instead',stacklevel=2)
		super(ServiceCriteriaScoreRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
