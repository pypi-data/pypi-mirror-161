from assetic.models.method_info import MethodInfo
import warnings
import six
class SystemReflectionMethodInfo(MethodInfo):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionMethodInfo" class is deprecated, use "MethodInfo" instead',stacklevel=2)
		super(MethodInfo, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
