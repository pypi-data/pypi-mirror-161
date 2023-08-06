# coding: utf-8

"""
    assetic.OData  (odata.py)
    Tools to assist with using Assetic OData endpoint
"""
from __future__ import absolute_import

import xml.etree.ElementTree as ET
from typing import List

import six.moves.urllib as urllib

from .apihelper import APIHelper
from ..api_client import ApiClient


class OData(object):
    """
    Class with generic tools to assist using OData endpoints - has a
    10k record return limit.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger

        self.apihelper = APIHelper(api_client)

        self._asset_odata = None
        self._component_odata = None
        self._networkmeasure_odata = None
        self._fl = None

    @property
    def asset_odata(self):
        # type: () -> dict
        """
        Cached asset odata.

        :return:
        """
        if self._asset_odata is None:
            self._asset_odata = self._get_odata_dict('assets')

        return self._asset_odata

    @property
    def component_odata(self):
        # type: () -> dict
        """
        Cached component odata.
        :return:
        """
        if self._component_odata is None:
            self._component_odata = self._get_odata_dict('component')

        return self._component_odata

    @property
    def networkmeasure_odata(self):
        # type: () -> dict
        """
        Cached network measure odata.
        :return:
        """
        if self._networkmeasure_odata is None:
            self._networkmeasure_odata = self._get_odata_dict('networkmeasure')

        return self._networkmeasure_odata

    @property
    def fl_odata(self):
        if self._fl is None:
            self._fl = self._get_odata_dict('functionallocations')

        return self._fl

    def _get_odata_dict(self, entity):
        # type: (str) -> dict
        """
        Retrieves a dictionary defining relationship between internal
        cloud names and friendly label names from the oData specification
        at https://env.assetic.net/odata/$metadata

        :param: entity
        :return: <dict>
        """
        # valid = {
        #     "assets": 0,
        #     "workorder": 1,
        #     "workrequest": 2,
        #     "component": 3,
        #     "fairvaluation": 4,
        #     "networkmeasure": 5,
        #     "servicecriteria": 6,
        #     "treatments": 7,
        #     "functionallocations": 8
        # }
        #
        # if entity not in valid.keys():
        #     raise TypeError("Must pass in valid entity type. "
        #                     "{} is not a valid entity.".format(entity))

        # pass in the url and retrieve the raw xml data
        raw = self.apihelper.generic_get('/odata/$metadata')

        if raw is None:
            raise Exception("Is the environment offline?")

        # instantiate element tree to parse the tree
        tree = ET.fromstring(raw)

        # retrieve the assets from the tree
        #entity_vals = tree[0][0][valid[entity]]
        entity_vals = None
        for node in tree[0][0]:
            if str(node.attrib['Name']).lower() == entity.lower():
                entity_vals = node
                break
        if entity_vals is None:
            raise TypeError("Must pass in valid OData entity type. "
                            "{0} not found.".format(entity))

        # iterate over all of the child nodes and build
        # a dict of names and their string values
        attrib_dict = {}
        for prop in entity_vals:
            attrib_dict[prop.attrib['Name']] = prop[0].attrib['String']

        return attrib_dict

    def get_odata_data(self, entity, fields, filters=None, top=500, skip=0
                       , orderby=None):
        """
        Get asset data from the asset endpoint.
        Specify fields, filter optional
        :param entity: odata entity
        currently one of 'assets','workorder','workrequest'
        :param fields: A list or tuple of fields to return.
        Specify at least one
        :param filters: A list of valid odata filters that will append by 'and'
        or a single string representing a valid filter (filter not validated)
        :param top: number of records to return using top syntax. default 500
        :param skip: number of records to skip, must be > 0. Default=0
        :param orderby: fields to order results by. Can be a delimited string
        , or list or tuple
        :returns: a list of asset dictionaries matching the select fields or
        None if error.  If no results then empty list
        """

        # todo, make list of supported entities dynamic - i.e. hit odata metadata
        # could do this on initialisation of this class?
        if entity not in ("assets", "workorder", "workrequest", "component"
                          , "fairvaluation", "networkmeasure", "servicecriteria"
                          , "treatments"):
            msg = 'Entity must be one of "assets", "workorder", "workrequest",' \
                  ' "component", "fairvaluation", "networkmeasure"\
                  , "servicecriteria", "treatments"'
            self.logger.error(msg)
            return None

        # build the URL.
        url = "/odata/{0}?$top={1}".format(entity, top)
        if skip > 0:
            # only include skip if non zero else endpoint returns no data
            url = url + "&$skip={0}".format(skip)
        # add search fields
        if isinstance(fields, list) or isinstance(fields, tuple):
            if len(fields) == 0:
                msg = "OData asset search requires at least one search field"
                self.logger.error(msg)
                return None
            url = url + "&$select=" + ",".join(fields)
        else:
            # assume single field as string or comma delimited string
            url = url + "&$select=" + fields
        # apply filters
        if isinstance(filters, list) or isinstance(filters, tuple):
            if len(filters) > 0:
                url = url + "&$filter=" + " and ".join(filters)
        elif filters is not None:
            # assume single field as string or comma delimited string
            url = url + "&$filter=" + filters

        # add order by
        if isinstance(orderby, list) or isinstance(orderby, tuple):
            if len(orderby) > 0:
                url = url + "&$orderby=" + ",".join(orderby)
        elif orderby is not None:
            # assume single field as string or comma delimited string
            url = url + "&$orderby=" + orderby

        # replace spaces but keep other special characters
        url = urllib.parse.quote(url, safe="/?$&='")
        # get the data
        response = self.apihelper.generic_get(url)
        if response is None:
            return None
        if "value" in response:
            return response["value"]
        else:
            return None

    @staticmethod
    def generate_odata_query_strings(entity, filter_, filter_contents, select):
        # type: (str, str, List[str], List[str]) -> List[str]
        """
        Returns a list of odata URL requests that can be passed to the api_helper
        generic_get's method to retrieve assets and their components.

        NOTE: oData URLs require only the values after $Filter to be URL encoded

        :param entity: oData entity
        :param filter_: feature to be used to retrieve values (retrieve from
        oData values)
        :param filter_contents: list of entities to be matched against, e.g. where
        filter_~eq~filter_contents[0]~and~filter_~eq~filter_contents[1]...
        :param select: features to be returned
        :return:
        """

        if isinstance(select, list) is False:
            raise TypeError("Passed in select queries must be a list, not {0}."
                            .format(type(select)))

        valid_entities = ['Assets', 'Component', 'NetworkMeasure',
                          'FunctionalLocations']

        if entity not in valid_entities:
            raise TypeError("'{0}' is an invalid oData entity. Choose one of {1}."
                            .format(entity, ', '.join(valid_entities)))

        select_str = ','.join(select)

        max_odata_len = 1450
        query = "/odata/{0}?$Select={1}&$Filter=".format(entity, select_str)

        filter_str = "{0} eq '{{}}'".format(filter_)

        urls = []
        query_cp = query
        for i, a in enumerate(filter_contents):
            new_size = (
                    len(query_cp) + len(urllib.parse.quote(filter_str.format(a))) +
                    len(urllib.parse.quote(' or '))
            )
            if new_size >= max_odata_len:
                # strip out of the url encoded ' or ' (len == 8)
                query_cp = query_cp[:-8]
                urls.append(query_cp)
                query_cp = query

            query_cp += urllib.parse.quote("{0} or ".format(filter_str.format(a)))
        else:
            # strip out of the url encoded ' or ' (len == 8)
            query_cp = query_cp[:-8]
            urls.append(query_cp)

        return urls

if __name__ == '__main__':
    o = OData()
    o._get_odata_dict('workorder')
