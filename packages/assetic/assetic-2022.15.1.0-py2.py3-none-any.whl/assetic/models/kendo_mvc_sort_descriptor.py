from assetic.models.sort_descriptor import SortDescriptor
import warnings
import six
class KendoMvcSortDescriptor(SortDescriptor):
	def __init__(self, **kwargs):
		warnings.warn('The "KendoMvcSortDescriptor" class is deprecated, use "SortDescriptor" instead',stacklevel=2)
		super(SortDescriptor, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
