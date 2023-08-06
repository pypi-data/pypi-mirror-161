from assetic.models.document_asmt_representation import DocumentAsmtRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentAsmtRepresentation(DocumentAsmtRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentAsmtRepresentation" class is deprecated, use "DocumentAsmtRepresentation" instead',stacklevel=2)
		super(DocumentAsmtRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
