from assetic.models.asmt_task_form_representation import AsmtTaskFormRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAsmtTaskFormRepresentation(AsmtTaskFormRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAsmtTaskFormRepresentation" class is deprecated, use "AsmtTaskFormRepresentation" instead',stacklevel=2)
		super(AsmtTaskFormRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
