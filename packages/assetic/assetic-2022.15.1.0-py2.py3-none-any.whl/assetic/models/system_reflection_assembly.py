from assetic.models.assembly import Assembly
import warnings
import six
class SystemReflectionAssembly(Assembly):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionAssembly" class is deprecated, use "Assembly" instead',stacklevel=2)
		super(Assembly, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
