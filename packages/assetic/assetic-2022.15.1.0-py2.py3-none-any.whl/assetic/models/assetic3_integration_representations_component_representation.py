from assetic.models.component_representation import ComponentRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComponentRepresentation(ComponentRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComponentRepresentation" class is deprecated, use "ComponentRepresentation" instead',stacklevel=2)
		super(ComponentRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
