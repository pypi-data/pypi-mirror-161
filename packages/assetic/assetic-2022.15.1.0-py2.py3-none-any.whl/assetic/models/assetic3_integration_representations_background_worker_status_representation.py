from assetic.models.background_worker_status_representation import BackgroundWorkerStatusRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsBackgroundWorkerStatusRepresentation(BackgroundWorkerStatusRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsBackgroundWorkerStatusRepresentation" class is deprecated, use "BackgroundWorkerStatusRepresentation" instead',stacklevel=2)
		super(BackgroundWorkerStatusRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
