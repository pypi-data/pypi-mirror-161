from assetic.models.work_request_physical_location import WorkRequestPhysicalLocation
import warnings
import six
class Assetic3IntegrationRepresentationsWorkRequestPhysicalLocation(WorkRequestPhysicalLocation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsWorkRequestPhysicalLocation" class is deprecated, use "WorkRequestPhysicalLocation" instead',stacklevel=2)
		super(WorkRequestPhysicalLocation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
