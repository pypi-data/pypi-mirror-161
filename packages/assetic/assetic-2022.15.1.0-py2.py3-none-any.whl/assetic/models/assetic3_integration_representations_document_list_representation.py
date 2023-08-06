from assetic.models.document_list_representation import DocumentListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentListRepresentation(DocumentListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentListRepresentation" class is deprecated, use "DocumentListRepresentation" instead',stacklevel=2)
		super(DocumentListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
