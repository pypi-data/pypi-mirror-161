from assetic.models.config_unit_type import ConfigUnitType
import warnings
import six
class Assetic3IntegrationRepresentationsConfigUnitType(ConfigUnitType):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsConfigUnitType" class is deprecated, use "ConfigUnitType" instead',stacklevel=2)
		super(ConfigUnitType, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
