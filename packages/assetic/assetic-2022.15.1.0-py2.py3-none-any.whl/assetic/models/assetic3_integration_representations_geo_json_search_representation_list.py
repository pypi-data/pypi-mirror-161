from assetic.models.geo_json_list_feature_collection import GeoJsonListFeatureCollection
import warnings
import six
class Assetic3IntegrationRepresentationsGeoJsonSearchRepresentationList(GeoJsonListFeatureCollection):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsGeoJsonSearchRepresentationList" class is deprecated, use "GeoJsonListFeatureCollection" instead',stacklevel=2)
		super(GeoJsonListFeatureCollection, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
