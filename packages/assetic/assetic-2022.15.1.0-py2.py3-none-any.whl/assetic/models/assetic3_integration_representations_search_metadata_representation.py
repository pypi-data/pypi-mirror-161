from assetic.models.search_metadata_representation import SearchMetadataRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsSearchMetadataRepresentation(SearchMetadataRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsSearchMetadataRepresentation" class is deprecated, use "SearchMetadataRepresentation" instead',stacklevel=2)
		super(SearchMetadataRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
