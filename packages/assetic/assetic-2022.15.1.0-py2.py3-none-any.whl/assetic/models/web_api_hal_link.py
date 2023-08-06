from assetic.models.link import Link
import warnings
import six
class WebApiHalLink(Link):
	def __init__(self, **kwargs):
		warnings.warn('The "WebApiHalLink" class is deprecated, use "Link" instead',stacklevel=2)
		super(Link, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
