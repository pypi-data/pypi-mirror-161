"""
    Tools to assist with work request and work order integrations
"""
import base64
import os
import sys

from assetic import DocumentApi, DocumentRepresentation, FilePropertiesRepresentation

from ..api import AssetApi
from ..api_client import ApiClient
from ..models.custom_address import CustomAddress
from ..models.work_request_spatial_location \
    import WorkRequestSpatialLocation
from ..rest import ApiException


class MaintenanceTools(object):
    """
    Class to provide Work Request integration processes
    """

    def __init__(self, api_client=None):
        """
        initialise object
        :param api_client: sdk client object, optional
        :param **kwargs: provide any config specific to the CRM
        """
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger

        self.assetapi = AssetApi()

    def get_location_by_assetguid(self, assetguid):
        """
        Get the address and/or spatial definition for an asset
        :param assetguid: The asset GUID
        :returns:
        """
        try:
            spatial = self.assetapi.asset_search_spatial_information_by_asset_id(
                assetguid)
        except ApiException as e:
            if e.status == 404:
                # no spatial data, but that's ok
                return None
            else:
                msg = "Status {0}, Reason: {1} {2}".format(e.status, e.reason,
                                                           e.body)
                self.logger.error(msg)
                return None, None
        # create address object
        wraddr = CustomAddress()
        # create spatial location object
        wrsl = WorkRequestSpatialLocation()

        address = spatial["Data"]["properties"]["AssetPhysicalLocation"]
        if address is not None:
            wraddr.street_number = address["StreetNumber"]
            wraddr.street_address = address["StreetAddress"]
            wraddr.city_suburb = address["CitySuburb"]
            wraddr.state = address["State"]
            wraddr.zip_postcode = address["ZipPostcode"]
            wraddr.country = address["Country"]

        geoms = spatial["Data"]["geometry"]["geometries"]
        for geom in geoms:
            if geom["type"] == "Point":
                wrsl.point_string = "Point({0} {1})".format(
                    str(geom["coordinates"][0]),
                    str(geom["coordinates"][1]))
        return wraddr, wrsl

    @staticmethod
    def _encode_file(abs_file_path):
        # type: (str) -> str
        """
        base64 encodes a file so it can be sent as a JSON attribute when uploading a file.

        Supports python2 and python3

        :param abs_file_path:
        :return:
        """
        with open(abs_file_path, "rb") as f:

            data = f.read()

            if sys.version_info < (3, 0):
                # python 2
                filecontents = data.encode("base64")
            else:
                # python 3
                bytes_filecontents = base64.b64encode(data)
                filecontents = bytes_filecontents.decode(encoding="utf-8", errors="strict")

        return filecontents

    def _attach_file(self, doc_rep, abs_file_path):
        # type: (DocumentRepresentation, str) -> None
        """
        Accepts a DocumentRepresenation and path to file. Encodes the file contents,
        and attaches contents and attributes to the DocumentRepresentaion
        as a FilePropertiesRepresentation.

        :param doc_rep:
        :param abs_file_path:
        :return: None
        """

        if not os.path.isfile(abs_file_path):
            self.logger.error("File not found {0}".format(abs_file_path))
            return None

        # get/generate all of the attributes of the file
        file_name = os.path.split(abs_file_path)[1]
        file_extension = file_name.split(".")[-1]
        file_size = os.path.getsize(abs_file_path)

        # b64 encode the file
        filecontents = self._encode_file(abs_file_path)

        # instatiate a FilePropertiesRepresentation
        file_properties = FilePropertiesRepresentation()

        # attach all of the attributes to the file
        file_properties.name = file_name
        file_properties.file_size = file_size
        file_properties.mimetype = file_extension
        file_properties.filecontent = filecontents
        filearray = [file_properties]

        # attach the file representation to the document representation
        doc_rep.file_property = filearray

        # no need to return anything as we are attaching the file representation
        # to the passed in object

    def post_document_to_work_request(self, file_path, work_request_guid, document_group, **kwargs):
        # type: (str, str, str, **str) -> str
        """
        Uploads document against a work request identified by work_request_id.

        :param file_path: <str> Full file path of the document to upload
        :param work_request_guid: <str> unique identifier of the work request
        :param document_group: <str> Document Group label
        :param kwargs:
            description: <str> file description to be uploaded against the file, defaults to None
            document_category: <str> Document category, defaults to None
            document_sub_category: <str> Document Sub Category, defaults to None
            external_id: <str> defaults to None
        :return:
        """

        # define the default values of all of the kwargs
        def_kwargs = {
            'description': None,
            'document_category': None,
            'document_sub_category': None,
            'external_id': None,
        }

        # throw error if an unknown kwarg is provided
        if set(kwargs.keys()).issubset(def_kwargs.keys()) is False:
            # only interested in the first error
            diff = list(set(kwargs.keys()).difference(set(def_kwargs.keys())))[0]
            raise TypeError("'{}' is an invalid keyword arugment for this function.".format(diff))

        # overwrite the kwargs with new values if no errors thrown
        def_kwargs.update(kwargs)

        docapi = DocumentApi()

        # these are the required properties
        docrep = DocumentRepresentation()
        docrep.document_group_label = document_group
        docrep.parent_id = work_request_guid
        docrep.parent_type = 3  # this is the file type for work requests

        # attach the kwargs (should never fail as they have been pre-defined as None)
        docrep.description = def_kwargs['description']
        docrep.document_category = def_kwargs['document_category']
        docrep.document_sub_category = def_kwargs['document_sub_category']
        docrep.external_id = def_kwargs['external_id']

        self._attach_file(docrep, file_path)
        if not docrep.file_property:
           return 1

        try:
            doc_json = docapi.document_post(docrep)
        except ApiException:
            self.logger.error("Error posting document {} to Work Request with ID {}."
                              .format(os.path.split(file_path)[-1], work_request_guid))
            return 1

        doc_guid = doc_json[0]['Id']

        return doc_guid
