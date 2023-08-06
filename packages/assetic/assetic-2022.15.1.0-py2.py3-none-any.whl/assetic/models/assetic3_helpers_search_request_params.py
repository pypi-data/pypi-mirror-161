from assetic.models.search_request_params import SearchRequestParams
import warnings
import six
class Assetic3HelpersSearchRequestParams(SearchRequestParams):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3HelpersSearchRequestParams" class is deprecated, use "SearchRequestParams" instead',stacklevel=2)
		super(SearchRequestParams, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
