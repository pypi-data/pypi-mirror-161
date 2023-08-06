from assetic.models.geo_json_feature_collection import GeoJsonFeatureCollection
import warnings
import six
class Assetic3IntegrationRepresentationsGeoJsonRepresentation(GeoJsonFeatureCollection):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsGeoJsonRepresentation" class is deprecated, use "GeoJsonFeatureCollection" instead',stacklevel=2)
		super(GeoJsonFeatureCollection, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
