from assetic.models.work_request_spatial_location import WorkRequestSpatialLocation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestSpatialLocation(WorkRequestSpatialLocation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestSpatialLocation" class is deprecated, use "WorkRequestSpatialLocation" instead',stacklevel=2)
		super(WorkRequestSpatialLocation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
