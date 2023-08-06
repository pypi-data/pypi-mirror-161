from assetic.models.runtime_method_handle import RuntimeMethodHandle
import warnings
import six
class SystemRuntimeMethodHandle(RuntimeMethodHandle):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemRuntimeMethodHandle" class is deprecated, use "RuntimeMethodHandle" instead',stacklevel=2)
		super(RuntimeMethodHandle, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
