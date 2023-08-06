from assetic.models.custom_attribute_typed_argument import CustomAttributeTypedArgument
import warnings
import six
class SystemReflectionCustomAttributeTypedArgument(CustomAttributeTypedArgument):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionCustomAttributeTypedArgument" class is deprecated, use "CustomAttributeTypedArgument" instead',stacklevel=2)
		super(CustomAttributeTypedArgument, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
