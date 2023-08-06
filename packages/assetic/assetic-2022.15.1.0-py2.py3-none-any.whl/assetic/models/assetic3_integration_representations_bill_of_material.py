from assetic.models.bill_of_material import BillOfMaterial
import warnings
import six
class Assetic3IntegrationRepresentationsBillOfMaterial(BillOfMaterial):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsBillOfMaterial" class is deprecated, use "BillOfMaterial" instead',stacklevel=2)
		super(BillOfMaterial, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
