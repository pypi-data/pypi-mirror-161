from assetic.models.financial_class_list_representation import FinancialClassListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsFinancialClassListRepresentation(FinancialClassListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFinancialClassListRepresentation" class is deprecated, use "FinancialClassListRepresentation" instead',stacklevel=2)
		super(FinancialClassListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
