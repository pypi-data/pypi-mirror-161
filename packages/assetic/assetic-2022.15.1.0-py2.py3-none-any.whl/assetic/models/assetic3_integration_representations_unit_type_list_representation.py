from assetic.models.unit_type_list_representation import UnitTypeListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsUnitTypeListRepresentation(UnitTypeListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsUnitTypeListRepresentation" class is deprecated, use "UnitTypeListRepresentation" instead',stacklevel=2)
		super(UnitTypeListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
