# coding: utf-8
"""
    assetic.FileSystemDocuments  (file_system.py)
    Tools to assist with integrating documents with local file server.
"""
from __future__ import absolute_import
from ..documents import ECMSPluginBase
import os
import logging

class FileSystemDocuments(ECMSPluginBase):
    """
    Class to manage file system based document integration
    """

    def __init__(self):
        """
        Initialise the file system integration plugin
        """
        logger = logging.getLogger(__name__)
        self.logger = logger 

    def create_folder(self,folder_rep):
        """
        Create a new folder on file server
        :param folder_rep: an instance of assetic.ECMSFolderRepresentation
        which contains the information required to create a folder
        :returns: folder_rep with the full path assigned to the ecmsid property
        """
        parentfolder = folder_rep.ecmsparent
        currentname = folder_rep.ecmsid    #use if updating folder
        foldername = folder_rep.title
        #set to None to indicate failure. Will set to full file name if success
        folder_rep.ecmsid = None
        
        ##make sure we have the basic data
        if parentfolder == None or foldername == None:
            msg = "Please define ecmsparent for parent folder name and"\
                  " title for name of folder to create under parent. "\
                  "Values provided were {0} and {1} respectively".format(
                      parentfolder,foldername)
            return folder_rep
        
        ##check path is valid
        parentfolder = os.path.normpath(parentfolder)
        if os.path.isdir(parentfolder) == False:
            msg = "Parent folder [{0}] does not exist.  Please create".format(
                parentfolder)
            self.logger.error(msg)
            return folder_rep
        
        ##now either create or rename folder
        fullfoldername = os.path.join(parentfolder,foldername)
        folder_rep.ecmsid = None
        if (currentname != None and os.path.isdir(currentname) == True) and \
           os.path.isdir(foldername) == False:
            #updating an existing folder name
            fullcurrentname = os.path.join(parentfolder,currentname)
            chk = self.update_folder_name(fullcurrentname, fullfoldername)
            if chk == 0:
                folder_rep.ecmsid = new_name
        else:
            ##create folder
            try:
                os.mkdir(fullfoldername)
            except Exception as ex:
                msg = "Error creating folder {0}: {1}".format(
                fullfoldername,str(ex))
                self.logger.error(msg)
            else:
                folder_rep.ecmsid = fullfoldername
            return folder_rep
        
    def create_document(self,doc_rep):
        """
        Create a new document in HP CM via web service
        Will optionally update a document if the ecmsid property is set
        :param doc_rep: an instance of assetic.ECMSDocumentRepresentation
        which contains the information required to create a document in HP CM
        :returns: doc_rep with the HP CM URI assigned to the ecmsid property
        """
        rectype = doc_rep.ecmsdoctype
        folder = doc_rep.ecmsparent
        data = doc_rep.assetic_doc_representation.file_property.filecontent
        filename = doc_rep.assetic_doc_representation.file_property.name

        doc_rep.ecmsid = None
        ##check that parent folder exists
        if os.path.isdir(folder) == False:
            return doc_rep
        folder = os.path.normpath(folder)        
        fullfilename = os.path.join(folder,filename)
        if type(data) == bytes:
            ##cater for different binary data
            with open( fullfilename, "wb" ) as out_file:
                out_file.write(data)
                self.logger.debug("Created file: {0}".format(fullfilename))
        elif type(data) == str:
            ##string data
            with open( fullfilename, "w", newline="",encoding="utf-8" ) as out_file:
                try:
                    out_file.write(data)
                    self.logger.debug("Created file: {0}".format(fullfilename))
                except UnicodeEncodeError as ex:
                    msg = "Document save, encoding error: {0}".format(str(ex))
                    self.logger.error(msg)
                    return doc_rep
         
        ##if successful set ecmsid
        doc_rep.ecmsid = fullfilename
        return doc_rep
    
    def update_folder_name(self,parent_folder, old_name, new_name):
        """
        Rename a folder(expects full paths)
        :param old_name: name of folder to change
        :param new_name: new name of folder
        :return: 0 if no error, else error >0
        """
        try:
            os.rename(old_name, new_name)
        except Exception as ex:
            msg = "Error renaming folder {0} to {1}: {2}".format(
                old_name, new_name,str(ex))
            self.logger.error(msg)
            return 1
        return 0

