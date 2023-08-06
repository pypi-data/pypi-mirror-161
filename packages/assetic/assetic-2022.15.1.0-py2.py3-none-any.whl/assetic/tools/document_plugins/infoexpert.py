# coding: utf-8
"""
    assetic.InfoExpertTools
    Tools to assist with integrating with InfoExpert, an ECMS
    InfoExpert is also branded as MagiQ Documents
"""
import os
import shutil
import sys
import base64
import six
try:
    import configparser as configparser
except:
    import ConfigParser as configparser
import logging
try:
    from suds.client import Client  #SOAP module (pypy suds-py3 or suds if py2)
except ImportError as ex:
    msg = "InfoExpert integration requires package 'suds-py3'"\
              "Please install suds, i.e. 'pip install suds-py3'"
    if six.PY2:
        msg = "InfoExpert integration requires package 'suds'"\
              "Please install suds, i.e. 'pip install suds'"
    raise ImportError(msg)

import abc
from ..documents import ECMSPluginBase

class HP_CMTools(ECMSPluginBase):
    """
    Class to manage HP Content Manager integration
    """

    def __init__(self,ini=None):
        """
        Initialise the InfoExpert document integration plugin
        :param ini: ini file with InfoExpert connection details.  If none then
        will look for $appdata\\Assetic\\infoexpert_config.ini
        """
        logger = logging.getLogger(__name__)
        self.logger = logger 

        ##get settings and create http session
        settings = configparser.ConfigParser()
        if ini == None:
            appdata = os.environ.get("APPDATA")
            inifile = os.path.abspath(
                appdata + "\\Assetic\\infoexpert_config.ini")
            if os.path.isfile(inifile) == False:
               self.logger.error("InfoExpert configuration file not found") 
               return None     
        settings.read(inifile)
        # Apply assetic config settings
        try:
            host = settings.get('environment', 'url')
            username = settings.get('auth', 'username')
            password = settings.get('auth', 'password')
            token = settings.get('auth', 'api_key')
        except Exception as ex:
            msg = "Error reading InfoExpert configuration file. \r\n\{0}"\
                  "".format(str(ex))
            self.logger.error(msg)
            raise Exception(msg)

        if host == None or host.strip() == "":
            self.logger.error("InfoExpert configuration for host is undefined") 
            return None            
        ##InfoExpert suds instance
        self.client = Client(host)

        #must have a token. Can get one using username & pwd if token
        #not in ini.
        #
        #Do we need to test token and if fail get new one?
        #
        if token == None or token.strip() == "":
            resp = self.client.service.AuthenticateUser(username,password)
            self.token = resp.response._ticket
        else:
            self.token = token

    def create_folder(self,folder_rep):
        """
        Create a new folder in InfoExpert via web service
        :param folder_rep: an instance of assetic.ECMSFolderRepresentation
        which contains the information required to create a folder
        :returns: folder_rep with the InfoExpert ID assigned to the ecmsid
        property
        """

        parentfolder = folder_rep.ecmsparent
        newfolder = folder_rep.title
        fullpath = parentfolder + "/" + newfolder
        chk = self.client.service.FolderExists(self.token,parentfolder)
        if chk.response._success == "false":
            msg = "Parent Folder {0} does not exist prior to creation of"\
                  " folder {1}".format(parentfolder,newfolder)
            self.logger.debug(msg)
            ##To DO# Try to create folder
        else:
            chk = self.client.service.FolderAccessAllowed(self.token,filedir,38)
            if chk.response._success == "false":
                msg = "Create Folder [{0}] in Folder [{0}] access denied."\
                      "".format(newfolder,parentfolder)
            self.logger.error(msg)
            return folder_rep
        
        chk = self.client.service.FolderExists(self.token,fullpath)
        if chk.response._success == "true":
            msg = "Folder {0} already exists.".format(fullpath)
            self.logger.debug(msg)
        else:
            resp = self.client.service.CreateFolder(self.token,fullpath)
            if resp.response._success == "false":
                msg = "Folder {0} not created: {1}".format(
                    fullpath,resp.response._error)
                self.logger.error(msg) 
        return folder_rep

    def create_document(self,doc_rep):
        """
        Create a new document in InfoExpert via web service
        Will optionally update a document if the ecmsid property is set
        :param doc_rep: an instance of assetic.ECMSDocumentRepresentation
        which contains the information required to create a document in
        InfoExpert
        :returns: doc_rep with the InfoExpert ID assigned to the ecmsid property
        """

        filename = doc_rep.assetic_doc_representation.file_property.name
        if filename == None or filename.strip() == "":
            filename = "unknownfilename"

        ##for document location get folder and append file name
        #filedir ="Assetic Business Classification Scheme/Roads/Design And Construction/Paving/Work Order/"
        filedir = doc_rep.doc_rep.ecmsparent

        ##check if path already exists.
        ##Note that UploadDocument can create path anyway.
        chk = self.client.service.FolderExists(self.token,filedir)
        if chk.response._success == "false":
            msg = "Folder {0} does not exist prior to document upload.".format(
                        filedir)
            self.logger.error(msg)
            ##To DO# Try to create folder
        else:
            chk = self.client.service.FolderAccessAllowed(self.token,filedir,37)
            if chk.response._success == "false":
                msg = "Create document in folder {0} access denied.".format(
                        filedir)
            self.logger.error(msg)
            return doc_rep
            
        fullfilename = filedir + filename

        ##upload document itself
        docdata = doc_rep.assetic_doc_representation.file_property.filecontent

        resp = self.client.service.UploadDocument(self.token,
                                    fullfilename, docdata)

        ##get the ID of the created document
        doc = self.client.service.GetDocument(self.token,fullfilename)
        if doc.response._success == "false":
            msg = "Unable to retrieve newly uploaded document {0}.".format(
                        fullfilename)
            self.logger.error(msg)
        else:
            doc_rep.ecmsid = doc.response.document._DocumentID
        return doc_rep
