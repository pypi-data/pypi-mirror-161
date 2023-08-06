from assetic.models.complex_asset_representation import ComplexAssetRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsComplexAssetRepresentation(ComplexAssetRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsComplexAssetRepresentation" class is deprecated, use "ComplexAssetRepresentation" instead',stacklevel=2)
		super(ComplexAssetRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
