from assetic.models.asmt_task_representation import AsmtTaskRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAsmtTaskRepresentation(AsmtTaskRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAsmtTaskRepresentation" class is deprecated, use "AsmtTaskRepresentation" instead',stacklevel=2)
		super(AsmtTaskRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
