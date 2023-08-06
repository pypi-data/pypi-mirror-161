from assetic.models.data_exchange_task import DataExchangeTask
import warnings
import six
class Assetic3IntegrationRepresentationsDataExchangeTask(DataExchangeTask):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDataExchangeTask" class is deprecated, use "DataExchangeTask" instead',stacklevel=2)
		super(DataExchangeTask, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
