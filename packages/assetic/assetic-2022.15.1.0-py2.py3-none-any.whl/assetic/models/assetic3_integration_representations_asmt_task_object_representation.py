from assetic.models.asmt_task_object_representation import AsmtTaskObjectRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAsmtTaskObjectRepresentation(AsmtTaskObjectRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAsmtTaskObjectRepresentation" class is deprecated, use "AsmtTaskObjectRepresentation" instead',stacklevel=2)
		super(AsmtTaskObjectRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
