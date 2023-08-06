from assetic.models.db_geography import DbGeography
import warnings
import six
class SystemDataEntitySpatialDbGeography(DbGeography):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemDataEntitySpatialDbGeography" class is deprecated, use "DbGeography" instead',stacklevel=2)
		super(DbGeography, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
