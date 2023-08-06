from assetic.models.document_thumb_nail_representation import DocumentThumbNailRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentThumbNailRepresentation(DocumentThumbNailRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentThumbNailRepresentation" class is deprecated, use "DocumentThumbNailRepresentation" instead',stacklevel=2)
		super(DocumentThumbNailRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
