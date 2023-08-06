from assetic.models.search_representation_list import SearchRepresentationList
import warnings
import six
class Assetic3IntegrationRepresentationsSearchRepresentationList(SearchRepresentationList):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsSearchRepresentationList" class is deprecated, use "SearchRepresentationList" instead',stacklevel=2)
		super(SearchRepresentationList, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
