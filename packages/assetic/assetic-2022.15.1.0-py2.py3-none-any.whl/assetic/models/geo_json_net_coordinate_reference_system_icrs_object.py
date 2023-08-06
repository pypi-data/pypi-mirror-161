from assetic.models.icrs_object import ICRSObject
import warnings
import six
class GeoJSONNetCoordinateReferenceSystemICRSObject(ICRSObject):
	def __init__(self, **kwargs):
		warnings.warn('The "GeoJSONNetCoordinateReferenceSystemICRSObject" class is deprecated, use "ICRSObject" instead',stacklevel=2)
		super(ICRSObject, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
