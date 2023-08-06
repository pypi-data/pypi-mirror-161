from assetic.models.financial_sub_class_representation import FinancialSubClassRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsFinancialSubClassRepresentation(FinancialSubClassRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFinancialSubClassRepresentation" class is deprecated, use "FinancialSubClassRepresentation" instead',stacklevel=2)
		super(FinancialSubClassRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
