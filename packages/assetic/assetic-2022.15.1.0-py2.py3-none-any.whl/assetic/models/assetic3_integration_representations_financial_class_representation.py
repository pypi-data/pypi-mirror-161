from assetic.models.financial_class_representation import FinancialClassRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsFinancialClassRepresentation(FinancialClassRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFinancialClassRepresentation" class is deprecated, use "FinancialClassRepresentation" instead',stacklevel=2)
		super(FinancialClassRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
