from assetic.models.requestor_physical_location import RequestorPhysicalLocation
import warnings
import six
class Assetic3IntegrationRepresentationsRequestorPhysicalLocation(RequestorPhysicalLocation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRequestorPhysicalLocation" class is deprecated, use "RequestorPhysicalLocation" instead',stacklevel=2)
		super(RequestorPhysicalLocation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
