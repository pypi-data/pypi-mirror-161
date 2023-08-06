import abc

import six

from assetic import AsseticSDK
from assetic.tools.shared.xml_config_reader import XMLConfigReader


@six.add_metaclass(abc.ABCMeta)
class ConfigBase:
    """
    A configuration class that accepts all of the customer's
    information and allows it to be accessible by all parts
    of the integration
    """

    def __init__(self, messager, xmlconfigfile, inifile,
                 logfile, loglevelname):
        self.messager = messager
        self.xmlconfigfile = xmlconfigfile
        self.inifile = inifile
        self.logfile = logfile
        self.loglevelname = loglevelname

        self._asseticsdk = None
        self._layerconfig = None

    @property
    def asseticsdk(self):
        if self._asseticsdk is None:
            self._asseticsdk = AsseticSDK(self.inifile, self.logfile, self.loglevelname)

        return self._asseticsdk

    @property
    def layerconfig(self):
        if self._layerconfig is None:
            self._layerconfig = XMLConfigReader(self.messager, self.xmlconfigfile,
                                                self.asseticsdk)

        return self._layerconfig
