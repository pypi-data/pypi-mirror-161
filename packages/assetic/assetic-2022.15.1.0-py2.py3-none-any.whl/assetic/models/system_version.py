from assetic.models.version import Version
import warnings
import six
class SystemVersion(Version):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemVersion" class is deprecated, use "Version" instead',stacklevel=2)
		super(Version, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
