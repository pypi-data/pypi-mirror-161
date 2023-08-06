from assetic.models.application_create_ticket_representation import ApplicationCreateTicketRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsApplicationCreateTicketRepresentation(ApplicationCreateTicketRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsApplicationCreateTicketRepresentation" class is deprecated, use "ApplicationCreateTicketRepresentation" instead',stacklevel=2)
		super(ApplicationCreateTicketRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
