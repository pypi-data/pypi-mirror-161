from assetic.models.document_asset_representation import DocumentAssetRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentAssetRepresentation(DocumentAssetRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentAssetRepresentation" class is deprecated, use "DocumentAssetRepresentation" instead',stacklevel=2)
		super(DocumentAssetRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
