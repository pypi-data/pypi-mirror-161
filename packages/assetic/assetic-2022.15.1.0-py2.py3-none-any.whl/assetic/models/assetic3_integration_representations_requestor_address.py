from assetic.models.requestor_address import RequestorAddress
import warnings
import six
class Assetic3IntegrationRepresentationsRequestorAddress(RequestorAddress):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRequestorAddress" class is deprecated, use "RequestorAddress" instead',stacklevel=2)
		super(RequestorAddress, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
