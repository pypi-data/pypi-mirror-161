from assetic.models.complex_asset_list_representation import ComplexAssetListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComplexAssetListRepresentation(ComplexAssetListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComplexAssetListRepresentation" class is deprecated, use "ComplexAssetListRepresentation" instead',stacklevel=2)
		super(ComplexAssetListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
