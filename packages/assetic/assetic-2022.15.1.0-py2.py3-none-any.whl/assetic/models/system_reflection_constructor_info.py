from assetic.models.constructor_info import ConstructorInfo
import warnings
import six
class SystemReflectionConstructorInfo(ConstructorInfo):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionConstructorInfo" class is deprecated, use "ConstructorInfo" instead',stacklevel=2)
		super(ConstructorInfo, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
