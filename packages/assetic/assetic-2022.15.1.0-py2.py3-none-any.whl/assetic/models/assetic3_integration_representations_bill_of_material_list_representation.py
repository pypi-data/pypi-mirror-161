from assetic.models.bill_of_material_list_representation import BillOfMaterialListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsBillOfMaterialListRepresentation(BillOfMaterialListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsBillOfMaterialListRepresentation" class is deprecated, use "BillOfMaterialListRepresentation" instead',stacklevel=2)
		super(BillOfMaterialListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
