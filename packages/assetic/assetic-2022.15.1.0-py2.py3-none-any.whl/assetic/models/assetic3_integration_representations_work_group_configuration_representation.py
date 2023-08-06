from assetic.models.work_group_configuration_representation import WorkGroupConfigurationRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkGroupConfigurationRepresentation(WorkGroupConfigurationRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkGroupConfigurationRepresentation" class is deprecated, use "WorkGroupConfigurationRepresentation" instead',stacklevel=2)
		super(WorkGroupConfigurationRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
