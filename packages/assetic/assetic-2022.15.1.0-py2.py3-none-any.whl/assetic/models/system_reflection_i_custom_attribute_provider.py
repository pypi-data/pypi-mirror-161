from assetic.models.i_custom_attribute_provider import ICustomAttributeProvider
import warnings
import six
class SystemReflectionICustomAttributeProvider(ICustomAttributeProvider):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionICustomAttributeProvider" class is deprecated, use "ICustomAttributeProvider" instead',stacklevel=2)
		super(ICustomAttributeProvider, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
