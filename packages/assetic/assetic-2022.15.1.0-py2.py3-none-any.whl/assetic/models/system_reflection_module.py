from assetic.models.module import Module
import warnings
import six
class SystemReflectionModule(Module):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionModule" class is deprecated, use "Module" instead',stacklevel=2)
		super(Module, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
