from assetic.models.pagination_request_params import PaginationRequestParams
import warnings
import six
class Assetic3HelpersPaginationRequestParams(PaginationRequestParams):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3HelpersPaginationRequestParams" class is deprecated, use "PaginationRequestParams" instead',stacklevel=2)
		super(PaginationRequestParams, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
