from assetic.models.member_info import MemberInfo
import warnings
import six
class SystemReflectionMemberInfo(MemberInfo):
	def __init__(self, **kwargs):
		warnings.warn('The "SystemReflectionMemberInfo" class is deprecated, use "MemberInfo" instead',stacklevel=2)
		super(MemberInfo, self).__init__()
		for attr, _ in six.iteritems(self.swagger_types):
			val = None
			if attr in kwargs:
				val = kwargs[attr]
			setattr(self, "_" + attr, val) 
