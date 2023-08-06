from assetic.models.document_work_order_representation import DocumentWorkOrderRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentWorkOrderRepresentation(DocumentWorkOrderRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentWorkOrderRepresentation" class is deprecated, use "DocumentWorkOrderRepresentation" instead',stacklevel=2)
		super(DocumentWorkOrderRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
