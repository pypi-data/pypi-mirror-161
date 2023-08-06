# coding: utf-8
"""
    assetic.HP_CMTools  (hp_cm.py)
    Tools to assist with integrating with HP Content Manager (HP CM).
    HP CM formerly known as RM8 and TRIM
"""
from __future__ import absolute_import

try:
    import requests
except ImportError as ex:
    msg = "HP CM integration requires package 'requests'"\
          "Please install packages 'requests' and 'requests_ntlm'"
    raise ImportError(msg)
try:
    from requests_ntlm import HttpNtlmAuth
except ImportError as ex:
    msg = "HP CM integration requires package 'requests_ntlm'"\
          "Please install package 'requests_ntlm'"
    raise ImportError(msg)
import os
import logging
try:
    import configparser as configparser
except:
    import ConfigParser as configparser
from ..documents import ECMSPluginBase


class HP_CMTools(ECMSPluginBase):
    """
    Class to manage HP Content Manager integration
    """

    def __init__(self,ini=None):
        """
        Initialise the HP CM document integration plugin
        :param ini: ini file with HP CM connection details.  If none then
        will look for $appdata\\Assetic\\trim_config.ini
        """
        logger = logging.getLogger(__name__)
        self.logger = logger 

        ##get settings and create http session
        settings = configparser.ConfigParser()
        if ini == None:
            appdata = os.environ.get("APPDATA")
            inifile = os.path.abspath(appdata + "\\Assetic\\trim_config.ini")
            if os.path.isfile(inifile) == False:
                self.logger.error("HP CM configuration file not found")
                return
        settings.read(inifile)
        # Apply assetic config settings
        try:
            host = settings.get('environment', 'url')
            username = settings.get('auth', 'username')
            password = settings.get('auth', 'password')
        except Exception as e:
            msg = "Error reading HP CM configuration file. \r\n\{0}".format(
                str(e))
            self.logger.error(msg)
            raise Exception(msg)
        self.host = host
        self.hp_cm_session = self.new_hp_cm_session(username,password)

    def new_hp_cm_session(self,username,password):
        """
        Create a new requests session using NTLM authentication to
        HP CM web service
        :param username: NTLM username
        :param password: NTLM password
        :return: requests session
        """
        session = requests.Session()
        session.auth = HttpNtlmAuth(username, password, session)

        return session

    def create_folder(self,folder_rep):
        """
        Create a new folder in HP CM via web service
        :param folder_rep: an instance of assetic.ECMSFolderRepresentation
        which contains the information required to create a folder in HP CM
        :returns: folder_rep with the HP CM URI assigned to the ecmsid property
        and the HP CM Record Number assigned to the ecmsid2 property
        """
        headers = {"Accept": "application/json"}
        self.hp_cm_session.headers.update(headers)

        recordnumber = folder_rep.ecmsid2
        reccontainer = folder_rep.ecmsparent
        recorduri = None    # use if updating folder
        recordlevel = folder_rep.ecmslevel
        author = folder_rep.ecmsauthor
        
        payload = {
            "RecordExternalReference": (None, folder_rep.asseticid),
            "Validate": (None, "true"),
            "RecordTitle": (None, folder_rep.title),
            "RecordRecordType": (None, folder_rep.ecmsfoldertype)
            }
        if recorduri is not None:
            # updating an existing document so set it's URI in payload
            payload["Uri"] = (None, recorduri)
        if reccontainer is not None:
            payload["RecordContainer"] = (None, reccontainer)
        if folder_rep.ecmsclassification is not None:
            payload["RecordClassification"] = (None,
                                               folder_rep.ecmsclassification)
        if recordnumber is not None:
            payload["RecordNumber"] = (None, recordnumber)
        if recordlevel is not None:
            payload["RecordLevel"] = (None, recordlevel)
        if author is not None:
            payload["RecordAuthor"] = (None, author)

        # add tags
        for tag in folder_rep.tags:
            payload[tag.tagfield] = (None, tag.tagvalue)
            
        endpoint = "{0}/Record/".format(self.host)

        response = self.hp_cm_session.post(endpoint, files=payload)

        if response.status_code != requests.codes.ok:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.logger.error("HP CM folder create failed with error: "
                                  "{0} {1}".format(str(e), response.text))
            return folder_rep
        responsedata = response.json()

        if len(responsedata["Results"]) > 0:
            results = responsedata["Results"][0]
            uri = results["Uri"]
            if uri == 0:
                errmsg = responsedata["ResponseStatus"]["Message"]
                self.logger.error("Error creating folder: {0}".format(errmsg))
                folder_rep.ecmsid = None
                folder_rep.ecmsid2 = None
            else:
                folder_rep.ecmsid = uri
                folder_rep.ecmsid2 = None
                try:
                    folder_rep.ecmsid2 = results["RecordNumber"]["Value"]
                except:
                    pass
            return folder_rep
        else:
            return folder_rep
        
    def create_document(self, doc_rep):
        """
        Create a new document in HP CM via web service
        Will optionally update a document if the ecmsid property is set
        :param doc_rep: an instance of assetic.ECMSDocumentRepresentation
        which contains the information required to create a document in HP CM
        :returns: doc_rep with the HP CM URI assigned to the ecmsid property
        """
        headers = {"Accept": "application/json"}
        self.hp_cm_session.headers.update(headers)
        endpoint = "{0}/Record/".format(self.host)

        rectype = doc_rep.ecmsdoctype
        rectitle = doc_rep.assetic_doc_representation.label
        recordnumber = None
        externalreference = doc_rep.assetic_doc_representation.id
        reccontainer = doc_rep.ecmsparent
        recorduri = doc_rep.ecmsid
        recordlevel = doc_rep.ecmslevel
        recdata = doc_rep.assetic_doc_representation.file_property.filecontent
        filename = doc_rep.assetic_doc_representation.file_property.name
        author = doc_rep.ecmsauthor
        classification = doc_rep.ecmsclassification
        
        payload = {
            "RecordExternalReference": (None, externalreference),
            "Validate": (None, "true"),
            "RecordTitle": (None, rectitle),
            "RecordRecordType": (None, rectype)
            }
        if recorduri is not None:
            # updating an existing document so set it's URI in payload
            payload["Uri"] = (None, recorduri)
        if reccontainer is not None:
            payload["RecordContainer"] = (None, reccontainer)
        if recordnumber is not None:
            payload["ExpandedNumber"] = (None, recordnumber)
        if filename is not None:
            payload["Files"] = (filename,recdata)
        if recordlevel is not None:
            payload["RecordLevel"] = (None, recordlevel)
        if author is not None:
            payload["RecordAuthor"] = (None, author)
        if classification is not None:
            payload["RecordClassification"] = (None,classification)

        # add tags
        for tag in doc_rep.tags:
            payload[tag.tagfield] = (None, tag.tagvalue)
            
        try:    
            response = self.hp_cm_session.post(endpoint, files=payload)
        except requests.exceptions.RequestException as e:
            self.logger.error("HP CM Document create in failed with error {0}"
                              "".format(str(e)))
            doc_rep.ecmsid = None
            return doc_rep
        
        doc_rep.ecmsid = None
        if response.status_code != requests.codes.ok:
            try:
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.logger.error("HP CM Document create failed with error "
                                  "{0} {1}".format(str(e), response.text))
            return doc_rep
        responsedata = response.json()
        if len(responsedata["Results"]) > 0:
            results = responsedata["Results"][0]
            uri = results["Uri"]
            if uri == 0:
                errmsg = responsedata["ResponseStatus"]["Message"]
                self.logger.error("Error creating document in HP CM: {0}"
                                  "".format(errmsg))
            else:
                doc_rep.ecmsid = uri
        return doc_rep


