from assetic.models.get_request_params import GetRequestParams
import warnings
import six
class Assetic3HelpersGetRequestParams(GetRequestParams):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3HelpersGetRequestParams" class is deprecated, use "GetRequestParams" instead',stacklevel=2)
		super(GetRequestParams, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
