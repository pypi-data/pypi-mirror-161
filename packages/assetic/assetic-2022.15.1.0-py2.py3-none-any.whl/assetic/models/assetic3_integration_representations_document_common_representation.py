from assetic.models.document_common_representation import DocumentCommonRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsDocumentCommonRepresentation(DocumentCommonRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsDocumentCommonRepresentation" class is deprecated, use "DocumentCommonRepresentation" instead',stacklevel=2)
		super(DocumentCommonRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
