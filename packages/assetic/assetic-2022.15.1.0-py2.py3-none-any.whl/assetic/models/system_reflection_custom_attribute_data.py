from assetic.models.custom_attribute_data import CustomAttributeData
import warnings
import six
class SystemReflectionCustomAttributeData(CustomAttributeData):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionCustomAttributeData" class is deprecated, use "CustomAttributeData" instead',stacklevel=2)
		super(CustomAttributeData, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
