import pandas as pd

from assetic.tools.static_def import dx_data as dx
from assetic.tools.dx_tools import DataExchangeTools
from assetic.tools.functional_location_tools import FunctionalLocationTools
from .static_def import cust_config_xml_defs
import logging


class GISTools(object):
    def __init__(self, layer_config, api_client=None):

        self.layer_config = layer_config
        self.dxtools = DataExchangeTools(api_client)
        from assetic import AssetTools # todo
        from assetic import OData

        self.asset_tools = AssetTools(api_client)

        self.funcloc_tools = FunctionalLocationTools(api_client)
        self.odata = OData(api_client)

        self._categories = None

        self.logger = logging.getLogger(__name__)

        self._component_list = list()

    @property
    def categories(self):
        # type: () -> dict
        """
        Allows retrieval of cloud category from layer name string
        :return:
        """

        if self._categories is None:
            self._categories = {v: k for k, v in dx.ASSET_VALUES.items()}

        return self._categories

    def bulk_update_assets(self, rows, lyr_name):
        # type: (list, str) -> (int, list)
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update assets. Assumes that each asset already exists.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param lyr_name: Name of the GIS layer being processed
        :return: 0 success, else error
        """

        lyr_config = self._get_cat_config(lyr_name)
        # category label is the user friendly Asset Category name
        category_label = lyr_config["asset_category"]

        header_dict = self.get_asset_client_to_label_dict(lyr_name)
        # cloud_cat is the internal name of the Asset Category
        if category_label in dx.ASSET_VALUES:
            cloud_cat = dx.ASSET_VALUES[category_label]
        else:
            self.logger.error("Category '{0}' is invalid for layer {0}".format(
                category_label, lyr_name))
            return 1, list()

        # get the default, static values to append
        default_asset_values = self.get_asset_label_default_dict(
            lyr_name)

        # get list of asset ID's and use to get the status of the asset
        assets_list = [r[header_dict["Asset Id"]] for r in rows]
        assets_status_list = self.asset_tools.get_assets_status(
                assets=assets_list, is_guid=False)

        # convert to str() to allow comparison for strings and ints
        assets_status_list = {str(k):v for k, v in assets_status_list.items()}

        # make sure asset exists and is not disposed
        valid_rows = list()
        for row in rows:
            if not str(row[header_dict["Asset Id"]]) in assets_status_list.keys():
                # asset not found.  Don't include in DX as it will create asset
                self.logger.warning(
                    "Asset '{0}' not found, it cannot be updated".format(
                        row[header_dict["Asset Id"]]
                    ))
                continue

            if assets_status_list[str(row[header_dict["Asset Id"]])] == "Disposed":
                # don't try to update a disposed asset
                self.logger.warning(
                    "Asset '{0}' is disposed, it cannot be updated".format(
                        row[header_dict["Asset Id"]]
                    ))
                continue
            valid_rows.append(row)

        csv_repr = self.dxtools.create_asset_csv(
            rows=valid_rows,
            cloud_cat=cloud_cat,
            header_dict=header_dict,
            default_asset_values=default_asset_values
        )

        if len(csv_repr) > 1:
            guid = self.dxtools.bulk_update_assets_via_data_exchange(
                category=category_label, nested_list=csv_repr
            )
            self.logger.info("Data Exchange Asset update: {0}".format(guid))
        return 0, valid_rows

    def bulk_update_addresses(self, rows, layer_name):
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update address information. Assumes that each asset
        already exists.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from the cursor
        :param layer_name: Name of the GIS layer being processed
        :return: None
        """

        # using the header, get the cloud label analogues
        # (only returns values from GIS data that relate to assets)
        header_dict = self.get_addr_client_to_label_dicts(layer_name)

        if len(header_dict) == 0:
            # e.g. there are no address fields defined, return early
            return

        # retrieve the default dict and set the order by which
        # we add default values
        def_val_dict = self.get_addr_default_values(layer_name)

        # get the asset ID column
        asset_col = self.get_asset_column(layer_name)

        csv_repr = self.dxtools.create_address_csv(
            rows=rows,
            header_dict=header_dict,
            def_val_dict=def_val_dict,
            asset_col=asset_col
        )
        if len(csv_repr) > 1:
            guid = self.dxtools.bulk_update_addresses_via_data_exchange(
                csv_repr)
            self.logger.info("Data Exchange Address update: {0}".format(guid))

    def bulk_update_spatial(self, rows):
        # type: (list)->None
        """
        Use data exchange to bulk update spatial data of asset
        :param rows: a list of dicts
        """
        csv_repr = self.dxtools.create_spatial_csv(rows)
        if len(csv_repr) > 1:
            guid = self.dxtools.bulk_update_spatial_via_data_exchange(
                nested_list=csv_repr
            )
            self.logger.info("Data Exchange Spatial update: {0}".format(
                guid))

    def bulk_update_components(self, rows, layer_name):
        # type: (list, str) -> None
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update components.
        Assumes that each asset and component already exists

        # todo support new component creation ?!

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param layer_name: Name of the GIS layer being processed
        :return: None
        """
        header_dicts = self.get_cp_client_to_label_dicts(layer_name)

        if len(header_dicts) == 0:
            # e.g. there are no mappings for components in the XML, return early
            return

        asset_col = self.get_asset_column(layer_name)

        # retrieve dict that defines default values for components
        def_vals_list = self.get_cp_label_default_dicts(layer_name)

        # retrieve a list of asset values so we can retrieve
        # all attached components
        assets_list = [r[asset_col] for r in rows]

        asset_cps = self.asset_tools.get_attached_components(assets_list)
        self._component_list = asset_cps   # use later in network measure
        csv_repr = self.dxtools.create_component_csv(
            rows=rows,
            header_dicts=header_dicts,
            def_vals_list=def_vals_list,
            asset_col=asset_col,
            assets_cps=asset_cps
        )

        if len(csv_repr) > 1:
            guid = self.dxtools.bulk_update_components_via_data_exchange(
                nested_list=csv_repr
            )
            self.logger.info("Data Exchange Component update: {0}".format(
                guid))

    def bulk_update_networkmeasures(self, rows, layer_name):
        # type: (list, str) -> None
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update network measures. Assumes that each asset, component, and
        network measurement already exists.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param layer_name: Name of the ESRI layer being processed
        :return: None
        """
        header_dicts = self.get_nm_client_to_label_dicts(layer_name)

        # retrieve dict that defines default values for network measurements
        label_vals_list = self.get_nm_label_default_dicts(layer_name)

        asset_col = self.get_asset_column(layer_name)

        # retrieve a list of asset values so we can retrieve
        # all attached components
        assets_list = [r[asset_col] for r in rows]

        asset_nms = self.asset_tools.get_attached_networkmeasures(assets_list)

        # returning multiple CSVs as a tuple can probably be done better
        csvs_no_shapes, csvs_rects, csvs_circs = self.dxtools.create_networkmeasure_csvs(
            rows=rows,
            header_dicts=header_dicts,
            def_vals_list=label_vals_list,
            asset_col=asset_col,
            asset_nms=asset_nms,
            component_list=self._component_list
        )

        for i, (cp, csv_) in enumerate(csvs_no_shapes.items()):
            if len(csv_) > 1:
                guid = self.dxtools.bulk_update_network_measures_via_dataexchange(
                    nested_list=csv_,
                    shape='No Shape',
                    cp_name=cp
                )
                self.logger.info(
                    "Data Exchange Network Measure update: {0}".format(guid))

        for i, (cp, csv_) in enumerate(csvs_rects.items()):
            if len(csv_) > 1:
                guid = self.dxtools.bulk_update_network_measures_via_dataexchange(
                    nested_list=csv_,
                    shape='Rectangle',
                    cp_name=cp
                )

        for i, (cp, csv_) in enumerate(csvs_circs.items()):
            if len(csv_) > 1:
                guid = self.dxtools.bulk_update_network_measures_via_dataexchange(
                    nested_list=csv_,
                    shape='Circle',
                    cp_name=cp
                )

    def bulk_update_asset_fl_assoc(self, rows, layer_name):
        layer_dict = self.get_funcloc_xml_layer_dict(layer_name)
        if len(layer_dict) == 0:
            return
        header_dict = self.get_funcloc_client_label_dict(layer_name)

        if layer_dict['functional_location_name']:
            # have a field in GIS for FL Name
            flnames = list(set(
                [r[layer_dict['functional_location_name']] for r in rows]))

            fl_info = self.funcloc_tools.get_functional_locations_by_names(
                flnames)
        else:
            # get by FL ID
            fl_ids = list(set(
                [r[layer_dict['functional_location_id']] for r in rows]))

            fl_info = self.funcloc_tools.get_functional_locations_by_ids(
                fl_ids)
        if not fl_info:
            # no fl's
            return

        # Now create csv
        csv_repr = self.dxtools.create_functionallocation_csv(
            rows, layer_dict, header_dict, fl_info)

        if len(csv_repr) > 1:
            df = pd.DataFrame(csv_repr[1:], columns=csv_repr[0])
            guid = self.dxtools.bulk_update_asset_fl_assoc_via_data_exchange(
                csv_repr)
            self.logger.info("Data Exchange Functional Location update: {0}"
                             .format(guid))

    def _get_cat_config(self, layer_name):
        # type: (str) -> dict
        """
        Parses the layerconfig dictionary and returns the attributes
        for the given layer

        :param layer_name: GIS Layer name
        :return:
        """
        for config in self.layer_config.assetconfig:
            if config['layer'] == layer_name:
                return config

        confs = ', '.join([c['layer'] for c in self.layer_config.assetconfig])

        raise TypeError("Error parsing XML. No Asset layer called {}. "
                        "Available layers: {}".format(layer_name, confs))

    def get_asset_label_default_dict(self, layer_name):
        # type: (str) -> dict
        """
        Retrieves a dictionary that provides default data for the cloud upload
        file, drawing info from BOTH the coredefault node and attributefields
        node.

        Returns a dict where the key is the cloud label, and the value
        is a static value.

        :param layer_name: GIS Layer name
        :return:
        """
        cat_config = self._get_cat_config(layer_name)

        core_defaults = cat_config['coredefaults']
        attr_defaults = cat_config['attributedefaults']

        comb_defaults = dict()
        comb_defaults.update(core_defaults)
        comb_defaults.update(attr_defaults)

        labels = {}
        for attr, val in core_defaults.items():
            odata_val = cust_config_xml_defs.asset_core_fields_dict[attr]
            label = self.odata.asset_odata[odata_val]
            labels[label] = val

        for attr, val in attr_defaults.items():
            label = self.odata.asset_odata[attr]
            labels[label] = val

        return labels

    def get_nm_label_default_dicts(self, layer_name):
        # type: (str) -> list
        """
        Retrieves a list of dictionaries that provides default data
        for the cloud upload file, drawing info from component default
        xml node.

        Each dictionary relates to the network measurement defined
        in the customer config xml file under the <dimension> node.

        :param layer_name: GIS Layer name
        :return: List[dict]
        """

        cat_config = self._get_cat_config(layer_name)

        cps = cat_config['components']  # type: list

        xml_val_list = []
        for c in cps:
            cp_type = c['defaults']['component_type']
            dims = c['dimensions']
            for d in dims:
                defs = d['defaults']  # type: dict
                try:
                    defs['component_type'] = cp_type
                except KeyError:
                    pass
                try:
                    defs['label'] = c['defaults']['label']
                except KeyError:
                    pass

                xml_val_list.append(defs)

        label_val_list = []
        for nmdict in xml_val_list:
            nmlabels = {}
            for xmlval, defval in nmdict.items():
                odata_val = cust_config_xml_defs.nm_fields_dict[xmlval]
                try:
                    clabel = self.odata.networkmeasure_odata[odata_val]
                except KeyError:
                    clabel = self.odata.component_odata[odata_val]
                nmlabels[clabel] = defval

            label_val_list.append(nmlabels)

        return label_val_list

    def get_cp_label_default_dicts(self, layer_name):
        # type: (str) -> list
        """
        Retrieves a list of dictionaries that provides default data
        for the cloud upload file, drawing info from component xml node.

        Each dictionary relates to the component defined
        in the customer config xml file under the <component> node.

        :param layer_name: GIS Layer name
        :return: List[dict]
        """
        # retrieve the configuration for the layer
        cat_config = self._get_cat_config(layer_name)

        # retrieve all of the info relating to components
        cps = cat_config['components']

        # define a new list for the component + label info
        def_cp_list = []

        # iterate over the defaults, retrieve the odata values, then
        # retrieve the cloud values
        for c in cps:
            dv = c['defaults']
            label_vals = {}
            for xml_val, def_val in dv.items():
                odata = cust_config_xml_defs.component_fields_dict[xml_val]

                try:
                    cloud = self.odata.component_odata[odata]
                except KeyError:
                    # sometimes odata doesn't contain all of the values
                    # we want, so labels are defined in the
                    # component fields dict
                    cloud = odata

                label_vals[cloud] = def_val
            def_cp_list.append(label_vals)

        return def_cp_list

    def _get_component_attributefields_dicts(self, layer_name):
        # type: (str) -> list
        """
        Get component attribute fields for each component defined
        in the customer config.

        :param layer_name: GIS Layer name
        :return:
        """

        cat_config = self._get_cat_config(layer_name)

        components = cat_config['components']  # type: list
        # returns list, one for each component

        cp_dicts = []
        for cp in components:  # type: dict
            cp_dicts.append(cp['attributes'])

        return cp_dicts

    def _get_address_attributefields(self, layer_name):
        # type: (str) -> dict
        """
        Get address attribute fields

        :param layer_name: GIS Layer name
        :return:
        """
        cat_config = self._get_cat_config(layer_name)

        addr_fields = cat_config['addressfields']

        return addr_fields

    def _get_nm_attributefields(self, layer_name):
        # type: (str) -> list
        """
        Returns list of network measure attributes, as defined in the
        components/dimensions xml node.

        :param layer_name: GIS Layer name
        :return:
        """
        cat_config = self._get_cat_config(layer_name)

        components = cat_config['components']  # type: list
        # returns list, one for each component

        attrs = []
        for cp in components:  # type: dict
            for dim in cp['dimensions']:
                attrs.append(dim['attributes'])

        return attrs

    def get_nm_client_to_label_dicts(self, layer_name):
        """
        Returns dict defining relationships between client headers and
        cloud headers.

        :param layer_name: GIS Layer name
        :return:
        """
        nm_list = self._get_nm_attributefields(layer_name)

        nms = []
        for nm in nm_list:  # type: dict
            nm_dict = {}
            for xmlval, layercol in nm.items():
                odata_val = cust_config_xml_defs.nm_fields_dict[xmlval]
                label = self.odata.networkmeasure_odata[odata_val]
                nm_dict[label] = layercol

            nms.append(nm_dict)

        return nms

    def get_addr_client_to_label_dicts(self, layer_name):
        """
        Returns a dictionary defining the relationship between the layer
        column names and their cloud label counterparts.

        :param layer_name: the name of the GIS layer
        :return: dictionary of address field names and corresponding
        layer column names
        """
        attrs = self._get_address_attributefields(layer_name)

        header_dict = {}
        for xml, lyrcol in attrs.items():
            try:
                odata_val = cust_config_xml_defs.address_fields_dict[xml]
            except KeyError:
                continue

            label = self.odata.asset_odata[odata_val]

            header_dict[lyrcol] = label

        return header_dict

    def get_cp_client_to_label_dicts(self, layer_name):
        """
        Get the layer definition for components from xml config

        :param layer_name: the name of the GIS layer
        :return: dictionary of component field names and corresponding
        GIS attribute field name
        """
        # From the XML config get a list of component dictionaries
        # There may be more than one component, hence the list
        cp_list = self._get_component_attributefields_dicts(layer_name)

        hds = []
        # iterate through each component XML definition and get labels to use
        for cp in cp_list:

            cp_dict = {}
            for xmlval, layercol in cp.items():
                if xmlval != "id":
                    odata_val = cust_config_xml_defs.component_fields_dict[
                        xmlval]
                    try:
                        label = self.odata.component_odata[odata_val]
                        if label == "Component ID":
                            # TODO Is this the right place to correct odata
                            label = "Component Id"
                    except KeyError:
                        label = odata_val
                    cp_dict[label] = layercol

            hds.append(cp_dict)

        return hds

    def get_funcloc_xml_layer_dict(self, layer_name):
        # type: (str) -> dict
        """
        Returns dict defining relationship between xml node and layerdata
        column name.

        This is useful in retrieving functional location type and functional
        location name to retrieve the ID.

        :param layer_name: GIS layer name
        :return:
        """

        cat_config = self._get_cat_config(layer_name)
        cores = cat_config['corefields']
        fls = cat_config['functionallocation']
        if len(fls) == 0:
            # No FL definition.  Ok, it's optional
            return dict()

        if 'functional_location_id' not in fls:
            if 'functional_location_type' not in fls and \
                    'functional_location_name' not in fls:
                # Need type (and name) defined if no ID
                return dict()
            else:
                # make sure id exists in dict
                fls['functional_location_id'] = None
        else:
            # make sure name and type exist in dict
            if 'functional_location_name' not in fls:
                fls['functional_location_name'] = None
            if 'functional_location_type' not in fls:
                fls['functional_location_type'] = None

        layer_dict = {
            'asset_id': cores['asset_id'],
            'functional_location_id': fls['functional_location_id'],
            'functional_location_name': fls['functional_location_name'],
            'functional_location_type': fls['functional_location_type'],
        }

        return layer_dict

    def get_funcloc_client_label_dict(self, layer_name):
        # type: (str) -> dict
        """
        Returns a dictionary defining relationship between cloud upload
        csv column headers and the layerdata column headers.

        :param layer_name: GIS layer name
        :return:
        """
        cat_config = self._get_cat_config(layer_name)
        cores = cat_config['corefields']
        fls = cat_config['functionallocation']

        c = cust_config_xml_defs

        label_dict = {
            # asset id - want this in csv
            c.funcloc_fields_dict['asset_id']: cores['asset_id'],

            # func loc id - want this in csv
            c.funcloc_fields_dict['functional_location_id']:
                fls['functional_location_id'],

            # only want below 2 if we don't have func loc id, so use
            # standard xml values
            'functional_location_name': fls['functional_location_name'],
            'functional_location_type': fls['functional_location_type'],
        }

        return label_dict

    def get_asset_client_to_label_dict(self, layer_name):
        """
        Returns a dictionary defining relationship between client supplied
        layer column names and the cloud upload labels.

        Includes values for BOTH the core fields and the attribute fields.

        :param layer_name:
        :return:
        """
        cat_config = self._get_cat_config(layer_name)

        attrs = cat_config['attributefields']
        cores = cat_config['corefields']

        labels = {}
        for odata, layercol in attrs.items():
            label = self.odata.asset_odata[odata]
            labels[label] = layercol

        for core, layercol in cores.items():
            # 'id' is the asset GUID which is not needed for DX
            if core != "id":
                odata_val = cust_config_xml_defs.asset_core_fields_dict[core]
                label = self.odata.asset_odata[odata_val]
                labels[label] = layercol

        return labels

    def get_asset_column(self, layer_name):
        # type: (str) -> str
        """
        Returns column name for asset id

        :param layer_name: GIS layer name
        :return:
        """

        cat_config = self._get_cat_config(layer_name)

        corefields = cat_config['corefields']

        asset_col = corefields['asset_id']

        return asset_col

    def get_addr_default_values(self, layer_name):
        cat_config = self._get_cat_config(layer_name)

        addr_fields = cat_config['addressdefaults']  # type: dict

        addr_defs = {}
        for xml, val in addr_fields.items():
            odata_val = cust_config_xml_defs.address_fields_dict[xml]
            try:
                cloud_label = self.odata.asset_odata[odata_val]
            except KeyError:
                cloud_label = odata_val

            addr_defs[cloud_label] = val

        return addr_defs
