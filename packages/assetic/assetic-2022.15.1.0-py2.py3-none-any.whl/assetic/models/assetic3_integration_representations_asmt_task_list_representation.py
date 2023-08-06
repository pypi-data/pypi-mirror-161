from assetic.models.asmt_task_list_representation import AsmtTaskListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAsmtTaskListRepresentation(AsmtTaskListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAsmtTaskListRepresentation" class is deprecated, use "AsmtTaskListRepresentation" instead',stacklevel=2)
		super(AsmtTaskListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
