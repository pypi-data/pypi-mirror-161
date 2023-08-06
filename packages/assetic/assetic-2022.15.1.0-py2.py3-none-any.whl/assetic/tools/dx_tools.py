import base64
import csv
import sys
from io import StringIO, BytesIO

import functools
import pandas as pd
import six

from assetic import DocumentRepresentation, DocumentApi, DataExchangeJobNoProfileRepresentation, DataExchangeJobApi, FilePropertiesRepresentation
from assetic.tools.assets import AssetTools
from assetic.tools.static_def import dx_data as dx
from ..api_client import ApiClient


class DataExchangeTools(object):
    """
    Class to manage Data Exchange file creation from API data sources
    """
    
    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.asset_tools = AssetTools(api_client)
        self.logger = api_client.configuration.packagelogger
        self.dxjobapi = DataExchangeJobApi(api_client)
        # create a DocumentAPI object and post the documet representation
        self.docapi = DocumentApi(api_client)

    def create_asset_csv(self, rows, cloud_cat, header_dict,
                         default_asset_values):
        # type: (list, str, dict, dict) -> list
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update assets. Assumes that each asset already exists.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param cloud_cat: <str> asset category to upload against in the data
        exchange.
        :param header_dict: <dict> defines the relationship between the
        the header of the cloud data exchange upload file, and the column
        label of the List[dict-like] object.
        E.g.
            {'Asset ID': 'UNIQUE_ASSET_ID'}
        :param default_asset_values: <dict> defines any values that are static
        for the entire CSV, and are not included in the layerfile.
        E.g.
            {'Country': 'Australia'}
        :return: <List[List]> nested list representation of the file to
        be uploaded.
        """
        def_vals_cols = sorted(list(default_asset_values.keys()))
        def_vals = [default_asset_values[d] for d in def_vals_cols]

        cloud_cols = sorted(list(header_dict.keys()))
        layer_cols = [header_dict[c] for c in cloud_cols]

        first_row = cloud_cols + def_vals_cols + ['Asset Category']

        # get the cloud labels for each of the headers
        # and add it to the first row
        asset_rows = [first_row]

        # iterate over each of the row values
        for row in rows:  # type: dict
            # create a list representing the new row
            c_row = []

            for col in layer_cols:
                c_row.append(row[col])

            for val in def_vals:
                c_row.append(val)

            c_row.append(cloud_cat)
            asset_rows.append(c_row)

        # df = pd.DataFrame(data=asset_rows[1:], columns=asset_rows[0])

        return asset_rows

    @staticmethod
    def create_address_csv(rows, header_dict, def_val_dict, asset_col):
        # type: (list, dict, dict, str) -> list
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update address information. Assumes that each asset
        already exists.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param header_dict: <dict> defines the relationship between the
        the header of the cloud data exchange upload file, and the column
        label of the List[dict-like] object.
        E.g.
            {'Asset ID': 'UNIQUE_ASSET_ID'}
        :param def_val_dict: <dict> defines any values that are static for
        the entire CSV, and are not included in the layerfile.
        E.g.
            {'Country': 'Australia'}
        :param asset_col: <str> the layerfile column label that defines
        the asset ID column.
        :return: <List[List]> nested list representation of the file to
        be uploaded.
        """

        # create order of columns and the order by which we retrieve the
        # values from the layer columns
        cols_layer = sorted(list(header_dict.keys()))
        cols_label = [header_dict[h] for h in cols_layer]

        # retrieve the default dict and set the order by which
        # we add default values
        def_cols = sorted(list(def_val_dict.keys()))
        def_vals = [def_val_dict[d] for d in def_cols]

        # generate the first row
        first_row = ['Asset Id'] + cols_label + def_cols

        adr_rows = [first_row]

        # iterate over each row, extract values from row, then
        # add default values
        for row in rows:  # type: dict
            adr_row = [row[asset_col]]

            for lcol in cols_layer:
                val = row[lcol]
                adr_row.append(val)

            for dval in def_vals:
                adr_row.append(dval)

            adr_rows.append(adr_row)

        # df = pd.DataFrame(data=adr_rows[1:], columns=adr_rows[0])

        return adr_rows

    def create_spatial_csv(self, rows):
        """
        For the given data add a data exchange header
        :param rows: a list of dict containing spatial data to load
        :return: <List[List]> nested list representation of the file to
        be uploaded.
        """
        first_row = ["Asset ID", "Point", "Polygon", "Line"]
        sp_rows = list()
        sp_rows.append(first_row)

        for row_dict in rows:
            # map data to column list by key to avoid column order issues
            if six.PY2:
                sp_rows.append(
                    map(lambda x: row_dict.get(x, ""), first_row))
            else:
                sp_rows.append(
                    list(map(lambda x: row_dict.get(x, ""), first_row)))

        return sp_rows

    def create_component_csv(self, rows, header_dicts, def_vals_list, asset_col,
                             assets_cps):
        # type: (list, list, list, str, dict) -> list
        """
        Accepts a list of layer rows and uses the assetic SDK to bulk
        update components. Assumes that each asset and component already exists.

        # todo support new component creation ?!

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param header_dicts: <List[dict]> a list containing dicts that
        define the relationship between the the header of the cloud data
        exchange upload file, and the column label of the List[dict-like]
        object. Each separate dict contains different column headers based
        on the component type.
        E.g.
            [{'Design Life': 'PAVEMENT_DESIGN_LIFE'},
             {'Design Life': 'SURFACE_DESIGN_LIFE'},]
        Note: This list should define columns in the same order as the
        def_vals_list list of default values.
        :param def_vals_list: <List[dict]> a list containing dicts that
        define any values that are static for the component, and are not
        included in the layerfile.
        E.g.
            [{'Component Type': 'Pavement Base'},
             {'Component Type': 'Surface Main'},]
        Note: this list should define default values in the same order as
        the header_dicts.
        :param asset_col: <str> the layerfile column label that defines
        the asset ID column.
        :param assets_cps: <dict> dict defining the components attached
        to each asset in form:
            {'BR001': [{'ComponentName: 'Pavement Base', ...}, ...],
             'BR002': [{'ComponentName: 'Surface Main', ...}, ...]}
        Note: a dict of assets with associated components can be retrieved
        using the method AssetTools().get_attached_components()
        :return: <List[List]> nested list representation of the file to
        be uploaded.
        """

        # Build a unique list of all component field headers
        # Each record may have a different set of fields
        if six.PY2:
            header_columns = map(lambda x: x.keys(), header_dicts)
            default_columns = map(lambda x: x.keys(), def_vals_list)
            all_columns = header_columns + default_columns

            first_row = list(set(reduce(lambda x, y: x + y, all_columns)))
        else:
            header_columns = list(map(lambda x: x.keys(), header_dicts))
            default_columns = list(map(lambda x: x.keys(), def_vals_list))
            all_columns = header_columns + default_columns
            first_row = list(set(functools.reduce(
                lambda x, y: x | y, all_columns)))

        # sorted_headers = list(sorted(header_dicts[0].keys()))
        # sorted_default_headers = list(sorted(def_vals_list[0].keys()))
        # first_row = sorted_headers + sorted_default_headers

        # Ensure mandatory fields in header row
        if 'Component Id' not in first_row:
            first_row.append('Component Id')
        if 'Asset Id' not in first_row:
            first_row.append('Asset Id')

        # initialise the csv repr. with the first row containing headers
        cp_rows = [first_row]

        # iterate over each of the component configurations and populate the
        # csv with row data.
        for hv, dv in zip(header_dicts, def_vals_list):  # type: dict, dict

            # get sorted list of columns where we need to retrieve data
            val_cols = [hv[v] for v in sorted(hv.keys())]

            # get sorted list of columns where we need to add static/default data
            def_vals_cols = sorted(list(dv.keys()))

            # dicts to lookup GIS field name to get DX name
            if six.PY2:
                reverse_hv = dict((v, k) for k, v in hv.iteritems())
            else:
                reverse_hv = dict((v, k) for k, v in hv.items())

            # iterate over rows, retrieve value columns, append default data
            for row in rows:  # type: dict
                # c_row = []
                row_dict = dict()
                mand_vals = []

                # retrieve new/updated data
                for vcol in val_cols:
                    val = row[vcol]
                    mand_vals.append(val == '')
                    # c_row.append(val)
                    if vcol in reverse_hv:
                        row_dict[reverse_hv[vcol]] = val
                # add static data
                for dvcol in def_vals_cols:
                    # c_row.append(dv[dvcol])
                    if dvcol in dv:
                        row_dict[dvcol] = dv[dvcol]

                # retrieve the component id and add it to the row
                if "Component Id" not in row_dict or \
                        row_dict["Component Id"] is None:
                    if 'Component Type' in dv and 'Component Name' in dv:
                        cp_id = self.asset_tools.get_component_id(
                            asset_id=row[asset_col],
                            cp_type=dv['Component Type'],
                            cp_name=dv['Component Name'],
                            asset_cps=assets_cps
                        )
                        if cp_id:
                            row_dict["Component Id"] = cp_id

                if "Component Id" not in row_dict or \
                        row_dict["Component Id"] is None:
                    self.logger.warning(
                        "Component not found for "
                        "asset '{0}' when bulk updating network "
                        "measure".format(
                            row[asset_col]
                        ))
                    continue
                # c_row.append(cp_id)

                # add the asset ID to the row too
                # c_row.append(row[asset_col])
                row_dict["Asset Id"] = row[asset_col]
                # if mandatory values are blank (val=='') then ignore the roe
                # and continue
                if all(mand_vals):
                    # e.g there is no data in the rows we want
                    continue

                # add row to the csv if it contains data
                # cp_rows.append(c_row)
                # map data to column list by key to avoid column order issues
                if six.PY2:
                    cp_rows.append(
                        map(lambda x: row_dict.get(x, ""), first_row))
                else:
                    cp_rows.append(
                        list(map(lambda x: row_dict.get(x, ""), first_row)))
        # df = pd.DataFrame(data=cp_rows[1:], columns=cp_rows[0])

        return cp_rows

    def create_networkmeasure_csvs(self, rows, header_dicts, def_vals_list,
                                   asset_col, asset_nms, component_list):
        """

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param header_dicts: <List[dict]> a list containing dicts that
        define the relationship between the the header of the cloud data
        exchange upload file, and the column label of the List[dict-like]
        object. Each separate dict contains different column headers based
        on the component type.
        E.g.
            [{'Design Life': 'PAVEMENT_DESIGN_LIFE'},
             {'Design Life': 'SURFACE_DESIGN_LIFE'},]
        Note: This list should define columns in the same order as the
        def_vals_list list of default values.
        :param def_vals_list: <List[dict]> a list containing dicts that
        define any values that are static for the component, and are not
        included in the layerfile.
        E.g.
            [{'Component Type': 'Pavement Base'},
             {'Component Type': 'Surface Main'},]
        Note: this list should define default values in the same order as
        the header_dicts.
        :param asset_col: <str> the layerfile column label that defines
        the asset ID column.
        :param asset_nms: <dict> dict defining the network measures attached
        to each asset in form:
            {'BR001': [{'ComponentName: 'Pavement Base', ...}, ...],
             'BR002': [{'ComponentName: 'Surface Main', ...}, ...]}
        Note: a dict of assets with associated components can be retrieved
        using the method AssetTools().get_attached_networkmeasures()
        :param component_list: List of assets with their components
        :return: <List[List]> nested list representation of the file to
        be uploaded.
        """
        csvs_no_shapes = {}
        csvs_rectangles = {}
        csvs_circles = {}

        for hv, dv in zip(header_dicts, def_vals_list):  # type: dict, dict

            shape_headers = list(hv.keys())
            shape_cols = [hv[c] for c in shape_headers]

            def_val_cols = list(dv.keys())

            #aid_headers = ['Asset Id', 'Component Name']
            aid_headers = ['Asset Id']

            first_row = shape_headers + def_val_cols + aid_headers

            first_row.append('Measurement Record Id')

            shape = self._determine_nm_shape(first_row)

            csv_rows = [first_row]

            for row in rows:
                srow = []

                # define empty list of important values
                mand_vals = []

                # retrieve all of the value fields from the row
                for scol in shape_cols:
                    sval = row[scol]
                    mand_vals.append(sval == '')

                    srow.append(sval)

                # add all of the default values to the new row
                for dvcol in def_val_cols:
                    srow.append(dv[dvcol])

                # add all of the component identifying info to the row
                srow.append(row[asset_col])

                # get component name for component type because nm record
                # does not hold type
                #TODO get component using combination of name and type
                cp_name = None
                if row[asset_col] in component_list:

                    # iterate over all of the components contained in the cp list
                    for component in component_list[row[asset_col]]:

                        # check to see if cp type matches
                        m_cptype = component["ComponentType"] == dv["Component Type"]

                        # check to see if cp name matches
                        m_cpname = component["ComponentName"] == dv["Component Name"]

                        if m_cptype and m_cpname:
                            # if match, retrieve the name
                            cp_name = component["ComponentName"]
                            break

                if not cp_name:
                    # No component name so move to next record
                    self.logger.warning(
                        "Component of type '{0}' not found for asset '{1}'"
                        " when bulk updating network measure".format(
                            dv["Component Type"], row[asset_col]
                        ))
                    continue

                nid = self.asset_tools.get_networkmeasure_id(
                    asset_id=row[asset_col],
                    cp_name=cp_name,
                    measurement_type=dv['Measurement Type'],
                    record_type=dv['Record Type'],
                    nm_list=asset_nms
                )

                srow.append(nid)

                # require this to be populated with at least one False
                # for row to be valid
                if all(mand_vals):
                    continue

                csv_rows.append(srow)

            if shape == 'No Shape':
                csvs_no_shapes[dv['Component Type']] = csv_rows
            elif shape == 'Circle':
                csvs_circles[dv['Component Type']] = csv_rows
            elif shape == 'Rectangle':
                csvs_rectangles[dv['Component Type']] = csv_rows
            else:
                self.logger.error("Unsupported Network Measure Shape Type"
                                  ": '{0}' No update created".format(shape))

        return csvs_no_shapes, csvs_rectangles, csvs_circles

    def create_functionallocation_csv(self, rows, layer_dict, header_dict,
                                      fl_info):
        """
        Creates a csv containing asset and functional location information.

        :param rows: <List[dict-like]> a list of dict objects representing
        rows from ther cursor
        :param layer_dict: <dict> a dict that defines the relationship between
        the the xml node and the layerdata column header.
        E.g.
            [{'functional_location_type': 'FL_TYPE_76'},
             {'functional_location_name': 'FLNAME'},]
        :param header_dict: <dict> a dict that defines the relationship between
        the layerdata column header and the csv cloud upload header.
        :param fl_info: List[dict] list containing functional location info
        in dict form.
        :return:
        """
        # Columns: Asset,	Functional Location ID
        df = pd.DataFrame(fl_info)

        first_row = ['Asset ID', 'Functional Location ID']

        csv_repr = [first_row]

        for row in rows:
            if not row[header_dict['functional_location_name']] and\
                       not row[header_dict['functional_location_type']]:
                # No FL defined for asset so continue to next record
                continue

            flrow = df.loc[
                (df['GroupAssetNameL1'] == row[
                    header_dict['functional_location_name']]) &
                (df['GroupAssetTypeIdL1'] == row[
                    header_dict['functional_location_type']])
                ]
            if flrow.empty:
                # doesn't exist.  Is that an error?
                self.logger.error(
                    "Unable to find functional location '{0}' for type '{1}' "
                    "".format(row[header_dict['functional_location_name']]
                              , row[header_dict['functional_location_type']]))
                continue
            try:
                flid = flrow.iloc[0]['GroupAssetIdL1']
            except KeyError:
                # Doesn't Exist
                self.logger.error(
                    "Unable to find functional location '{0}' for type '{1}' "
                    "".format(row[header_dict['functional_location_name']]
                              , row[header_dict['functional_location_type']]))
                continue
            csv_row = [row[layer_dict['asset_id']], flid]
            csv_repr.append(csv_row)

        return csv_repr

    @staticmethod
    def _find_flid(flname, fltype, fls):
        # type: (str, str, list) -> str
        """
        Searches through passed in functional locations to find the FL
        that contains functional location name and functional location type
        that matches passed in values

        :param flname: <str> functional location name
        :param fltype: <str> functional location type
        :param fls: <List[dict]> list of functional location values retrieved
        from odata.
        :return: <str> functional location ID
        """

        for fl in fls: # type: dict
            if (fl['GroupAssetNameL1'] == flname) and (fl['GroupAssetTypeIdL1'] == fltype):
                return fl['GroupAssetIdL1']

        return None

    @staticmethod
    def _determine_nm_shape(first_row):
        # type: (list) -> str
        """
        Examines the first row of a csv and determines the shape of the
        network measurement.

        :param first_row: list of columns contained within the csv
        :return: name of shape
        """

        rectangle = ['Length', 'Width']
        circle = ['Diameter']

        if set(rectangle).issubset(set(first_row)):
            shape = 'Rectangle'
        elif set(circle).issubset(set(first_row)):
            shape = 'Circle'
        else:
            shape = 'No Shape'  # todo only supports 3 shapes

        return shape

    def bulk_update_assets_via_data_exchange(self, nested_list, category):
        # type: (list, str) -> str
        """
        Uploads a nested list representing a data exchange CSV containing
        assets to the cloud.

        :param nested_list: representation of data exchange CSV
        :param category: target category in the data exchange. NOTE: must
        be cloud name, e.g. 'Buildings (Market Value)'
        :return:
        """

        mod_val = dx.MODULE_VALUES['Assets']
        cat_val = dx.ASSET_VALUES[category]

        fn = '{}_asset_dx_upload'.format(category)
        response = self.post_to_dx_no_profile(nested_list, mod_val, cat_val, fn)

        return response

    def bulk_update_components_via_data_exchange(self, nested_list):
        # type: (list) -> str
        """
        Uploads a nested list representing a data exchange CSV containing
        components to the cloud.

        :param nested_list: representation of data exchange CSV
        :return:
        """
        mod_val = dx.MODULE_VALUES['Components']
        cat_val = dx.COMPONENT_VALUES['Update Component']

        fn = 'component_upload'
        response = self.post_to_dx_no_profile(
            nested_list,
            mod_val,
            cat_val,
            fn
        )

        return response

    def bulk_update_network_measures_via_dataexchange(self, nested_list, shape,
                                                      cp_name=None):
        # type: (list, str, str) -> str
        """
        Uploads a nested list represetned network measurements to the data
        exchange.

        Must pass in the shape name (limited to the shapes available to the
        data exchange), and the component name to which it relates.

        :param nested_list: <List[list]]> representation of data exchange CSV
        :param shape: <str> network measure shape
        :param cp_name: <str=None> component name
        :return:
        """
        if cp_name is None:
            cp_name = 'all'

        shapes_dict = {
            'No Shape': 'Add/Update Network Measure (without shape)',
            'Circle': 'Add/Update Circle',
            'Rectangle': 'Add/Update Rectangle',
        }

        cat = shapes_dict[shape]

        mod_val = dx.MODULE_VALUES['Components Network Measure']
        cat_val = dx.NETWORK_MEASURE_VALUES[cat]

        fn = 'networkmeasure_{}_{}'.format(cp_name, shape.lower().replace(" ", "_"))
        response = self.post_to_dx_no_profile(
            nested_list,
            mod_val,
            cat_val,
            fn
        )

        return response

    def bulk_update_addresses_via_data_exchange(self, nested_list):
        # type: (list) -> str
        """
        Uploads a nested list represented addresses to the data exchange.

        :param nested_list: <List[list]]> representation of data exchange CSV
        :return:
        """

        mod_val = dx.MODULE_VALUES['Mapping']
        cat_val = dx.MAPPING_VALUES['Asset Address']

        fn = 'address_upload'
        response = self.post_to_dx_no_profile(
            nested_list,
            mod_val,
            cat_val,
            fn
        )
        return response

    def bulk_update_spatial_via_data_exchange(self, nested_list):
        # type: (list) -> str
        """
        Uploads a nested list represented addresses to the data exchange.

        :param nested_list: <List[list]]> representation of data exchange CSV
        :return:
        """

        mod_val = dx.MODULE_VALUES['Mapping']
        cat_val = dx.MAPPING_VALUES['Asset Spatial']

        fn = 'spatial_upload'
        response = self.post_to_dx_no_profile(
            nested_list,
            mod_val,
            cat_val,
            fn
        )
        return response

    def bulk_update_asset_fl_assoc_via_data_exchange(self, nested_list):
        # type: (list) -> str
        """
        Uploads a nested list representing functional locations to the data exchange.

        :param nested_list: <List[list]]> representation of data exchange CSV
        :return:
        """

        mod_val = dx.MODULE_VALUES['Assets Associations']
        cat_val = dx.ASSETS_ASSOCIATIONS_VALUES['Functional Location to Asset']

        fn = 'fn_to_asset_associations'
        response = self.post_to_dx_no_profile(
            nested_list,
            mod_val,
            cat_val,
            fn
        )

        return response

    def post_to_dx_no_profile(self, nested_list, mod_val, cat_val, file_name):
        # type: (list, str, str, str) -> str
        """
        Posts a nested list representing a CSV to the data exchange using
        api/v2/dataexchangejobnoprofile, using module and category values
        defined by the passed in parameters.

        Cloud values are defined in dicts in the tools/static_def/dx_data.py
        files.

        :param nested_list:
        :param mod_val:
        :param cat_val:
        :param file_name:
        :return:
        """

        doc = DocumentRepresentation()

        # conver the list contents to a CSV, and attach to the document representation
        self._attach_csv_to_document(doc, nested_list, file_name)

        # posting a document just creates it, it doesn't upload to data exchange
        guid = self.docapi.document_post(doc)[0]['Id']

        # create a data exchange job representation
        # note: swagger definitions sometimes break, which is why
        # guid, module, and category are being set manually
        dxdoc = DataExchangeJobNoProfileRepresentation('', '', '')

        # manually set important values
        dxdoc.document_id = guid
        dxdoc.module = mod_val
        dxdoc.category = cat_val

        # create a DX API object and post to data exchange
        # note: data_exchange_job_post_0 refers to api/v2/dataexchangejobnoprofile
        dx_guid = self.dxjobapi.data_exchange_job_post_0(dxdoc)

        return dx_guid

    @staticmethod
    def _attach_csv_to_document(doc_rep, nested_list, file_name):
        # type: (DocumentRepresentation, list, str) -> None
        """
        Attaches nested list (representative of a data exchange CSV document)
        to a DocumentRepresentation.

        :param doc_rep: <DocumentRepresentation> object to be posted
        to assetic document API
        :param nested_list: <list> nested list containing information to be
        uploaded to cloud
        :param file_name: <str> name of the file to be uploaded
        :return: None
        """

        # write the nested list as csv contents to the io object
        # csv.writer(in_mem_csv).writerows(nested_list)
        # set csv writer output to string
        if six.PY2:
            in_mem_csv = BytesIO()
            csv.writer(in_mem_csv).writerows(nested_list)
        else:
            # create an in memory io object
            in_mem_csv = StringIO()
            csv.writer(in_mem_csv).writerows(nested_list)

        # retrieve the file size of the in memory object
        file_size = sys.getsizeof(in_mem_csv)

        # convert to bytes
        bytestr = in_mem_csv.getvalue().encode('utf-8')

        # encode as base64
        b64_bytes = base64.b64encode(bytestr)

        # decode back in to string (still base64)
        filecontents = b64_bytes.decode('utf-8')

        # create a file properties object and attach all of the info to it
        file_properties = FilePropertiesRepresentation()
        file_properties.name = file_name
        file_properties.file_size = file_size
        file_properties.mimetype = 'csv'
        file_properties.filecontent = filecontents
        filearray = [file_properties]

        # attach the file properties to the document representation
        doc_rep.file_property = filearray

        # no need to return anything - attaches document info
        # to passed in DocumentRepresentation
