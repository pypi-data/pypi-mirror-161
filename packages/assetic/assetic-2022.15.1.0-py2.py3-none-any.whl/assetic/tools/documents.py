# coding: utf-8

"""
    assetic.DocumentTools  (documents.py)
    Tools to assist with using Assetic API's for documents.
"""
from __future__ import absolute_import

import six
from ..api_client import ApiClient
from ..rest import ApiException
from ..api import DocumentApi
from ..api import WorkOrderApi
from ..api import WorkRequestApi
from ..tools import AssetTools
from ..models.complex_asset_representation import ComplexAssetRepresentation
from pprint import pformat
from ..models.document_representation import DocumentRepresentation
from ..models.file_properties_representation import \
    FilePropertiesRepresentation

import abc

class DocumentTools(object):
    """
    Class to manage processes that manage Assetic documents
    """

    def __init__(self, ecms, api_client):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger
        self.documentapi = DocumentApi(self.api_client)
        self.ecms_name = ecms
        self.ecms_plugin = None
        if ecms == "HP_CM":
            self.ecms_plugin = self.init_hp_cm()
        elif ecms == "File_System":
            self.ecms_plugin = self.init_file_system_cm()
            
        self.asset_tools = AssetTools()
        self.workorderapi = WorkOrderApi()
        self.workrequestapi = WorkRequestApi()

    ##Allow user to access the plugin directly in case their workflow
    ##does not fit with the provided default workflow in these tools
    @property
    def ecmsid(self):
        return self._ecmsid
    
    def init_hp_cm(self):
        """
        Initialise the plugin for HP CM integration
        :return: The plugin which implements class ECMSPluginBase
        """ 
        try:
            from .document_plugins.hp_cm import HP_CMTools
            hp_plugin = HP_CMTools()
            return hp_plugin
        except ImportError as ex:
            self.logger.error(str(ex))
            return None

    def init_file_system_cm(self):
        """
        Initialise the plugin for File System integration
        :return: The plugin which implements class ECMSPluginBase
        """ 
        try:
            from .document_plugins.file_system import FileSystemDocuments
            file_system_plugin = FileSystemDocuments()
            return file_system_plugin
        except ImportError as ex:
            self.logger.error(str(ex))
            return None
        
    def new_folder_for_asset(self,assetid,folder_rep):
        """
        Create a new folder in ECMS corresponding to an Assetic asset.
        Update the Assetic asset with the folder ID and ECMS type
        param assetid: Assetic asset ID (GUID or user friendly asset ID)
        param folder_rep: assetic.ECMSFolderRepresentation
        """   
        #get asset details
        asset = self.asset_tools.get_asset(assetid,["ExternalOtherSystem1ID"])
        try:
            assetguid = asset["Id"]
            assetid = asset["AssetId"]
            assetname = asset["AssetName"]
            externalid = asset["Attributes"]["ExternalOtherSystem1ID"]
        except Exception as ex:
            self.logger.error(str(ex))
            return 1
        if externalid != None and externalid.strip() != "":
            msg = "Asset {0} already has folder {1}".format(assetid,externalid)
            self.logger.warn(msg)
            return -1            
        
##        ##set assetic guid
##        folder_rep.asseticid = assetname

        #create the folder using the instantiated plugin
        new_folder = self.ecms_plugin.create_folder(folder_rep)
        if new_folder.ecmsid != None:
            ecmsid = new_folder.ecmsid
        else:
            return 1
        ecms_name = self.ecms_name
        
        #update assetic with the folder ID and ECMS type
        asset_rep = ComplexAssetRepresentation()
        asset_rep.id = assetguid
        #could also set ExternalOtherSystem1Flag?
        asset_rep.attributes = {"ExternalOtherSystem1Name":ecms_name,
                                "ExternalOtherSystem1ID":ecmsid}
        if new_folder.ecmsid2 != None:
            asset_rep.attributes["ExternalOtherSystem1ID2"] = new_folder.ecmsid2
        return self.asset_tools.update_complex_asset(asset_rep)
        
    def move_document_to_ecms(self,ecms_doc_rep,asset_as_parent = True,delete = True):
        """
        Download the document from Assetic and upload to ECMS
        Then delete document from Assetic
        :Param ecms_doc_rep: assetic.ECMSDocumentRepresentation which has the
        document details
        :Param asset_as_parent: If True then the parent folder will be the asset
        folder.  This means a work order document is put in the asset folder
        :Param delete: document is removed from Assetic once the document is
        saved in the ECMS.  Set False to retain in Assetic. For active document
        such as in active Work Orders or Work Requests the document
        is always retained until the work order/work request is closed.
        Returns: 0 = Success, 1 = Error, -1 skipped
        """
        if isinstance(ecms_doc_rep,ECMSDocumentRepresentation) != True:
            msg ="ecms_doc_rep is not the required type: '{0}'".format(
                "ECMSDocumentRepresentation")
            self.logger.error(msg)
            return 1
        doc_rep = ecms_doc_rep.assetic_doc_representation
        docid = doc_rep.id
        if docid == None:
            msg = "Document ID not set in ecms_doc_rep. "\
                  "Unable to get document from Assetic."
            self.logger.error(msg)
            return 1

        if doc_rep.status == None:
            #get the document metadata
            docmetadata = self.get_document_metadata_by_id(docid)
            #set the values in the doc_rep
            # doc_rep = self.dict_to_object(docmetadata,doc_rep)
            # TODO: verify this desrialises correctly
            doc_rep = self.api_client.deserialize(docmetadata,
                                                  "DocumentRepresentation")
            if not doc_rep.status:
                doc_rep.status = "Active"
            doc_rep.parent_type = "All"

        #make sure doc group is set else update fails
        if doc_rep.document_group == None or \
           doc_rep.document_group == 0:
            ##will not be able to update this, but not treat as error
            msg ="Document Group not set for document: '{0}'.  "\
                  "This document will be ignored".format(docid)
            self.logger.warning(msg)            
            return -1

        ##check doc status - may already be deleted
        if doc_rep.status == 500:
            ##wil not process this document, but not treat as error
            msg ="Document already deleted: '{0}'.  "\
                  "This document will be ignored".format(docid)
            self.logger.warning(msg)            
            return -1
        
        ##check if doc exists (has external ID)
        doc_rep.ecmsid = None
        if doc_rep.external_id != None and doc_rep.external_id.strip() != "":
            ##doc exists
            doc_rep.ecmsid = doc_rep.external_id
        
        assetid = None
        assetguid = None
        can_delete = False
        ##now process the document unless active no asset
        if doc_rep.document_work_order != None:
            ##process the file if there is an asset
            if doc_rep.document_work_order.document_asset != None:
                assetguid = doc_rep.document_work_order.document_asset.id
                assetid = doc_rep.document_work_order.document_asset.asset_id
                wkoguid = doc_rep.document_work_order.work_order_id
                friendlyid = doc_rep.document_work_order.friendly_id
                wkostatus = self.get_wko_status(wkoguid)
                if wkostatus == "ASSESS" or wkostatus == "COMP" or \
                   wkostatus == "CAN":
                    can_delete = True
                ##prefix document label with wko number
                doc_rep.label = "{0}-{1}".format(
                    doc_rep.document_work_order.friendly_id,doc_rep.label)
        if doc_rep.document_work_request != None:
            ##process the file if there is an asset
            if doc_rep.document_work_request.document_asset != None:
                assetguid = doc_rep.document_work_request.document_asset.id
                assetid = doc_rep.document_work_request.document_asset.asset_id
                wrguid = doc_rep.document_work_request.work_request_id
                friendlyid = doc_rep.document_work_request.friendly_id
                wrstatus = self.get_workrequest_status(wrguid)
                if wrstatus == "Resolved" or wrstatus == "Rejected":
                    can_delete = True
                ##prefix document label with wr number
                doc_rep.label = "{0}-{1}".format(
                    doc_rep.document_work_request.friendly_id,doc_rep.label)
        if doc_rep.document_asset != None:
            assetguid = doc_rep.document_asset.id
            assetid = doc_rep.document_asset.asset_id
            can_delete = True

        if asset_as_parent == True:
            if assetguid == None or \
               assetguid == "00000000-0000-0000-0000-000000000000":
                ##will not be able to update this, but not treat as error
                msg ="Document asset not set for document: '{0}'.  "\
                      "This document will be ignored".format(docid)
                self.logger.warning(msg)            
                return -1
            
            ecmsparent = self.get_ecmsid_for_asset(assetguid)
            if ecmsparent.strip() == "":
                ##will not be able to update this, but not treat as error
                msg ="Document parent not set for Document: {0}, Asset guid: {1}"\
                      "; Asset ID: {2}. This document will be ignored".format(
                          docid,assetguid,assetid)
                self.logger.warning(msg)            
                return -1
            ecms_doc_rep.ecmsparent = ecmsparent
 
        if ecms_doc_rep.ecmsparent == None:
                ##will not be able to update this, but not treat as error
                msg ="Document parent not set for Document: {0}, "\
                      "This document will be ignored".format(
                          docid,assetguid,assetid)
                self.logger.warning(msg)            
                return -1            
        if doc_rep.ecmsid == None:
            ##get the document from Assetic
            docdata,docfilename = self.download_doc_with_filename(docid)
            if docdata == None:
                return 1

            file_rep = FilePropertiesRepresentation()
            file_rep.filecontent = docdata
            file_rep.name = docfilename
            doc_rep.file_property = file_rep

            #now upload document to ECMS
            moved_doc = self.ecms_plugin.create_document(ecms_doc_rep)
            if moved_doc.ecmsid == None:
                return 1

            ##update document 'External ID' with 'ECMS id'
            update_doc_rep = DocumentRepresentation()
            update_doc_rep.id = doc_rep.id
            update_doc_rep.external_id = str(moved_doc.ecmsid)
            chk = self.update_document_metadata(update_doc_rep,False)
            if chk > 0:
                return 1
            msg ="Document: {0} uploaded, Asset guid: {1}"\
                  "; Asset ID: {2}.".format(
                      docid,assetguid,assetid)
            self.logger.debug(msg) 
        ##Now delete 
        chk = 0
        if can_delete == True and delete == True:
            ##delete the document
            chk = self.delete_doc(doc_rep.id)
        return chk

    def get_ecmsid_for_asset(self,assetguid):
        """
        Get the ecms ID for the given asset
        Param docid: asset GUID
        Returns: ECMS ID or None
        """
        attributes = ["ExternalOtherSystem1Name",
                    "ExternalOtherSystem1ID"]
        try:
            asset = self.asset_tools.get_asset(assetguid,attributes)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return ""
        ecmsid = asset["Attributes"]["ExternalOtherSystem1ID"]
        if ecmsid == None:
            ecmsid = ""
        return ecmsid
        
    def download_doc_with_filename(self,docid):
        """
        Download the document and get the filename
        Param docid: document GUID
        Returns: Tuple of document and filename
        """
        try:
            getfile = self.documentapi.document_get_document_file_with_http_info(docid)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return None,None
        except Exception as ex:
            self.logger.error("Error downloading file {0}".format(
                str(ex)))
            return None,None            

        self.logger.debug("Downloaded document {0}".format(docid))
        filename = None
        if getfile != None and len(getfile) == 3:
            if "Content-Disposition" in getfile[2]:
                ##get document name from response. The response is a tuple
                if "attachment" in getfile[2]["Content-Disposition"] \
                and "filename=" in getfile[2]["Content-Disposition"]:
                    filename = getfile[2]["Content-Disposition"].split(
                        "filename=",1)[1]
                if '"' in filename or "'" in filename:
                    filename = filename[1:-1]
            if filename == None:
                msg = "Filename not associated with document"
##                msg = "Unable to get document name. Make sure document tools"\
##                      "api is initated with asseticSDK.client_for_docs"\
##                      "Document ID={0}".format(docid)
                self.logger.error(msg)
                return None,None
            filedata = getfile[0]
        else:
            #No file data
            msg = "File not downloaded or is empty.  Document ID={0}".format(
                docid)
            self.logger.error(msg)
            return None,None            
        return filedata,filename

    def update_document_metadata(self,doc_rep,setnulls=False):
        """
        Update document metadata
        Param doc_rep: DocumentRepresentation
        :param setnulls: optional, default is False.  If True then empty fields
        in the passed in object will be set to null, otherwise the default is to
        keep the existing value of fields with no defined value in the object
        Returns: 0 = Success, >0 = Error
        """
        if isinstance(doc_rep,\
        DocumentRepresentation) != True:
            msg ="update_document_metadata doc_rep param should be of type "\
                "DocumentRepresentation"
            self.logger.error(msg)
            return 1
        docid = doc_rep.id
        if docid == None:
            msg ="Document ID not defined for update_document_metadata"
            self.logger.error(msg)
            return 1
        
        if setnulls == False:
            current = self.get_document_metadata_by_id(docid)
            if current == None:
                return 1
            ##loop through the passed in object and set the values for
            ##null fields to be that of the current component values
            for k,v in six.iteritems(doc_rep.attribute_map):
                if getattr(doc_rep,k) == None \
                and v in current and current[v] != None and \
                k not in ("links","embedded"):
                    if k == "status":
                        setattr(doc_rep,k,"Active")
                    elif k == "parent_type":
                        setattr(doc_rep,k,"All")
                    else:
                        setattr(doc_rep,k,current[v])
        try:
            doc = self.documentapi.document_put(docid,doc_rep)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return e.status
        return 0

    def get_document_metadata_by_id(self,docid):
        """
        Get the document metadata by document GUID
        :params docid: the document GUID to get metadata for
        :return: DocumentRepresentation
        If error then None
        """
        try:
            doc = self.documentapi.document_get_0(docid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return None
        return doc

    def delete_doc(self,docid):
        """
        Set the document status as deleted.  Will remove the document itself
        from the server, but the metadata will remain.  Also removes links it
        had the the asset/work order etc.
        :params doc_id: the document to delete
        :return: 0 = success,>0 = error
        """
        try:
            doc = self.documentapi.document_delete_document_file_by_id(docid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return e.status        
        return 0
    
    def get_workrequest_status(self,wrguid):
        """
        Get the status of a work request
        Param wrguid: the unique guid of the work order
        Returns: 0 = Success, >0 = Error
        """
        wr = self.get_workrequest(wrguid)
        if wr == None:
            return None
        else:
            return wr["WorkRequestStatus"]
        
    def get_workrequest(self,wrguid):
        """
        Get the status of a work request
        Param wrguid: the unique guid of the work request
        Returns: 0 = Success, >0 = Error
        """
        try:
            wr = self.workrequestapi.work_request_get(wrguid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return None
        return wr

    def get_wko_status(self,wkoguid):
        """
        Get the status of a work order
        Param wkoguid: the unique guid of the work order
        Returns: 0 = Success, >0 = Error
        """
        wko = self.get_wko(wkoguid)
        if wko == None:
            return None
        else:
            return wko["Status"]
        
    def get_wko(self,wkoguid):
        """
        Get a work order given unique guid
        Param wkoguid: the unique guid of the work order
        Returns: 0 = Success, >0 = Error
        """
        try:
            wko = self.workorderapi.work_order_integration_api_get_0(wkoguid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status,e.reason,e.body))
            return None
        return wko

    # def dict_to_object(self,in_dict,object_rep):
    #     """
    #     Given a json object (response from an api call) convert to the
    #     representation object.
    #     Param in_dict: the json/dictionary of values
    #     Param object_rep: The object to write the dictionary values to
    #     Returns: object_rep
    #     """
    #     for k,v in six.iteritems(object_rep.attribute_map):
    #         if getattr(object_rep,k) == None \
    #         and v in in_dict and in_dict[v] != None and \
    #         k not in ("links","embedded"):
    #             if k == "status":
    #                 setattr(object_rep,k,"Active")
    #             elif k == "parent_type":
    #                 setattr(object_rep,k,"All")
    #             else:
    #                 if "Assetic3IntegrationRepresentations" in object_rep.swagger_types[k] and \
    #                 "list[" not in object_rep.swagger_types[k]:
    #                     sub = eval("{0}".format(object_rep.swagger_types[k]))()
    #                     sub = self.dict_to_object(in_dict[v],sub)
    #                     setattr(object_rep,k,sub)
    #                 else:
    #                     setattr(object_rep,k,in_dict[v])
    #     return object_rep
    
class ECMSPluginBase(object):
    """
    Base class for common ECMS integration activities
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_folder(self,folder_representation):
        return folder_representation

    @abc.abstractmethod
    def create_document(self,document_representation):
        return document_representation
    
class ECMSDocumentRepresentation(object):
    """"
    A structure for document information to be passed between assetic
    and external enterprise content management system (ECMS)
    :param assetic_doc_representation: DocumentRepresentation
    :param ecmsid: unique id of document in ECMS.  Leave null unless updating existin document
    :param ecmsparent: container id/folder location to put document in. Can be None
    if document is to be loaded against Asset
    :param ecmsdoctype: if ECMS requires. In HP CM it is the 'document type'
    :param ecmsclassification: if ECMS requires.  In HP CM it is the 'Classification'
    :param ecmslevel: if ECMS requires.  In HP CM it is the level number
    :param ecmsauthor: if ECMS requires document author
    """
    def __init__(self,assetic_doc_representation=None,ecmsid=None,ecmsparent=None,ecmsclassification=None,ecmsdoctype=None,ecmslevel=None,ecmsauthor=None,tags=list()):

        self.fieldtypes = {
            "assetic_doc_representation": "DocumentRepresentation",
            "ecmsid":"str",
            "ecmsparent":"str",
            "ecmsdoctype":"str",
            "ecmsclassification":"str",
            "ecmslevel":"str",
            "ecmsauthor":"str",
            "tags":"list[ECMSTagRepresentation]"
        }

        self._assetic_doc_representation = assetic_doc_representation
        self._ecmsid = ecmsid
        self._ecmsclassification = ecmsclassification
        self._ecmsparent = ecmsparent
        self._ecmsdoctype = ecmsdoctype
        self._ecmslevel = ecmslevel
        self._ecmsauthor = ecmsauthor
        self._tags = tags
        
        api_client = ApiClient()           
        self.logger = api_client.configuration.packagelogger

    @property
    def assetic_doc_representation(self):
        return self._assetic_doc_representation
    @assetic_doc_representation.setter
    def assetic_doc_representation(self,assetic_doc_representation):
        ##check the type is correct
        if not isinstance(assetic_doc_representation, DocumentRepresentation):
            msg = "assetic_doc_representation is not the required type: '{0}'"\
                  "".format("DocumentRepresentation")
            self.logger.error(msg)
            self._assetic_doc_representation = None
        else:
            self._assetic_doc_representation = assetic_doc_representation
        
    @property
    def ecmsid(self):
        return self._ecmsid
    @ecmsid.setter
    def ecmsid(self,ecmsid):
        self._ecmsid = ecmsid

    @property
    def ecmsparent(self):
        return self._ecmsparent
    @ecmsparent.setter
    def ecmsparent(self,ecmsparent):
        self._ecmsparent = ecmsparent

    @property
    def ecmsclassification(self):
        return self._ecmsclassification
    @ecmsclassification.setter
    def ecmsclassification(self,ecmsclassification):
        self._ecmsclassification = ecmsclassification
        
    @property
    def ecmsdoctype(self):
        return self._ecmsdoctype
    @ecmsdoctype.setter
    def ecmsdoctype(self,ecmsdoctype):
        self._ecmsdoctype = ecmsdoctype

    @property
    def ecmslevel(self):
        return self._ecmslevel
    @ecmslevel.setter
    def ecmslevel(self,ecmslevel):
        self._ecmslevel = ecmslevel

    @property
    def ecmsauthor(self):
        return self._ecmsauthor
    @ecmsauthor.setter
    def ecmsauthor(self,ecmsauthor):
        self._ecmsauthor = ecmsauthor

    @property
    def tags(self):
        return self._tags
    @tags.setter
    def tags(self,tags):
        ##check the type is correct
        if isinstance(tags,list) != True:
            msg ="tags is not the required type: 'list'"
            self.logger.error(msg)
            self._tags == list()
        else:
            if False in [isinstance(e,ECMSTagRepresentation) for e in tags]:
                msg ="tags list values are not the required type: '{0'".format(
                    "ECMSTagRepresentation")
                self.logger.error(msg)
                self._tags == list()
            else:
                self._tags = tags
            
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
        return pformat(self.to_dict())

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

class ECMSFolderRepresentation(object):
    """"
    A structure for document information to be passed between assetic
    and external enterprise content management system (ECMS)
    """
    def __init__(self,ecmsid=None,title=None,asseticid=None,ecmsparent=None,ecmsfoldertype=None,ecmsclassification=None,ecmslevel=None,ecmsid2=None,ecmsauthor=None,tags=list()):

        self.fieldtypes = {
            "ecmsid":"str",
            "title":"str",
            "asseticid":"str",
            "ecmsparent":"str",
            "ecmsfoldertype":"str",
            "ecmsclassification":"str",
            "ecmslevel":"str",
            "ecmsid2":"str",
            "ecmsauthor":"str",
            "tags":"list[ECMSTagRepresentation]"
        }

        self._ecmsid = ecmsid
        self._title = title
        self._asseticid = asseticid        
        self._ecmsparent = ecmsparent
        self._ecmsfoldertype = ecmsfoldertype
        self._ecmsclassification = ecmsclassification
        self._ecmslevel = ecmslevel
        self._ecmsid2 = ecmsid2
        self._ecmsauthor = ecmsauthor
        self._tags = tags
        
        api_client = ApiClient()        
        self.logger = api_client.configuration.packagelogger
        
    @property
    def ecmsid(self):
        return self._ecmsid
    @ecmsid.setter
    def ecmsid(self,ecmsid):
        self._ecmsid = ecmsid

    @property
    def title(self):
        return self._title
    @title.setter
    def title(self,title):
        self._title = title

    @property
    def asseticid(self):
        return self._asseticid
    @asseticid.setter
    def asseticid(self,asseticid):
        self._asseticid = asseticid
        
    @property
    def ecmsparent(self):
        return self._ecmsparent
    @ecmsparent.setter
    def ecmsparent(self,ecmsparent):
        self._ecmsparent = ecmsparent

    @property
    def ecmsclassification(self):
        return self._ecmsclassification
    @ecmsclassification.setter
    def ecmsclassification(self,ecmsclassification):
        self._ecmsclassification = ecmsclassification

    @property
    def ecmsfoldertype(self):
        return self._ecmsfoldertype
    @ecmsfoldertype.setter
    def ecmsfoldertype(self,ecmsfoldertype):
        self._ecmsfoldertype = ecmsfoldertype

    @property
    def ecmslevel(self):
        return self._ecmslevel
    @ecmslevel.setter
    def ecmslevel(self,ecmslevel):
        self._ecmslevel = ecmslevel
        
    @property
    def ecmsid2(self):
        return self._ecmsid2
    @ecmsid2.setter
    def ecmsid2(self,ecmsid2):
        self._ecmsid2 = ecmsid2

    @property
    def ecmsauthor(self):
        return self._ecmsauthor
    @ecmsauthor.setter
    def ecmsauthor(self,ecmsauthor):
        self._ecmsauthor = ecmsauthor

    @property
    def tags(self):
        return self._tags
    @tags.setter
    def tags(self,tags):
        ##check the type is correct
        if isinstance(tags,list) != True:
            msg ="tags is not the required type: 'list'"
            self.logger.error(msg)
            self._tags == list()
        else:
            if False in [isinstance(e,ECMSTagRepresentation) for e in tags]:
                msg ="tags list values are not the required type: '{0'".format(
                    "ECMSTagRepresentation")
                self.logger.error(msg)
                self._tags == list()
            else:
                self._tags = tags
        
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
        return pformat(self.to_dict())

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

class ECMSTagRepresentation(object):
    """"
    A structure for tags to be assigned to documents/folders between assetic
    and external enterprise content management system (ECMS)
    """
    def __init__(self,tagfield=None,tagvalue=None):

        self.fieldtypes = {
            "tagfield":"str",
            "tagvalue":"str"
        }

        self._tagfield = tagfield
        self._tagvalue = tagvalue
        
    @property
    def tagfield(self):
        return self._tagfield
    @tagfield.setter
    def tagfield(self,tagfield):
        self._tagfield = tagfield

    @property
    def tagvalue(self):
        return self._tagvalue
    @tagvalue.setter
    def tagvalue(self,tagvalue):
        self._tagvalue = tagvalue
        
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
        return pformat(self.to_dict())

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
