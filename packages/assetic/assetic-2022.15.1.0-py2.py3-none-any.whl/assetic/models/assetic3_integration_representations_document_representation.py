from assetic.models.document_representation import DocumentRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentRepresentation(DocumentRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentRepresentation" class is deprecated, use "DocumentRepresentation" instead',stacklevel=2)
		super(DocumentRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
