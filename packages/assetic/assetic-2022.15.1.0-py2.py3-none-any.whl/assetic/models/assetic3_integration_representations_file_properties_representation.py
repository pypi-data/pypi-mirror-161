from assetic.models.file_properties_representation import FilePropertiesRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsFilePropertiesRepresentation(FilePropertiesRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsFilePropertiesRepresentation" class is deprecated, use "FilePropertiesRepresentation" instead',stacklevel=2)
		super(FilePropertiesRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
