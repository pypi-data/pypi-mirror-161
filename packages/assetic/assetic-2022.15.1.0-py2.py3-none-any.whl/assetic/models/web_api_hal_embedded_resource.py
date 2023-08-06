from assetic.models.embedded_resource import EmbeddedResource
import warnings
import six
class WebApiHalEmbeddedResource(EmbeddedResource):
	def __init__(self, **kwargs):
		warnings.warn('The "WebApiHalEmbeddedResource" class is deprecated, use "EmbeddedResource" instead',stacklevel=2)
		super(EmbeddedResource, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
