from assetic.models.i_resource import IResource
import warnings
import six
class WebApiHalInterfacesIResource(IResource):
	def __init__(self, **kwargs):
		warnings.warn('The "WebApiHalInterfacesIResource" class is deprecated, use "IResource" instead',stacklevel=2)
		super(IResource, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
