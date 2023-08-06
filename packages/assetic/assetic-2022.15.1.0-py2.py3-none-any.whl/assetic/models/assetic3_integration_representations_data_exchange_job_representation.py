from assetic.models.data_exchange_job_representation import DataExchangeJobRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDataExchangeJobRepresentation(DataExchangeJobRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDataExchangeJobRepresentation" class is deprecated, use "DataExchangeJobRepresentation" instead',stacklevel=2)
		super(DataExchangeJobRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
