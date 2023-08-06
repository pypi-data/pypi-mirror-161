from assetic.models.form_layout_representation import FormLayoutRepresentation
import warnings
import six
class Assetic3IntegrationRepresentationsAssessmentFormFormLayoutRepresentation(FormLayoutRepresentation):
	def __init__(self, **kwargs):
		warnings.warn('The "Assetic3IntegrationRepresentationsAssessmentFormFormLayoutRepresentation" class is deprecated, use "FormLayoutRepresentation" instead',stacklevel=2)
		super(FormLayoutRepresentation, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
