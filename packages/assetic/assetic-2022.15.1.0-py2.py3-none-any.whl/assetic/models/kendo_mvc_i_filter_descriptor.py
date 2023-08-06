from assetic.models.i_filter_descriptor import IFilterDescriptor
import warnings
import six
class KendoMvcIFilterDescriptor(IFilterDescriptor):
	def __init__(self, **kwargs):
		warnings.warn('The "KendoMvcIFilterDescriptor" class is deprecated, use "IFilterDescriptor" instead',stacklevel=2)
		super(IFilterDescriptor, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
