from assetic.models.fcr_categorisation_list_representation import FCRCategorisationListRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation(FCRCategorisationListRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The '
					  '"Assetic3IntegrationRepresentationsFCRCategorisationListRepresentation" class is deprecated, use "FCRCategorisationListRepresentation" instead',stacklevel=2)
		super(FCRCategorisationListRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
