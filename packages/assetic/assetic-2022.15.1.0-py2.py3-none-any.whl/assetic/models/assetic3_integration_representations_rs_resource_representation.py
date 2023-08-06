from assetic.models.rs_resource_representation import RsResourceRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsRsResourceRepresentation(RsResourceRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsRsResourceRepresentation" class is deprecated, use "RsResourceRepresentation" instead',stacklevel=2)
		super(RsResourceRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
