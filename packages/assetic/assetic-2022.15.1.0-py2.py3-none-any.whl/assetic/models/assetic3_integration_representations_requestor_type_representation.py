from assetic.models.requestor_type_representation import RequestorTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsRequestorTypeRepresentation(RequestorTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRequestorTypeRepresentation" class is deprecated, use "RequestorTypeRepresentation" instead',stacklevel=2)
		super(RequestorTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
