from assetic.models.claim_type_representation import ClaimTypeRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsClaimTypeRepresentation(ClaimTypeRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsClaimTypeRepresentation" class is deprecated, use "ClaimTypeRepresentation" instead',stacklevel=2)
		super(ClaimTypeRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
