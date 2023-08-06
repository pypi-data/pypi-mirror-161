from assetic.models.curies_link import CuriesLink
import warnings
import six
class WebApiHalCuriesLink(CuriesLink):
	def __init__(self, **kwargs):
		warnings.warn('The "WebApiHalCuriesLink" class is deprecated, use "CuriesLink" instead',stacklevel=2)
		super(CuriesLink, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
