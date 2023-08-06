from assetic.models.form_widget_representation import FormWidgetRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormWidgetRepresentation(FormWidgetRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormWidgetRepresentation" class is deprecated, use "FormWidgetRepresentation" instead',stacklevel=2)
		super(FormWidgetRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
