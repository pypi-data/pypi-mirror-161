from assetic.models.spatial_request_params import SpatialRequestParams
import warnings
import six
class Assetic3HelpersSpatialRequestParams(SpatialRequestParams):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3HelpersSpatialRequestParams" class is deprecated, use "SpatialRequestParams" instead',stacklevel=2)
		super(SpatialRequestParams, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
