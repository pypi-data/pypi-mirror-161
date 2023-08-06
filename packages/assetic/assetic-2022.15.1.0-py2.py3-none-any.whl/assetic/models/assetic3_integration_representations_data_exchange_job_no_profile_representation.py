from assetic.models.data_exchange_job_no_profile_representation import DataExchangeJobNoProfileRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDataExchangeJobNoProfileRepresentation(DataExchangeJobNoProfileRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDataExchangeJobNoProfileRepresentation" class is deprecated, use "DataExchangeJobNoProfileRepresentation" instead',stacklevel=2)
		super(DataExchangeJobNoProfileRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
