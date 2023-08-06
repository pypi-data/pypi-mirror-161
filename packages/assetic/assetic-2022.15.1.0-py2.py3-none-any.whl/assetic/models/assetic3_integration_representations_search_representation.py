from assetic.models.search_representation import SearchRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsSearchRepresentation(SearchRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsSearchRepresentation" class is deprecated, use "SearchRepresentation" instead',stacklevel=2)
		super(SearchRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
