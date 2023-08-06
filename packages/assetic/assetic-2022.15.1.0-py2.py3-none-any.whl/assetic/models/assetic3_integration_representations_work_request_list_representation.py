from assetic.models.work_request_list_representation import WorkRequestListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestListRepresentation(WorkRequestListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestListRepresentation" class is deprecated, use "WorkRequestListRepresentation" instead',stacklevel=2)
		super(WorkRequestListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
