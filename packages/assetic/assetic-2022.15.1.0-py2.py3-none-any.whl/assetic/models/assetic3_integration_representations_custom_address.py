from assetic.models.custom_address import CustomAddress
import warnings
import six
class Assetic3IntegrationRepresentationsCustomAddress(CustomAddress):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsCustomAddress" class is deprecated, use "CustomAddress" instead',stacklevel=2)
		super(CustomAddress, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
