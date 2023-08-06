from assetic.models.document_work_request_representation import DocumentWorkRequestRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentWorkRequestRepresentation(DocumentWorkRequestRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentWorkRequestRepresentation" class is deprecated, use "DocumentWorkRequestRepresentation" instead',stacklevel=2)
		super(DocumentWorkRequestRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
