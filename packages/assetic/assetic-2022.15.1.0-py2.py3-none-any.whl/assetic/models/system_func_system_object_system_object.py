from assetic.models.func_object_object import FuncObjectObject
import warnings
import six
class SystemFuncSystemObjectSystemObject(FuncObjectObject):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemFuncSystemObjectSystemObject" class is deprecated, use "FuncObjectObject" instead',stacklevel=2)
		super(FuncObjectObject, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
