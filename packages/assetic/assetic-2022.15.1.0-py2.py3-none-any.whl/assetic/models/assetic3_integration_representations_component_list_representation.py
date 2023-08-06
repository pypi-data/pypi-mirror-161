from assetic.models.component_list_representation import ComponentListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComponentListRepresentation(ComponentListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComponentListRepresentation" class is deprecated, use "ComponentListRepresentation" instead',stacklevel=2)
		super(ComponentListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
