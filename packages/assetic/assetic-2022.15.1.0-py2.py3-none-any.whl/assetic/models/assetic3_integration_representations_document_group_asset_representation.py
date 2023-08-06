from assetic.models.document_group_asset_representation import DocumentGroupAssetRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentGroupAssetRepresentation(DocumentGroupAssetRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentGroupAssetRepresentation" class is deprecated, use "DocumentGroupAssetRepresentation" instead',stacklevel=2)
		super(DocumentGroupAssetRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
