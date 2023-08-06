import pprint
import six

# --wko config representation-----------------------------------------------
class WkoConfigRepresentation(object):
    """
    Use to hold user configurations for WKO
    """

    def __init__(self, wkoguidfld=None, wkoidfld=None, assetidfld=None
                 , remedycode=None, causecode=None, failurecode=None
                 , resourceid=None, wkotype=None):

        self.fieldtypes = {
            'wkoguidfld': 'str',
            'wkoidfld': 'str',
            'assetidfld': 'str',
            'remedycode': 'int',
            'causecode': 'int',
            'failurecode': 'int',
            'resourceid': 'str',
            'wkotype': 'int'
        }
        self._wkoguidfld = wkoguidfld
        self._wkoidfld = wkoidfld
        self._assetidfld = assetidfld
        self._remedycode = remedycode
        self._causecode = causecode
        self._failurecode = failurecode
        self._resourceid = resourceid
        self._wkotype = wkotype

    @property
    def wkoguidfld(self):
        return self._wkoguidfld

    @wkoguidfld.setter
    def wkoguidfld(self, wkoguidfld):
        self._wkoguidfld = wkoguidfld

    @property
    def wkoidfld(self):
        return self._wkoidfld

    @wkoidfld.setter
    def wkoidfld(self, wkoidfld):
        self._wkoidfld = wkoidfld

    @property
    def assetidfld(self):
        return self._assetidfld

    @assetidfld.setter
    def assetidfld(self, assetidfld):
        self._assetidfld = assetidfld

    @property
    def remedycode(self):
        return self._remedycode

    @remedycode.setter
    def remedycode(self, remedycode):
        self._remedycode = remedycode

    @property
    def causecode(self):
        return self._causecode

    @causecode.setter
    def causecode(self, causecode):
        self._causecode = causecode

    @property
    def failurecode(self):
        return self._failurecode

    @failurecode.setter
    def failurecode(self, failurecode):
        self._failurecode = failurecode

    @property
    def resourceid(self):
        return self._resourceid

    @resourceid.setter
    def resourceid(self, resourceid):
        self._resourceid = resourceid

    @property
    def wkotype(self):
        return self._wkotype

    @wkotype.setter
    def wkotype(self, wkotype):
        self._wkotype = wkotype

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in six.iteritems(self.fieldtypes):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
