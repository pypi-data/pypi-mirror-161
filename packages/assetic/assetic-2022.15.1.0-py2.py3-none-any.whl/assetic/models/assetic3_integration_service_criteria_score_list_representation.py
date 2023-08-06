from assetic.models.service_criteria_score_list_representation import ServiceCriteriaScoreListRepresentation
import warnings
import six
class Assetic3IntegrationServiceCriteriaScoreListRepresentation(ServiceCriteriaScoreListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationServiceCriteriaScoreListRepresentation" class is deprecated, use "ServiceCriteriaScoreListRepresentation" instead',stacklevel=2)
		super(ServiceCriteriaScoreListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
