from assetic.models.module_handle import ModuleHandle
import warnings
import six
class SystemModuleHandle(ModuleHandle):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemModuleHandle" class is deprecated, use "ModuleHandle" instead',stacklevel=2)
		super(ModuleHandle, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
