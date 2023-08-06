from assetic.models.client_handler_descriptor import ClientHandlerDescriptor
import warnings
import six
class KendoMvcClientHandlerDescriptor(ClientHandlerDescriptor):
	def __init__(self, **kwargs):
		warnings.warn('The "KendoMvcClientHandlerDescriptor" class is deprecated, use "ClientHandlerDescriptor" instead',stacklevel=2)
		super(ClientHandlerDescriptor, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
