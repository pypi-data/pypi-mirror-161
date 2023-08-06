# coding: utf-8
from __future__ import absolute_import

import os
import sys
import xml.dom.minidom

from assetic.tools.functional_location_tools import FunctionalLocationTools
from assetic.tools.shared.messager_base import MessagerBase

from .wko_config_repr import WkoConfigRepresentation

try:
    import pythonaddins
except ImportError:
    # ArcGIS Pro doesn't have this library
    pass

from typing import List, Any
import assetic
import six

try:
    import arcpy
except ImportError:
    pass

from .calculation_tools import CalculationTools


class XMLConfigReader(object):

    def __init__(self, messager, xmlfile, sdk):

        self.messager = messager
        self._xml_file = xmlfile

        self._assetlayerconfig = None
        self._loglevel = None
        self._logfile = None
        self._buttonconfig = {}
        self._bulk_threshold = None
        self._calculations_plugin = None

        self.xmlwkos = None
        self.xmlassets = None
        self.xmlfcnlocation = None
        self._buttonconfig = None

        self._assetlayerconfig = None
        self._fcnlayerconfig = None

        # initialise common tools so can use messaging method
        self.commontools = messager  # type: MessagerBase

        ##initalise settings by reading file and getting config
        self.init_xml()

        self._layerconfig = None

        self._is_valid_config = True

        self._assetconfig = None
        if not self.assetconfig:
            self._is_valid_config = False
        else:
            self._assetconfig = self.assetconfig
            self._is_valid_config = True
        self.asseticsdk = sdk  # todo

        # instantiate assetic.AssetTools
        self.assettools = assetic.AssetTools(self.asseticsdk.client)

        # get logfile name to help user find it
        self.logfilename = ""
        for h in self.asseticsdk.logger.handlers:
            try:
                self.logfilename = h.baseFilename
            except:
                pass

        # self.odata = assetic.tools.odata.OData()
        # self._layerconfig = None

        self.fltools = FunctionalLocationTools(self.asseticsdk.client)
        self.gis_tools = assetic.tools.GISTools(self._layerconfig, self.asseticsdk.client)

        if self.calculations_plugin:
            try:
                global_namespace = {
                    "__file__": __file__,
                    "__name__": "custom",
                }
                exec(compile(open(self.calculations_plugin,
                                  "rb").read(),
                             self.calculations_plugin,
                             'exec'), global_namespace)
            except Exception as ex:
                self.asseticsdk.logger.error(str(ex))
                self._calc_tools = CalculationTools()
            else:
                try:
                    self._calc_tools = global_namespace["FieldCalculations"]()
                except Exception as ex:
                    self.asseticsdk.logger.error(str(ex))
                    self._calc_tools = CalculationTools()
        else:
            self._calc_tools = CalculationTools()

        self._gis_type = None

    @property
    def gis_type(self):
        """
        Checks sys.modules to see which GIS library is installed,
        then sets it as an instance variable.

        Useful, as differences exist between QGIS and ArcPy when
        interacting with layers, e.g. lyr.name (arcpy) vs lyr.name()
        (qgis)
        """

        if self._gis_type is None:
            if "arcpy" in sys.modules:
                self._gis_type = "arcpy"
            elif "qgis" in sys.modules:
                self._gis_type = "qgis"
            elif "osgeo" in sys.modules:
                self._gis_type = "mapinfo"

        return self._gis_type

    @property
    def fcnlayerconfig(self):
        return self._fcnlayerconfig

    @property
    def assetconfig(self):
        return self._assetlayerconfig

    @property
    def buttonconfig(self):
        return self._buttonconfig

    @property
    def loglevel(self):
        return self._loglevel

    @property
    def logfile(self):
        return self._logfile

    @property
    def calculations_plugin(self):
        return self._calculations_plugin

    @property
    def is_valid_config(self):
        # type: () -> bool
        """
        Asset Layer Configuration
        Cache the XML content so that we don't continually reload it as we
        access it in _get_cat_config
        :return:
        """
        return self._is_valid_config

    @property
    def layerconfig(self):
        # type: () -> Any
        """
        Asset Layer Configuration
        Cache the XML content so that we don't continually reload it as we
        access it in _get_cat_config
        :return:
        """
        if self._layerconfig is None:
            self._layerconfig = self.get_asset_config_for_layers()

        return self._layerconfig

    @property
    def fl_layerconfig(self):
        # type: () -> dict
        """
        Functional Location Layer configuration
        Cache the XML content so that we don't continually reload it
        :return:
        """
        return self.fcnlayerconfig

    @property
    def bulk_threshold(self):
        """Gets the minimum threshold before bulk operation applied.
        :return: The integer to set for minimum threshold
        :rtype: int
        """
        return self._bulk_threshold

    @bulk_threshold.setter
    def bulk_threshold(self, value):
        """Sets the minimum threshold before bulk operation applied.
        :param value: The integer to set for minimum threshold
        :type: int
        """
        self._bulk_threshold = value

    def init_xml(self):
        """
        Read the XML configuration file into separate dom objects for assets and
        work orders
        """
        # Open XML config document using minidom parser
        DOMTree = xml.dom.minidom.parse(self._xml_file)
        collection = DOMTree.documentElement

        # get logfile and debug info
        loglevel = collection.getElementsByTagName("loglevel")
        self._loglevel = None
        if len(loglevel) > 0 and len(loglevel[0].childNodes) > 0:
            self._loglevel = str(loglevel[0].childNodes[0].data)

        self._logfile = None
        logfile = collection.getElementsByTagName("logfile")
        if len(logfile) > 0 and len(logfile[0].childNodes) > 0:
            self._logfile = str(logfile[0].childNodes[0].data)
            if not os.path.isdir(os.path.dirname(self._logfile)):
                # folder for log file not correct
                self.commontools.new_message(
                    "log file directory not found for: {0}".format(
                        self._logfile))
                self._logfile = None

        self._bulk_threshold = None
        bulk_threshold = collection.getElementsByTagName("bulk_threshold")
        if len(bulk_threshold) > 0 and len(bulk_threshold[0].childNodes) > 0:
            xml_bulk_threshold = int(bulk_threshold[0].childNodes[0].data)
            try:
                self._bulk_threshold = int(xml_bulk_threshold)
            except ValueError:
                # needs to be an int
                self.commontools.new_message(
                    "bulk_threshold setting must be an integer: {0}".format(
                        xml_bulk_threshold))
                self._bulk_threshold = None

        # Get all the wko and asset elements in the collection
        operations = collection.getElementsByTagName("operation")
        for operation in operations:
            if operation.getAttribute("action") == "Create Work Order":
                self.xmlwkos = operation.getElementsByTagName("layer")
            elif operation.getAttribute("action") == "Asset":
                self.xmlassets = operation.getElementsByTagName("layer")
            elif operation.getAttribute("action") == "Functional Location":
                self.xmlfcnlocation = operation.getElementsByTagName(
                    "layer")
            elif operation.getAttribute("action") == "Buttons":
                self._buttonconfig = self.get_button_action_config(operation)

        # get custom calculations plugin if set
        self._calculations_plugin = None
        plugin = collection.getElementsByTagName("calculations_file")
        if len(plugin) > 0 and len(plugin[0].childNodes) > 0:
            if os.path.isfile(str(plugin[0].childNodes[0].data)):
                self._calculations_plugin = str(plugin[0].childNodes[0].data)
            else:
                self.commontools.new_message(
                    "Calculations plugin file {0} not found".format(
                        str(plugin[0].childNodes[0].data)))

        # convert xml to list of dictionaries
        self._assetlayerconfig = self.get_asset_config_for_layers()
        self._fcnlayerconfig = self.get_functional_location_config_for_layers()

    def get_asset_config_for_layers(self):
        """
        From the XML configuration get the field names in the layers and the
        corresponding assetic field names
        :return: a list of dictionaries of assetic category to field name
        """
        allconfig = list()

        if not self.xmlassets:
            return allconfig

        for xmlasset in self.xmlassets:
            if xmlasset.hasAttribute("name"):
                lyr_config = {}
                coredict = {}
                attrdict = {}
                coredefsdict = {}
                attsdefsdict = {}
                addrdict = {}
                addrdefaultsdict = {}
                componentlist = list()
                funclocdict = {}
                calculationslist = list()

                lyr_config["layer"] = xmlasset.getAttribute("name")
                if lyr_config["layer"] is None:
                    msg = "Expecting tag <layer> in XML configuration"
                    self.commontools.new_message(msg)
                    return None

                assetcat = None
                if xmlasset.getElementsByTagName("category") and \
                    len(xmlasset.getElementsByTagName("category")) > 0 \
                    and len(xmlasset.getElementsByTagName("category")[ \
                                    0].childNodes) > 0:
                    assetcat = str(xmlasset.getElementsByTagName("category")[0].childNodes[0].data)
                if assetcat is None:
                    msg = "Asset Category for layer {0} not configured.\n" \
                          "Expecting tag <category>".format(lyr_config["layer"])
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.error(msg)
                    return None
                lyr_config["asset_category"] = assetcat

                # get core field mappings with layer fields
                for core in xmlasset.getElementsByTagName("corefields"):
                    for corefields in core.childNodes:
                        if corefields.nodeType == 1 \
                                and len(corefields.childNodes) > 0:
                            coredict[str(corefields.nodeName)] = str(corefields.childNodes[0].data)
                # check that we have either 'id' or 'asset_id' as minimum
                if "id" not in coredict and "asset_id" not in coredict:
                    msg = "Asset GUID and Asset ID for layer {0} not " \
                          "configured.\n" \
                          "Expecting tag <id> or <asset_id>, or both".format(
                        lyr_config["layer"])
                    self.commontools.new_message(msg)
                    return None
                # get attribute field mappings with layer fields
                for atts in xmlasset.getElementsByTagName("attributefields"):
                    for attflds in atts.childNodes:
                        if attflds.nodeType == 1 \
                                and len(attflds.childNodes) > 0:
                            attrdict[str(attflds.nodeName)] = str(attflds.childNodes[0].data)
                # get core field default value (where no layer field)
                for core in xmlasset.getElementsByTagName("coredefaults"):
                    for coredefaults in core.childNodes:
                        if coredefaults.nodeType == 1 and \
                                len(coredefaults.childNodes) > 0:
                            coredefsdict[str(coredefaults.nodeName)] = str(coredefaults.childNodes[0].data)
                # get attribute field default value (where no layer field)
                for atts in xmlasset.getElementsByTagName("attributedefaults"):
                    for attdefaults in atts.childNodes:
                        if attdefaults.nodeType == 1 and \
                                len(attdefaults.childNodes) > 0:
                            attsdefsdict[str(attdefaults.nodeName)] = str(attdefaults.childNodes[0].data)

                # get functional location fields
                for atts in xmlasset.getElementsByTagName("functional_location"):
                    for att in atts.childNodes:
                        if att.nodeType == 1 and len(att.childNodes) > 0:
                            funclocdict[str(att.nodeName)] = str(att.childNodes[0].data)

                # get component fields
                for component in xmlasset.getElementsByTagName("component"):
                    componentdict = {
                        "attributes": dict()
                        , "defaults": dict()
                        , "dimensions": list()
                    }
                    # get fields that map to layer attributes
                    for comp in component.getElementsByTagName(
                            "componentfields"):
                        for compfld in comp.childNodes:
                            if compfld.nodeType == 1:
                                if len(compfld.childNodes) > 0:
                                    componentdict["attributes"][
                                        str(compfld.nodeName)] = str(
                                        compfld.childNodes[0].data)
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for component "
                                        "{0} tag {1}".format(
                                            component.getAttribute("name")
                                            , str(compfld.nodeName))
                                    )
                    # get component default value (where no layer field)
                    for compdefs in component.getElementsByTagName(
                            "componentdefaults"):
                        for compdefault in compdefs.childNodes:
                            if compdefault.nodeType == 1:
                                if len(compdefault.childNodes) > 0:
                                    componentdict["defaults"][
                                        str(compdefault.nodeName)] = str(
                                        compdefault.childNodes[0].data)
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for component "
                                        "{0} default value tag {1}".format(
                                            component.getAttribute("name")
                                            , str(compdefault.nodeName))
                                    )
                    dimension_xml = component.getElementsByTagName("dimension")
                    if dimension_xml:
                        componentdict["dimensions"] = self.get_dimension_config(
                            dimension_xml)

                    # add component setting to list of components
                    if len(componentdict["defaults"]) > 0 or \
                            len(componentdict["attributes"]) > 0:
                        componentlist.append(componentdict)

                # get address fields
                for addr in xmlasset.getElementsByTagName("addressfields"):
                    for addrfld in addr.childNodes:
                        if addrfld.nodeType == 1 and \
                            len(addrfld.childNodes) > 0:
                            addrdict[str(addrfld.nodeName)] = \
                                str(addrfld.childNodes[0].data)
                # get address default value (where no layer field)
                for addrdefs in \
                        xmlasset.getElementsByTagName("addressdefaults"):
                    for addrdefault in addrdefs.childNodes:
                        if addrdefault.nodeType == 1 \
                                and len(addrdefault.childNodes) > 0:
                            addrdefaultsdict[str(addrdefault.nodeName)] = \
                                str(addrdefault.childNodes[0].data)
                # upload spatial?
                spatial = None
                uploadtagchk = xmlasset.getElementsByTagName(
                    "upload_feature")
                if uploadtagchk and len(uploadtagchk) > 0:
                    spatial = xmlasset.getElementsByTagName(
                        "upload_feature")[0].childNodes[0].data.upper() == 'TRUE'

                if not spatial or not isinstance(spatial, bool):
                    spatial = False
                    # if len(addrdict) > 0 or len(addrdefaultsdict) > 0:
                    #     msg = """Tag <upload_feature> in XML configuration
                    #             must be set to 'True' if defining fields for the
                    #             tags <addressfields> or <addressdefaults>.
                    #             Will assume <upload_feature>=True and continue"""
                    #     self.commontools.new_message(msg)
                    #     spatial = True
                status_cfg = "Active"
                status_chk = xmlasset.getElementsByTagName("creation_status")
                if status_chk and len(status_chk) > 0:
                    try:
                        status_cfg = xmlasset.getElementsByTagName(
                            "creation_status")[0].childNodes[0].data
                    except:
                        pass
                if status_cfg in ["Active", "Proposed", "Notional Asset"]:
                    status = status_cfg
                else:
                    status = "Active"
                    self.commontools.new_message(
                        "Status to use on asset creation not set correctly in "
                        "tag <creation_status>.\nCurrent setting is '{0}', use"
                        "one of 'Active', 'Proposed', 'Notional Asset'."
                        "\nDefaulting to status 'Active'".format(status_cfg))

                lookup_cfg = False
                lookup_chk = xmlasset.getElementsByTagName("resolve_lookups")
                if lookup_chk and len(lookup_chk) > 0:
                    try:
                        lookup_cfg = xmlasset.getElementsByTagName(
                            "resolve_lookups")[0].childNodes[0].data
                    except:
                        pass
                if isinstance(lookup_cfg, bool) or lookup_cfg.upper() == "TRUE":
                    lookup = bool(lookup_cfg)
                else:
                    lookup = False
                    self.commontools.new_message(
                        "resolve_lookups to use on domain lookup not set "
                        "correctly in "
                        "tag <resolve_lookups>.\nCurrent setting is '{0}', use"
                        "one of True or False."
                        "\nDefaulting to status 'False'".format(lookup_cfg))

                # get configuration for custom calculations to apply
                for calculation in xmlasset.getElementsByTagName(
                        "calculation"):
                    calculationdict = {
                        "input_fields": list()
                        , "output_field": None
                        , "calculation_tool": None
                    }
                    # get input fields that map to layer attributes
                    for input_field in calculation.getElementsByTagName(
                            "input_fields"):
                        for input_fld in input_field.childNodes:
                            if input_fld.nodeType == 1:
                                if len(input_fld.childNodes) > 0:
                                    calculationdict["input_fields"].append(
                                        str(input_fld.childNodes[0].data))
                                else:
                                    self.commontools.new_message(
                                        "No value supplied for calculation "
                                        "{0} tag {1}".format(
                                            calculation.getAttribute("name")
                                            , str(input_fld.nodeName))
                                    )
                    # get output field name
                    # get core field default value (where no layer field)
                    for calc_cfg in calculation.childNodes:
                        if calc_cfg.nodeType == 1 and \
                                str(calc_cfg.nodeName) != "input_fields":
                            calculationdict[str(calc_cfg.nodeName)] = \
                                str(calc_cfg.childNodes[0].data)

                    if len(calculationdict["input_fields"]) > 0 and \
                            calculationdict["output_field"] and \
                            calculationdict["calculation_tool"]:
                        calculationslist.append(calculationdict)
                    else:
                        self.commontools.new_message(
                            "Configuration for {0} calculation fields "
                            "incomplete".format(lyr_config["layer"]))

                lyr_config["upload_feature"] = spatial
                lyr_config["creation_status"] = status
                lyr_config["resolve_lookups"] = lookup

                lyr_config["corefields"] = coredict
                lyr_config["attributefields"] = attrdict
                lyr_config["coredefaults"] = coredefsdict
                lyr_config["attributedefaults"] = attsdefsdict
                lyr_config["addressfields"] = addrdict
                lyr_config["addressdefaults"] = addrdefaultsdict
                lyr_config["components"] = componentlist
                lyr_config['functionallocation'] = funclocdict
                lyr_config['calculations'] = calculationslist

                allconfig.append(lyr_config)

        # if coreitems !=None:
        #    for corefields in coreitems.childNodes:
        #        if corefields.nodeType == 1:
        #            fields.append(str(corefields.childNodes[0].data))
        #            fielddict[str(corefields.nodeName)] = str(corefields.childNodes[0].data)
        return allconfig

    def get_dimension_config(self, dimension_xml):
        """
        From the XML configuration dimension node get the dimension defaults
        :param dimension_xml: the dimension xml node which is defined within
        a component.  There may be one of more dimension settings
        :return: list of dict with dimension attributes and defaults
        """
        dimension_list = list()
        for dimension in dimension_xml:
            dimension_dict = {
                "attributes": dict()
                , "defaults": dict()
            }
            # get dimension fields that map to layer attributes
            for dim in dimension.getElementsByTagName("dimensionfields"):
                for dim_fld in dim.childNodes:
                    if dim_fld.nodeType == 1:
                        if len(dim_fld.childNodes) > 0:
                            dimension_dict["attributes"][
                                str(dim_fld.nodeName)] = str(
                                dim_fld.childNodes[0].data)
                        else:
                            self.commontools.new_message(
                                "No value supplied for dimension "
                                "{0} tag {1}".format(
                                    dim.getAttribute("name")
                                    , str(dim_fld.nodeName))
                            )
            # get dimension default value (where no layer field)
            for dim in dimension.getElementsByTagName("dimensiondefaults"):
                for dim_def in dim.childNodes:
                    if dim_def.nodeType == 1:
                        if len(dim_def.childNodes) > 0:
                            dimension_dict["defaults"][
                                str(dim_def.nodeName)] = str(
                                dim_def.childNodes[0].data)
                        else:
                            self.commontools.new_message(
                                "No value supplied for dimension "
                                "{0} default value tag {1}".format(
                                    dim.getAttribute("name")
                                    , str(dim_def.nodeName))
                            )
            if dimension_dict["attributes"] or dimension_dict["defaults"]:
                dimension_list.append(dimension_dict)
        return dimension_list

    def get_functional_location_config_for_layers(self):
        """
        Configuration for Functional Location creation/update
        From the XML configuration get the field names in the layers and the
        corresponding assetic field names
        :return: a list of dictionaries of assetic category to field name
        """
        allconfig = list()

        if not self.xmlfcnlocation:
            return allconfig

        for xmlfcnloc in self.xmlfcnlocation:
            if xmlfcnloc.hasAttribute("name"):
                lyr_config = dict()

                lyr_config["layer"] = xmlfcnloc.getAttribute("name")

                lyr_config["fl_corefields"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_corefields")
                lyr_config["fl_coredefaults"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_coredefaults")
                lyr_config["fl_attributefields"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_attributefields")
                lyr_config["fl_attributedefaults"] = self.get_dict_for_tag(
                    xmlfcnloc, "fl_attributedefaults")

                # check that we have either 'id' or 'asset_id' as minimum
                valid_config = True
                if "id" not in lyr_config["fl_corefields"] and \
                        "functional_location_id" not in \
                        lyr_config["fl_corefields"]:
                    msg = "Functional Location GUID and Functional Location " \
                          "ID for layer {0} not configured.\nExpecting tag " \
                          "<id> or <functional_location_id>, or both".format(
                        lyr_config["layer"])
                    self.commontools.new_message(msg)
                    return None
                if "functional_location_type" not in \
                        lyr_config["fl_corefields"] and \
                        "functional_location_type" not in \
                        lyr_config["fl_coredefaults"]:
                    self.commontools.new_message(
                        "<functional_location_type> must be defined as a core "
                        "field or core default field for functional "
                        "location layer {0}".format(lyr_config["layer"]))

                lookup_cfg = False
                lookup_chk = self.get_dict_for_tag(
                    xmlfcnloc, "resolve_lookups")
                if lookup_chk and len(lookup_chk) > 0:
                    try:
                        lookup_cfg = lookup_chk["resolve_lookups"]
                    except:
                        pass
                if isinstance(lookup_cfg, bool) or lookup_cfg.upper() == "TRUE":
                    lookup = bool(lookup_cfg)
                else:
                    lookup = False
                    self.commontools.new_message(
                        "resolve_lookups to use on domain lookup not set "
                        "correctly in "
                        "tag <resolve_lookups>.\nCurrent setting is '{0}', use"
                        "one of True or False."
                        "\nDefaulting to status 'False'".format(lookup_cfg))
                lyr_config["resolve_lookups"] = lookup

                if valid_config:
                    allconfig.append(lyr_config)

        return allconfig

    @staticmethod
    def get_dict_for_tag(element, tag):
        # type: (xml.dom.minidom.Element, str) -> dict
        """
        For a given element build a dict from the nodes in the element
        :param element: An XML element
        :param tag: the string value of the tag
        :returns: A dict with the mappings defined by the XML nodes in the
        element
        """
        mappings = dict()
        for nodes in element.getElementsByTagName(tag):
            for node in nodes.childNodes:
                if node.nodeType == 1 and len(node.childNodes) > 0:
                    mappings[str(node.nodeName)] = str(node.childNodes[0].data)
        return mappings

    def get_layer_wko_config(self, layername):
        """
        From the XML configuration get the work order defaults
        :param layername: work order layer name to get the config for
        :return: assetic_esri.WkoConfigRepresentation
        and a dictionary of assetic category to arcMap field name
        """
        config = WkoConfigRepresentation()
        for xmlwko in self.xmlwkos:
            if xmlwko.hasAttribute("name") and \
                    xmlwko.getAttribute("name") == layername:
                config.wkoguidfld = xmlwko.getElementsByTagName("guidfield")[0].childNodes[0].data
                config.wkoidfld = xmlwko.getElementsByTagName("friendlyfield")[0].childNodes[0].data
                config.assetidfld = xmlwko.getElementsByTagName("assetidfield")[0].childNodes[0].data
                config.failurecode = xmlwko.getElementsByTagName("failurecode")[0].childNodes[0].data
                config.remedycode = xmlwko.getElementsByTagName("remedycode")[0].childNodes[0].data
                config.causecode = xmlwko.getElementsByTagName("causecode")[0].childNodes[0].data
                # config.resourceid = xmlwko.getElementsByTagName("resourceid")[0].childNodes[0].data
                config.wkotype = xmlwko.getElementsByTagName("wkotypeid")[0].childNodes[0].data
        return config

    def get_button_action_config(self, xmlbuttons):
        button_config = {}
        button_config["but_create"] = False
        button_config["but_update"] = False
        button_config["but_delete"] = False
        button_config["but_show"] = False
        button_config["but_create"] = str(xmlbuttons.getElementsByTagName("create")[0].childNodes[0].data)
        button_config["but_update"] = str(xmlbuttons.getElementsByTagName("update")[0].childNodes[0].data)
        button_config["but_delete"] = str(xmlbuttons.getElementsByTagName("delete")[0].childNodes[0].data)
        button_config["but_show"] = str(xmlbuttons.getElementsByTagName("show")[0].childNodes[0].data)
        return button_config

    def get_fl_layer_config(self, lyr, lyrname, purpose, actuallayerflds):
        # type: (Any, str, str, List[str]) -> (dict, List[str],str)
        """
        Returns the configuration for dedicated functional location
        layer, as well as the fields to be retrieved from the cursor.

        :param lyr: GIS layer
        :param lyrname: name of the layer
        :param purpose:
        :param actuallayerflds: all of the fields contained in the layer
        plus any assetic created spatial fields (e.g. qgis _geometry_length_,
        etc.)
        :return: dict defining config as well as a list of fields
        in the layer
        """

        lyrs = [l for l in self.fcnlayerconfig if l['layer'] == lyrname]

        if len(lyrs) == 0:
            return None, None, None

        lyr_config = lyrs[0]

        if purpose in ["create", "update"]:
            cf = list(six.viewvalues(lyr_config["fl_corefields"]))
            af = list(six.viewvalues(lyr_config['fl_attributefields']))

            fields = cf + af

            missing = []
            for f in fields:
                if f not in actuallayerflds:
                    missing.append(f)

            if len(missing) > 0:
                msg = ("Following fields defined in the XML configuration "
                       "({0}) missing from layer. "
                       "Unable to process.".format(', '.join(missing)))
                self.fltools.logger.error(msg)
                return None, None, None
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            if "id" in lyr_config["fl_corefields"]:
                idfield = lyr_config["fl_corefields"]["id"]
            else:
                if "functional_location_id" in lyr_config["fl_corefields"]:
                    idfield = \
                        lyr_config["fl_corefields"]["functional_location_id"]
                else:
                    msg = "Functional Location ID and/or GUID field " \
                          "must be defined for layer {0}".format(lyrname)
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.warning(msg)
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            msg = "Functional Location ID Field [{0}] is defined in " \
                  "configuration but is not" \
                  " in layer {1}, check logfile for field list" \
                  "".format(idfield, lyr.name)
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(msg)
            msg = "Fields in layer {0} are: {1}".format(
                lyrname, actuallayerflds)
            self.asseticsdk.logger.warning(msg)
            return None, None, None

        return lyr_config, fields, idfield

    def get_layer_config(self, lyr, lyrname, purpose, actuallayerflds):
        """
        For the given layer get the config settings. Depending on purpose not
        all config is required, so only get relevant config
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param lyrname: name of the layer
        :param purpose: one of 'create','update','delete','display'
        :param actuallayerflds: all of the fields contained in the layer
        plus any assetic created spatial fields (e.g. qgis _geometry_length_,
        etc.)
        """

        if not self._assetconfig:
            self.commontools.new_message("No asset configuration available")
            return None, None, None
        lyr_config_list = [
            j for j in self._assetconfig if j["layer"] == lyrname]
        if len(lyr_config_list) == 0:
            if purpose not in ["delete"]:
                if self.gis_type == "qgis":
                    desc_lyrname = lyr.name()
                elif self.gis_type == "mapinfo":
                    desc_lyrname = lyrname
                else:
                    desc_lyrname = lyr.name

                xml_configs = [f["layer"] for f in self._assetconfig]

                msg = ("No configuration for layer '{0}' defined in configuration "
                       "file ({1}). Availble configurations: {2}".format(
                    desc_lyrname, self._xml_file, xml_configs))
                self.commontools.new_message(msg)
            return None, None, None

        lyr_config = lyr_config_list[0]

        if purpose in ["create", "update"]:
            # from config file build list of arcmap fields to query
            fields = list(six.viewvalues(lyr_config["corefields"]))
            if fields is None:
                msg = "missing 'corefields' configuration for layer {0}" \
                      "".format(lyr.name)
                self.commontools.new_message(msg)
                return None, None, None
            if "attributefields" in lyr_config:
                attfields = list(six.viewvalues(lyr_config["attributefields"]))
                if attfields != None:
                    fields = fields + attfields

            for component in lyr_config["components"]:
                compflds = list(six.viewvalues(component["attributes"]))
                if compflds:
                    fields = fields + compflds
                for dimension in component["dimensions"]:
                    dimflds = list(six.viewvalues(dimension["attributes"]))
                    if dimflds:
                        fields = fields + dimflds
            if "addressfields" in lyr_config.keys():
                addrfields = list(six.viewvalues(lyr_config["addressfields"]))
                if addrfields is not None:
                    fields = fields + addrfields
            if "functionallocation" in lyr_config.keys():
                flfields = list(
                    six.viewvalues(lyr_config['functionallocation']))
                if flfields is not None:
                    fields = fields + flfields

            calc_output_fields = list()
            if "calculations" in lyr_config.keys():
                for calculation in lyr_config["calculations"]:
                    calc_inputs = calculation["input_fields"]
                    if calc_inputs:
                        fields = fields + calc_inputs
                    calc_output = calculation['output_field']
                    calc_output_fields.append(calc_output)
                    if calc_output in actuallayerflds:
                        # field exists so include, optional since calc field
                        fields.append(calc_output)
            lyr_config["all_calc_output_fields"] = calc_output_fields

            # check fields from config are in layer
            if fields is not None:
                # create unique list (may not be unique if components or
                # dimensions config use same field for common elements
                fields = list(set(fields))

                # loop through list and check fields are in layer
                missing_fields = []
                for configfield in fields:
                    if configfield not in actuallayerflds and \
                            configfield not in calc_output_fields:
                        missing_fields.append(configfield)

                if len(missing_fields) > 0:
                    msg = "Fields [{0}] is defined in configuration but is " \
                          "not in layer {1}, check logfile for field list" \
                          "".format(', '.join(missing_fields), lyrname)
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.warning(msg)
                    msg = "Fields in layer {0} are: {1}".format(
                        lyrname, actuallayerflds)
                    self.asseticsdk.logger.warning(msg)
                    return None, None, None

                # remove any calc fields from the list
                fields[:] = [x for x in fields if x in actuallayerflds]
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            assetid = None
            if "id" in lyr_config["corefields"]:
                idfield = lyr_config["corefields"]["id"]
            else:
                if "asset_id" in lyr_config["corefields"]:
                    idfield = lyr_config["corefields"]["asset_id"]
                else:
                    msg = "Asset ID and/or Asset GUID field must be defined " \
                          "for layer {0}".format(lyr.name)
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.warning(msg)
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            msg = "Asset ID Field [{0}] is defined in configuration but is not" \
                  " in layer {1}, check logfile for field list".format(
                idfield, lyr.name)
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(msg)
            msg = "Fields in layer {0} are: {1}".format(
                lyr.name, actuallayerflds)
            self.asseticsdk.logger.warning(msg)
            return None, None, None

        return lyr_config, fields, idfield

    def get_fl_layer_fields_dict(self):

        cores = self.layerconfig['fl_corefields']
        coredefs = self.layerconfig['fl_coredefaults']

        layer_dict = {
            'id': cores['id'],
            'functional_location_id': cores['functional_location_id'],
            'functional_location_name': cores['functional_location_name'],
            'functional_location_type': coredefs['functional_location_type'],
        }

        return layer_dict

    def get_layer_asset_guid(self, assetid, lyr_config):
        """
        Get the asset guid for an asset.  Used where "id" is not in the
        configuration.  If it is then it is assumed the assetid is a guid
        :param assetid: The assetid - may be guid or friendly
        :param lyr_config: the layer
        :returns: guid or none
        """
        # alias core fields object for readability
        corefields = lyr_config["corefields"]
        if "id" not in corefields:
            ##must be using asset_id (friendly).  Need to get guid
            asset = self.assettools.get_asset(assetid)
            if asset is not None:
                assetid = asset["Id"]
            else:
                msg = "Asset with ID [{0}] not found in Assetic".format(
                    assetid)
                self.asseticsdk.logger.warning(msg)
                return None
        return assetid
