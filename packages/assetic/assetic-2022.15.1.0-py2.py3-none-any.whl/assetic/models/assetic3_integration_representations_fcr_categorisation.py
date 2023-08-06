from assetic.models.fcr_categorisation import FCRCategorisation
import warnings
import six
class Assetic3IntegrationRepresentationsFCRCategorisation(FCRCategorisation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFCRCategorisation" class is deprecated, use "FCRCategorisation" instead',stacklevel=2)
		super(FCRCategorisation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
