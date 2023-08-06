from assetic.models.db_geography_well_known_value import DbGeographyWellKnownValue
import warnings
import six
class SystemDataEntitySpatialDbGeographyWellKnownValue(DbGeographyWellKnownValue):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemDataEntitySpatialDbGeographyWellKnownValue" class is deprecated, use "DbGeographyWellKnownValue" instead',stacklevel=2)
		super(DbGeographyWellKnownValue, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
