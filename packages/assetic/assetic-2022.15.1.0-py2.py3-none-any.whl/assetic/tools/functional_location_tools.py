# coding: utf-8

"""
    assetic.FunctionalLocationTools
    Tools to assist with using Assetic API's for functional location.
"""
from __future__ import absolute_import

from typing import Optional, List

from .. import \
    FunctionalLocationApi \
    , CreatedRepresentationFunctionalLocationRepresentation \
    , FunctionalLocationRepresentation, AssetConfigurationApi \
    , AssetApi
from .odata import OData
from .apihelper import APIHelper
from ..api_client import ApiClient
from ..rest import ApiException


class FunctionalLocationTools(object):
    """
    Class to manage processes involving functional location
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.logger = api_client.configuration.packagelogger

        self.fl_api = FunctionalLocationApi(api_client)
        self.ac_api = AssetConfigurationApi(api_client)
        self.asset_api = AssetApi(api_client)
        self.apihelper = APIHelper(api_client)
        self.odata = OData(api_client)

        self._functional_location_types = None

    @property
    def functional_location_types(self):
        # type: () -> List[dict]
        """
        Caches functional location types to reduce API calls if retrieving
        the GUID of multiple functional locations.

        :return:
        """

        if self._functional_location_types is None:
            self._functional_location_types = self.get_functional_location_types()

        return self._functional_location_types

    def get_functional_location_type_id(self, flname):
        # type: (str) -> str
        """
        Iterates through cached functional location types and returns
        the GUID of the passed in functional location type name.

        :param flname: name of functional location type
        :return: <str> ID of functional location type
        """
        for fl in self.functional_location_types:
            if fl['FunctionalLocationTypeName'] == flname:
                return fl['Id']

        return ''

    def get_functional_location_types(self, page_size=500):
        # type: (int) -> List[dict]
        """
        Retrieves all of the functional location types from the
        environment.

        :return: <List[dict]> list of dicts containing name and type
        info
        """

        resp = self.ac_api.asset_configuration_get_group_asset_types(
            request_params_page=1, request_params_page_size=page_size,
            request_params_sorts='FunctionalLocationTypeName-asc')

        fls = resp['ResourceList']

        if resp['TotalPages'] != 1:
            # e.g. there are multiple pages to pull
            for i in range(2, resp['TotalPages'] + 1):
                nresp = self.ac_api.asset_configuration_get_group_asset_types(
                    request_params_page=i, request_params_page_size=page_size,
                    request_params_sorts='FunctionalLocationTypeName-asc')

                fls.extend(nresp['ResourceList'])
        return fls

    def create_functional_location(self, fl_representation):
        # type: (FunctionalLocationRepresentation) -> Optional [CreatedRepresentationFunctionalLocationRepresentation, None]
        """
        Create a functional location.
        :param fl_representation: required
        FunctionalLocationRepresentation
        :return: resultant functional location as
        FunctionalLocationRepresentation
        """

        # First make sure the object is correct
        self.logger.debug("Verify functional location fields")

        mandatory_fields = [
            "functional_location_name",
            "functional_location_type_id"
        ]

        for field in mandatory_fields:
            if fl_representation.__getattribute__(field) is None:
                self.logger.error("Mandatory field {0} missing from object "
                                  "FunctionalLocationRepresentation. Exiting."
                                  .format(field))
                return None

        # create the functional location
        self.logger.info("Create the functional location {0}".format(
            fl_representation.functional_location_name))
        try:
            response = self.fl_api.functional_location_post(fl_representation)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return None

        created_fl = self.api_client.deserialize(
            response['Data'][0], 'FunctionalLocationRepresentation')
        # fl_representation.id = response['Data'][0]['Id']
        return created_fl

    def create_functional_location_if_new(self, fl_representation):
        # type: (FunctionalLocationRepresentation) ->
        # type: Optional [CreatedRepresentationFunctionalLocationRepresentation, None]
        """
        Create a functional location only if new name for the given type,
        otherwise return existing
        :param fl_representation: required
        FunctionalLocationRepresentation
        :return: resultant functional location as
        FunctionalLocationRepresentation
        """
        # check to see if existing
        existing_fl = self.get_functional_location_by_name_and_type(
            fl_representation.functional_location_name
            , fl_representation.functional_location_type
            , fl_representation.attributes
        )
        if existing_fl and len(existing_fl) > 0:
            # return first record
            return existing_fl[0]

        # no existing fl so create the functional location
        self.logger.info("Create the functional location {0}".format(
            fl_representation.functional_location_name))
        try:
            response = self.fl_api.functional_location_post(fl_representation)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return None

        return response

    def get_functional_location_by_id(self, fl_id, attributes=None):
        # type: (str, Optional [List[str]]) -> Optional [FunctionalLocationRepresentation, None]
        """
        Get a functional location for the given functional location ID
        Can be either the GUID or the user friendly ID
        :param fl_id: The functional location GUID or Friendly ID
        :param attributes: A list of non-core attributes to get
        :return: fl response object or None
        """
        if not attributes:
            attributes = list()
        self.logger.debug("Get the functional location {0}".format(
            fl_id))
        try:
            fl = self.fl_api.functional_location_get(fl_id, attributes)
        except ApiException as e:
            if e.status == 404:
                self.logger.info(
                    "Functional Location for Functional Location GUID/Id {0} "
                    "not found".format(fl_id))
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status, e.reason,
                                                           e.body)
                self.logger.error(msg)
            return None

        flrepr = self.api_client.deserialize(fl, 'FunctionalLocationRepresentation')

        return flrepr

    def get_functional_location_by_name_and_type(self, fl_name, fl_type,
                                                 attributes=None):
        # type: (str, str, Optional [List[str]]) -> FunctionalLocationRepresentation
        """
        For the given name and functional location type return the
        functional location(s).  Name is not unique
        :param fl_name:
        :param fl_type:
        :param attributes:
        :return:
        """

        if not attributes:
            attributes = list()

        kwargs = {
            'request_params_page': 1
            , 'request_params_page_size': 50
            , 'request_params_filters':
                "FunctionalLocationType~eq~'{0}'~and~"
                "FunctionalLocationName~eq~'{1}'".format(fl_type, fl_name)
        }
        self.logger.debug(
            "Get the functional location for name {0} and type {1}".format(
                fl_name, fl_type))
        try:
            fl = self.fl_api.functional_location_get_0(attributes, **kwargs)
        except ApiException as e:
            if e.status == 404:
                self.logger.info(
                    "Functional Location for Functional Location not found "
                    "for name {0} and type {1}".format(fl_name, fl_type))
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status, e.reason,
                                                           e.body)
                self.logger.error(msg)
            return None

        if len(fl['ResourceList']) == 0:
            # e.g. no FLs by type and name
            return None

        if len(fl['ResourceList']) > 1:
            # more than 1 FL with identical type and name
            # environment has therefore been misconfigured, and we should throw
            # errors and exit
            self.logger.warning("Multiple Functional Locations with Name {0} "
                                "and Type {1} detected. This may cause "
                                "issues as package assumes only one FL per "
                                "name and type.".format(fl_name, fl_type))

        rfl = fl['ResourceList'][0]

        flr = self.api_client.deserialize(rfl, 'FunctionalLocationRepresentation')

        return flr

    def get_functional_locations_by_names(self, flnames):
        # type: (list) -> list
        """
        Method to retrieve functional location information given a list
        of functional location names.

        Uses oData instead of API, as the maximum ~and~ filter
        length is 2 elements.

        Note: can be changed to use API once filter.in is introduced as a
        feature for FunctionalLocation.get

        :param flnames: <List[str]> list of functional location names
        :return: <List[dict]>
        """

        select = [
            'GroupAssetNameL1',
            'GroupAssetTypeIdL1',
            'GroupAssetIdL1',
            'GAidL1'
        ]

        urls = self.odata.generate_odata_query_strings(
            entity='FunctionalLocations',
            filter_='GroupAssetNameL1',
            filter_contents=flnames,
            select=select
        )

        fls = []
        for url in urls:
            resp = self.apihelper.generic_get(url)
            fls.extend(resp['value'])

        return fls

    def get_functional_locations_by_ids(self, fl_ids):
        # type: (list) -> list
        """
        Method to retrieve functional location information given a list
        of functional location names.

        Uses oData instead of API, as the maximum ~and~ filter
        length is 2 elements.

        Note: can be changed to use API once filter.in is introduced as a
        feature for FunctionalLocation.get

        :param fl_ids: <List[str]> list of functional location Id's
        :return: <List[dict]>
        """

        select = [
            'GroupAssetNameL1',
            'GroupAssetTypeIdL1',
            'GroupAssetIdL1',
            'GAidL1'
        ]

        urls = self.odata.generate_odata_query_strings(
            entity='FunctionalLocations',
            filter_='GroupAssetIdL1',
            filter_contents=fl_ids,
            select=select
        )

        fls = []
        for url in urls:
            resp = self.apihelper.generic_get(url)
            fls.extend(resp['value'])

        return fls

    def link_asset_to_functional_location(self, asset_id, fl_representation):
        # type: (str, FunctionalLocationRepresentation) -> int
        """
        Associates asset with functional location.

        :param asset_id: <str> friendly asset ID
        :param fl_representation: <FunctionalLocationRepresentation>
        :return: 0 if successful, 1 if not
        """

        # mandatory_fields = [
        #     "functional_location_id",
        #     "functional_location_name",
        #     "functional_location_type",
        #     "functional_location_type_id",
        # ]
        #
        # for field in mandatory_fields:
        #     if fl_representation.__getattribute__(field) is None:
        #         self.logger.error("Mandatory field {0} missing from object "
        #                           "FunctionalLocationRepresentation. Exiting."
        #                           .format(field))
        #         return 1

        try:
            resp = self.asset_api.asset_link_complex_asset_to_functional_location(
                asset_id, fl_representation)
            errcode = 0
        except ApiException:
            errcode = 1

        return errcode

    def update_functional_location(self, flrepr):
        # type: (FunctionalLocationRepresentation) -> FunctionalLocationRepresentation
        try:
            resp = self.fl_api.functional_location_put(flrepr.id, flrepr)
        except ApiException:
            msg = ("Error attempting to update attributes of Functional Location "
                   "with Name {0} nd ID {1}.".format(flrepr.functional_location_name,
                                                     flrepr.functional_location_id))
            self.logger.error(msg)
            return None

        uflepr = self.api_client.deserialize(
            resp, 'FunctionalLocationRepresentation')

        return uflepr
