from assetic.models.custom_attribute_named_argument import CustomAttributeNamedArgument
import warnings
import six
class SystemReflectionCustomAttributeNamedArgument(CustomAttributeNamedArgument):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionCustomAttributeNamedArgument" class is deprecated, use "CustomAttributeNamedArgument" instead',stacklevel=2)
		super(CustomAttributeNamedArgument, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
