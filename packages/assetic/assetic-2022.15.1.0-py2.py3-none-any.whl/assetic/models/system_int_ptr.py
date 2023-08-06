from assetic.models.int_ptr import IntPtr
import warnings
import six
class SystemIntPtr(IntPtr):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemIntPtr" class is deprecated, use "IntPtr" instead',stacklevel=2)
		super(IntPtr, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
