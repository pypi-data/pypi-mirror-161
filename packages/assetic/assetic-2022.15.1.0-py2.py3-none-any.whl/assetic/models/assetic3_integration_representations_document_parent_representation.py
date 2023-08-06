from assetic.models.document_parent_representation import DocumentParentRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentParentRepresentation(DocumentParentRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentParentRepresentation" class is deprecated, use "DocumentParentRepresentation" instead',stacklevel=2)
		super(DocumentParentRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
