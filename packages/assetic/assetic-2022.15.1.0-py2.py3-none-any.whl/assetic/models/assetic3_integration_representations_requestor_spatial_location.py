from assetic.models.requestor_spatial_location import RequestorSpatialLocation
import warnings
import six
class Assetic3IntegrationRepresentationsRequestorSpatialLocation(RequestorSpatialLocation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRequestorSpatialLocation" class is deprecated, use "RequestorSpatialLocation" instead',stacklevel=2)
		super(RequestorSpatialLocation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
