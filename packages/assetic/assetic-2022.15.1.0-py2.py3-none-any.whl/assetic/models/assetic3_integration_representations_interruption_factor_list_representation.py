from assetic.models.interruption_factor_list_representation import InterruptionFactorListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsInterruptionFactorListRepresentation(InterruptionFactorListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsInterruptionFactorListRepresentation" class is deprecated, use "InterruptionFactorListRepresentation" instead',stacklevel=2)
		super(InterruptionFactorListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
