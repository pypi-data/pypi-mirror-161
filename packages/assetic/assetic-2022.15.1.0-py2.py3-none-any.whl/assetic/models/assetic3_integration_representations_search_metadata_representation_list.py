from assetic.models.search_metadata_representation_list import SearchMetadataRepresentationList
import warnings
import six
class Assetic3IntegrationRepresentationsSearchMetadataRepresentationList(SearchMetadataRepresentationList):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsSearchMetadataRepresentationList" class is deprecated, use "SearchMetadataRepresentationList" instead',stacklevel=2)
		super(SearchMetadataRepresentationList, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
