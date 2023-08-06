from assetic.models.interruption_factor import InterruptionFactor
import warnings
import six
class Assetic3IntegrationRepresentationsInterruptionFactor(InterruptionFactor):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsInterruptionFactor" class is deprecated, use "InterruptionFactor" instead',stacklevel=2)
		super(InterruptionFactor, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
