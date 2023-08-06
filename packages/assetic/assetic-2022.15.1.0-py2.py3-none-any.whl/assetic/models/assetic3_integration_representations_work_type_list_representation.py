from assetic.models.work_type_list_representation import WorkTypeListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkTypeListRepresentation(WorkTypeListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkTypeListRepresentation" class is deprecated, use "WorkTypeListRepresentation" instead',stacklevel=2)
		super(WorkTypeListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
