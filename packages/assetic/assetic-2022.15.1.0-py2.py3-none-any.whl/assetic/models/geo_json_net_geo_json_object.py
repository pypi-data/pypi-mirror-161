from assetic.models.geo_json_object import GeoJSONObject
import warnings
import six
class GeoJSONNetGeoJSONObject(GeoJSONObject):
	def __init__(self, **kwargs):
		warnings.warn('The "GeoJSONNetGeoJSONObject" class is deprecated, use "GeoJSONObject" instead',stacklevel=2)
		super(GeoJSONObject, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
