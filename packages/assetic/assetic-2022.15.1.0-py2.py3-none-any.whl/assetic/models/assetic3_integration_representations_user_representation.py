from assetic.models.user_representation import UserRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsUserRepresentation(UserRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsUserRepresentation" class is deprecated, use "UserRepresentation" instead',stacklevel=2)
		super(UserRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
