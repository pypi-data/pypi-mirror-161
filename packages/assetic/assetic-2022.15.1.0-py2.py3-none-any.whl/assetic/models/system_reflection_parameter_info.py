from assetic.models.parameter_info import ParameterInfo
import warnings
import six
class SystemReflectionParameterInfo(ParameterInfo):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionParameterInfo" class is deprecated, use "ParameterInfo" instead',stacklevel=2)
		super(ParameterInfo, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
