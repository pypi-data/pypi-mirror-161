# coding: utf-8

"""
    Assetic.bulk_export.py
    Tools to facilitate bulk export of data from assetic
    * Syncing exported data to a local sql server database
    * Export Search Profile data to csv
    * Export asset, components, dims to csv as a consolidated record
    
    DB Sync Checks if there are files to download from from Export All task
    Downloads the file and saves locally to then process
    Uses file system to record pending & processed export jobs
    Data is written to a temp db table and then the 'merge' SQL is used
    to update/insert records in the permanent table

    Alternatively save to file server as csv. This option uses the documents api
    to record exports in progress, so no need for a db table to manage export

    If number of records is less than 10,000 then export is immediate
"""
# from __future__ import absolute_import

import codecs
import csv
import datetime
import functools
import io
import os
import shutil
import string  # (use string.lower instead of str.lower for py2.7)
import sys
import time
from ast import literal_eval
from contextlib import contextmanager
from pprint import pformat

import pyodbc
import six

from .apihelper import APIHelper
from .assets import AssetTools
from ..api import BackgroundWorkerApi
from ..api import DocumentApi
from ..api import SearchApi
from ..api_client import ApiClient
from ..models.document_representation import DocumentRepresentation
from ..rest import ApiException


class SyncToLocalProcesses(object):
    """
    Class to manage processes that sync Assetic search data to a local DB
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger

        # create instance of search api
        self.searchapi = SearchApi(self.api_client)
        # create instance of document API
        self.docapi = DocumentApi(self.api_client)
        self.apihelper = APIHelper()
        self._workingdir = os.getcwd()

        self._custom_field_list = None

        self.long_text_field_list = [
            "Additional Details", "Additional Info", "Additional Information",
            "Assessment", "Asset Commissioning Notes", "Asset Strategy",
            "Aus. Standard Comments", "Bush Fire Affected Area Comments",
            "Change room Detail", "Chronology Support Information",
            "Commissioning Attribution", "Contact Details",
            "Contamination Comments", "Demarcation Details", "Device Details",
            "Dimension Details", "Door Detail", "Emergency Plan Comment",
            "Entrances Comments", "Essential Service Comment",
            "Exit Sign Location", "Fire Hose Location",
            "First Aid Box Location", "Fitout Detail",
            "Flood Affected Area Comments", "Floor Detail", "General Comments",
            "General Sign Information", "History", "Insurance Policy Notes",
            "Kerb Comments", "Kitchen Detail",
            "Land Fill Operational Comments", "Left Bank Description",
            "Legal Implications Comments", "Legal Restrictions Comments",
            "Line Marking Other Comments", "Location",
            "Management Category Description", "Meter Reading Comments",
            "Modifications", "Original", "Other Information",
            "Purpose or Usage", "Rating Comments", "Recommendation",
            "Relieving Slab Information", "Replacement Comments",
            "Replacement Strategy", "Right Bank Description",
            "Shade Structure Details", "Special Instructions", "Statement",
            "Statement of Significance", "Topography Comments",
            "Treatment Capacity Comments", "Utility Access", "Wall Comments",
            "Water Hose Location"]

    @property
    def workingdir(self):
        """
        Gets current working directory.
        """
        if self._workingdir == None:
            self._workingdir = os.getcwd()
        return self._workingdir

    @workingdir.setter
    def workingdir(self, value):
        """
        Sets a new current working directory.
        :param value: the working directory to use
        """
        if os.path.isdir(value) == True:
            self._workingdir = value
        else:
            raise ApiException(
                status=1,
                reason="Invalid workingdir set: `{0}`"
                    .format(value)
            )

    def get_details_of_last_export(self, profileguid, dbtools):
        # type: (str, DB_Tools) -> dict
        """
        Given search profile GUID, retrieves the last time the export ran and
        returns it.
        :param profileguid: GUID of search profile
        :param dbtools: instatiated DB_Tools object to interact with database

        returns: datetime in datetime.datetime.iso() format
        """
        bg = BackgroundWorkerApi(self.api_client)

        sql_ = """
            SELECT TOP (1) taskid, total_records, processed_records FROM 
            assetic_sync_manager
            WHERE profileid = '{0}'
            ORDER BY date_initiated DESC
        """.format(profileguid)

        error_code, results = dbtools.execute_select(sql_)

        response = {
            "start_time": datetime.datetime(2000, 1, 1, 0, 0, 0).isoformat()
            , "last_total_count": 0, "last_processed_count": 0}

        if len(results) == 0:
            # e.g. a row hasn't been added for this profile before
            return response
        result = results[0]

        # set last total and processed counts
        response["last_total_count"] = result.total_records
        response["last_processed_count"] = result.processed_records

        if "not required" in result.taskid:
            # it was an export immediate, not bulk export
            if len(result.taskid) > len("not required "):
                # this record should also have a last max date
                last_run_str = result.taskid[len("not required "):]
                response["start_time"] = last_run_str
            return response
        else:
            # use background worker task start time
            bg_worker_guid = result.taskid

            r = bg.background_worker_get(bg_worker_guid)

            response["start_time"] = r["StartTime"]

            return response

    def profile_contains_modified_column(self, profile):
        # type: (SearchProfileRepresentation) -> bool
        """
        Returns whether or not the passed in search profile contains the
        last modified column as defined by the type of search profile
        (asset, component, work-order, etc.)

        :param profile: SearchProfileRepresentation
        """

        # retrieve internal API name for property to order by (e.g. ComplexAssetId)
        internal_keyfield = self.get_profile_internal_name_for_label(profile, profile.keyfield)

        profile.reconcile_lastmodified_properties(internal_keyfield)

        # retrieve the search columns
        resp = self.get_search_columns(profile.profileguid)

        # return whether that exists in search profile
        if profile.lastmodified_property_value in \
                [l['Label'] for l in resp['ResourceList']]:
            return True
        else:
            if profile.lastmodified_property_value:
                self.logger.warning(
                    "Include the field [{0}] in the search profile '{1}' to "
                    "allow the export to be skipped if no change to "
                    "data".format(profile.lastmodified_property_value,
                                  profile.profilename)
                )
            return False

    def add_non_processed_syncrow(self, dbtools, profile):
        # type: (DB_Tools, SearchProfileRepresentation) -> int
        """
        Adds row to assetic_sync_manager logging attempt to perform
        search profile export but found no modified files.

        Adds row identical to previous export's contents, but with
        different status - "Processed - no changes"
        """
        sql_select = """
        SELECT TOP (1) taskid, replace_special, documentid, 
        status, total_records, processed_records
        FROM assetic_sync_manager
        WHERE profileid = '{0}'
        ORDER BY date_initiated DESC
        """.format(profile.profileguid)

        # pe will never be None, as even if this is run for the first time
        # the date since lastModified will be 1-1-2000
        code, pe = dbtools.execute_select(sql_select)

        if code != 0:
            # something has gone wrong
            e = ("Error attempting to retrieve row from assetic_sync_manager. "
                 "See log for more detailed output.")
            self.logger.error(e)
            return code

        sql_insert = """
            insert into assetic_sync_manager
            (oid,taskid, profileid,profilename,tablename,keyfield,logtable,
            useinternalnames,replacespaces,spacedelimiter,setemptyasnull,
            allowdelete,replace_special,truncation_indicator
            ,status, documentid,total_records, processed_records
            ,date_initiated,date_last_modified)
            values (NEWID(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            ,getdate(),getdate())
            """

        # this is mostly all going to be the same information as the
        # previous row
        record = (
            pe[0].taskid,
            profile.profileguid,  # profileid
            profile.profilename,  # profilename
            profile.tablename,  # tablename
            profile.keyfield,  # keyfield
            profile.logtable,  # logtable
            profile.useinternalnames,  # useinternalnames
            profile.replacespaces,  # replacespaces
            profile.spacedelimiter,  # spacedelimiter
            profile.set_empty_as_null,  # setemptyasnull
            profile.allow_delete,  # allowdelete
            pe[0].replace_special,
            profile.truncation_indicator,  # truncation_indicator
            "Processed - no changes",  # status
            pe[0].documentid,
            pe[0].total_records,
            pe[0].processed_records
        )

        code = dbtools.execute_single(sql_insert, record)

        if code != 0:
            e = ("Error attempting to insert row into assetic_sync_manager. "
                 "See log for more detailed output.")
            self.logger.error(e)

        return code

    def dbsync_initiate(self, dbserver, dbname, profiles, incremental=True,
                        username=None, password=None,
                        driver="ODBC Driver 13 for SQL Server"
                        , custom_field_list=None, force_export=False, always_background_export=False):
        """
        For each profile in profiles array create new exports and log export
        task ID in db for later 'finalisation' step
        With this method there are no files used to manage process
        By default it is intended that it will only gets records modified
        since last sync date, however this is not yet implemented. All records
        are therefore downloaded.  The parameter incremental will at a future
        point be utilised to control this behaviour
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.  Assumes trusted connection
        :param profiles: an array of SearchProfileRepresentation instances
        :param incremental: True/False.
        Apply incremental export if True (default).  
        Default=True, however not implemented yet.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: default="ODBC Driver 13 for SQL Server". Could also use
        "SQL Server" but this is an old driver and must use trusted connection
        :param custom_field_list: a list of instances of
        SyncProcessCustomFieldRepresentation used to define custom names for
        fields on a per profile basis
        :param force_export: force export regardless of tests for last modified
        :param always_background_export: force export to always create a file via a background worker task
        :returns: no errors = 0, error=>0. 
        """
        self.logger.info("Starting dbsync_initiate")
        dbtools = DB_Tools(dbserver, dbname, username, password, driver)

        # make sure custom field names are the right type
        if isinstance(custom_field_list, list):
            self._custom_field_list = custom_field_list

        # loop through the list of profiles and create exports
        errorcode = 0
        for profile in profiles:
            # check to see if the profile contains LastModified property
            contains_lastmodified = self.profile_contains_modified_column(
                profile)

            if force_export and contains_lastmodified:
                self.logger.warning(
                    "Parameter force_export is set to True.  Set as False to "
                    "allow export to occur only if there are modified records"
                )

            table_is_populated = False
            if contains_lastmodified:
                # last modified can be used to skip export if no changes

                # first make sure table exists and not empty because if it
                # is then we can't skip export
                table_is_populated = self.table_exists_not_empty(dbtools,profile)

            if table_is_populated and contains_lastmodified \
                    and not force_export:
                # get most recent start time of last background worker
                last_export = self.get_details_of_last_export(
                    profile.profileguid, dbtools)
                start_time = last_export["start_time"]
                last_total = last_export["last_total_count"]
                # there is also "last_processed_count"

                # get number of records where ComplexAssetLastModified
                # greater than start time of previous export
                modified_records = self.get_total_count_for_search(
                    profile.profileguid, "{0}>{1}".format(
                        profile.lastmodified_internal_value, start_time)
                )
                # get total records - use in secondary check for modifications
                totalrecords = self.get_total_count_for_search(
                    profile.profileguid)

                # if nothing has changed, log message and do nothing
                if modified_records == 0 and last_total == totalrecords:
                    e = ("Not initiating bulk export of profile {0} "
                         "({1}) as no information has changed since last "
                         "export on {2}.").format(
                        profile.profilename, profile.profileguid, start_time)
                    self.logger.info(e)
                    self.add_non_processed_syncrow(dbtools, profile)
                    continue

            if always_background_export:
                profile.background_export = True

            # else, run export
            errorcode = self.create_export_task_db(profile, dbtools, incremental)
            if errorcode != 0:
                self.logger.info("Exiting dbsync_initiate with error")
                return errorcode

        self.logger.info("Finished dbsync_initiate")

        return errorcode

    def dbsync_finalise(self, dbserver, dbname, username=None, password=None,
                        driver="ODBC Driver 13 for SQL Server"
                        , custom_field_list=None):
        """
        Finalise sync by checking for documents created by background worker
        process and downloading those files to an array (not to disk)
        The downloaded data is synced and the task flagged as complete
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: default="ODBC Driver 13 for SQL Server". Could also use
        "SQL Server" but this is an old driver and must use trusted connection
        :param custom_field_list: a list of instances of
        SyncProcessCustomFieldRepresentation used to define custom names for
        fields on a per profile basis
        :returns: no errors = 0, error=>0. 
        """
        self.logger.info("Starting dbsync_finalise")
        # make sure custom field names are the right type
        if isinstance(custom_field_list, list):
            self._custom_field_list = custom_field_list

        returncode = 0
        dbtools = DB_Tools(dbserver, dbname, username, password, driver)
        ##get list of in-progress tasks from db
        returncode, tasks = self.get_active_task_doclist_db(dbtools)
        if returncode > 0:
            self.logger.info("Exiting dbsync_finalise with error")
            return returncode
        if tasks == None:
            self.logger.info("No active task exports ready for download")
        else:
            ##Prepare SQL for updating manager table on a per profile basis
            sql = """update assetic_sync_manager set documentid = ?,
                    status = ?, processed_records = ?,
                    date_last_modified=getdate()
                    where oid=CONVERT(uniqueidentifier,?)"""
            ##get generated document ID for task
            for task in tasks:
                ##check if the document is expired
                docid = task.documentid
                try:
                    docapi = DocumentApi(self.api_client)
                    response = docapi.document_get_0(docid)
                    # if document is expired, update status in assetic_sync_manager
                    if response["IsExpired"]:
                        status = "Expired"
                        record_count = 0
                        vals = [docid, status, record_count, task.oid]
                        returncode = dbtools.execute_single(sql, vals)
                        if returncode != 0:
                            self.logger.error("Error updating assetic_sync_manager_table for expired record")
                        continue
                except ApiException as e:
                    msg = "Get document for Document ID {0}".format(
                        docid)
                    self.logger.error('{0}: Status {0}, Reason: {1} {2}'.format(
                        msg, e.status, e.reason, e.body))
                    continue

                ##get document data
                docdata = self.get_document(docid)
                if docdata == None:
                    msg = "[{0}] export file contains no data." \
                          "Please check search profile.  Task ID:{1}".format(
                        docid, task.profile.profilename)
                    self.logger.warning(msg)
                else:
                    profile = task.profile
                    self.logger.info("Processing document {0} for profile {1} "
                                     "for task {2}".format(docid,
                                                           profile.profilename,
                                                           task.taskguid))
                    ##get column mappings and data types for search profile
                    datadef = self.get_search_columns(profile.profileguid)
                    ##build target table (method first checks if existing)
                    returncode = self.build_table_from_search(dbtools,
                                                              datadef, profile,
                                                              False)
                    if returncode != 0:
                        self.logger.error("Exiting dbsync_finalise with error")
                        return returncode
                    # get the number of records (less header row)
                    record_count = len(docdata.splitlines()) - 1
                    # write the records to the database
                    returncode = self.csv_string_to_db(docdata, profile,
                                                       dbtools,
                                                       datadef)

                    # update assetic_sync_manager
                    if returncode == 0:
                        status = "Processed"
                    else:
                        status = "Error"
                    vals = [docid, status, record_count, task.oid]
                    returncode = dbtools.execute_single(sql, vals)
                    if returncode != 0:
                        self.logger.error("Error updating"
                                          " assetic_sync_manager_table")
        self.logger.info("Finished dbsync_finalise")
        return returncode

    def initiate_export_task_to_file(self, profile, hidecontroldoc=False,
                                     doc_group=None, doc_category=None,
                                     doc_subcategory=None
                                     , force_export=False, always_background_export=False):
        """
        Given a search profile initiate a bulk export job and record details
        in a document link in Assetic.
        :param profile: an array of SearchProfileRepresentation instances
        :Param hidecontroldoc: once export file created, set log status as deleted
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        :Param force_export: force export regardless of tests for last modified
        :Param always_background_export: force export to always create a file via a background worker task
        Returned: return code 0=success,1=error
        """
        # check to see if the profile contains LastModified property
        contains_lastmodified = self.profile_contains_modified_column(profile)
        if force_export and contains_lastmodified:
            self.logger.warning(
                "Parameter force_export is set to True.  Set as False to "
                "allow export to occur only if there are modified records"
            )
        # check how many rows are returned, if less than 10,000 and
        # always_background_export not enabled for the profile we can use the
        # search get rather than batch - quicker as no background worker process
        # if has last modified field use that to get current max date
        if contains_lastmodified:
            max_last_date, totalrecords = \
                self.get_max_date_and_count_for_search(
                    profile.profileguid,
                    profile.lastmodified_internal_value,
                    profile.lastmodified_property_value)
        else:
            totalrecords = self.get_total_count_for_search(profile.profileguid)
            max_last_date = None
        if totalrecords < 0:
            return 1

        if always_background_export:
            profile.background_export = True

        if 0 < totalrecords <= 10000 and not profile.background_export:
            # use standard search api to get data
            if contains_lastmodified and not force_export:
                # get last run details in case no export required
                past = self.get_last_immediate_export_from_doclink(profile)
                if past["record_count"] == totalrecords and \
                        past["max_last_modified"] == max_last_date:
                    # the data hasn't changed, so skip export
                    e = ("Not initiating export of profile {0} "
                         "({1}) as no information has changed since "
                         "last change at {2}.").format(
                        profile.profilename, profile.profileguid, max_last_date)
                    self.logger.info(e)
                    return 0
            # need to export
            chk = self.immediate_export_to_file(
                profile, max_last_date, hidecontroldoc, doc_group,
                doc_category, doc_subcategory)
            return chk

        else:
            #>10,000 records so create background worker export task

            modified_records = 1   #dummy value. Will be reset if can be tested

            if contains_lastmodified and not force_export:
                # get the guid of the task the last time this profile
                # was exported
                past = self.get_last_completed_export_task_from_doclink(
                    profile.profilename)

                if past["taskid"]:
                    # get the time the export of that the last task started
                    start_time = self.get_task_start_date(past["taskid"])

                    if start_time:
                        # get number of records where Last Modified greater
                        # than start time of previous export
                        modified_records = self.get_total_count_for_search(
                            profile.profileguid, "{0}>={1}".format(
                            profile.lastmodified_internal_value, start_time))

                        # if nothing has changed, log message and do nothing
                        if modified_records == 0 and \
                                past["record_count"] == totalrecords:
                            e = ("Not initiating bulk export of profile {0} "
                                 "({1}) as no information has changed since "
                                 "last export on {2}.").format(
                                profile.profilename, profile.profileguid
                                , start_time)
                            self.logger.info(e)
                            return 0

            taskid = self.create_export_task(profile.profileguid)

            if taskid is not None:
                chk = self.create_export_task_as_doclink(
                    profile.profilename,
                    profile.profileguid,
                    taskid, doc_group,
                    doc_category,
                    doc_subcategory)
                if chk == 0:
                    msg = "Background worker export task created for" \
                          " {0}".format(profile.profilename)
                    self.logger.info(msg)
            else:
                return 1
        return 0

    def finalise_export_task_to_file(self, hidecontroldoc=False):
        """
        Given a search profile initiate a bulk export job and record details
        in a document link in Assetic.
        :param hidecontroldoc: Delete the document record used to manage the export
        Returned: return code 0=success,1=error
        """
        # get outstanding exports awaiting download
        docs = self.get_active_export_tasks_from_doclink()
        if len(docs) == 0:
            # none to process
            self.logger.info("No background export tasks to process")
            return 0

        # loop through the documents and parse the task id from string
        for doc in docs:
            x = doc["ExternalId"]
            profile_name = doc["Label"]
            if "Export Backup Process Task for " in profile_name:
                # strip off text preceding profile name
                profile_name = profile_name[
                               len("Export Backup Process Task for "):]
            try:
                taskid = x[x.find("TaskId=") + 8:x.find(";")]
            except Exception as ex:
                msg = "Unable to parse Task ID from external ID {0} for "
                "document {1}  Error is : {2}".format(x, doc["Id"], ex)
                self.logger.error(msg)
            else:
                csvstring = None
                # get the document ID for the export file
                status, exportdocid = self.get_export_docid(taskid)
                if not exportdocid:
                    msg = "Status of export is [{0}] for task [{1}] and " \
                          "profile name '{2}'" \
                          "".format(status, taskid, profile_name)
                    self.logger.info(msg)
                # if an old expired doclink is found, set docid to remove 'Not Processed'
                elif status == "Expired":
                    self.update_completed_export_task_as_doclink(
                        doc, exportdocid, 0, hidecontroldoc)
                else:
                    # get the document as a string
                    csvstring = self.get_document(exportdocid)
                if csvstring:
                    try:
                        record_count = len(csvstring.splitlines()) - 1
                    except Exception as ex:
                        record_count = 0
                    fullfilename = os.path.join(
                        self.workingdir, profile_name + ".csv")
                    # save document to file
                    chk = self.csvstring_to_file(csvstring, fullfilename)
                    if chk == 0:
                        # flag export to file as complete
                        chk = self.update_completed_export_task_as_doclink(
                            doc, exportdocid, record_count, hidecontroldoc)
                        if chk == 0:
                            msg = "Successfully downloaded csv [{0}] for " \
                                  "profile name '{1}'".format(
                                fullfilename, profile_name)
                            self.logger.info(msg)

    def immediate_export_to_file(
            self, profile, max_date, hidecontroldoc=False,
            doc_group=None, doc_category=None, doc_subcategory=None):
        """
        Initiate Export of the given profile to csv using the search API
        :param profile: SearchProfileRepresentation instance
        :param max_date: maximum last modified date
        Param hidecontroldoc: once export file created, set log status
         as deleted
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        Returned: return code 0=success,1=error
        """

        # need the keyfield internal name to sort by
        order_by_field = self.get_profile_internal_name_for_label(
            profile, profile.keyfield)
        metadata = self.get_search_columns(profile.profileguid)
        csvstring = self.run_search_for_pages(
            profile.profileguid, order_by_field, metadata)
        if csvstring == None:
            return 1
        # get number of records excluding header
        totalrecords = len(csvstring.splitlines()) - 1
        fullfilename = os.path.join(self.workingdir,
                                    profile.profilename + ".csv")
        chk = self.csvstring_to_file(csvstring, fullfilename)
        if chk != 0:
            return chk

        ##record as processed
        self.create_immediate_export_as_doclink(
            profile.profilename, profile.profileguid, totalrecords
            , max_date, hidecontroldoc, doc_group, doc_category,
            doc_subcategory)
        msg = "Immediate creation of csv file '{0}'".format(fullfilename)
        self.logger.info(msg)
        return 0

    def create_export_task_db(self, profile, dbtools, incremental):
        # type: (SearchProfileRepresentation,DB_Tools, bool) -> int
        """
        Given a search profile initiate a bulk export job for dbsync
        :param profile: The search profile guid
        :param dbtools: instance of DB_Tools
        :param incremental: incremental update supported True/False
        Returned: return code 0=success,1=error
        """
        # verify sync table is up to date
        returncode = self.upgrade_assetic_sync_manager_table(dbtools)
        if returncode != 0:
            return returncode

        # will first see how many rows in export, apply a filter if incremental
        qfilter = None
        if incremental == True:
            ##uses a date filter.  Get server time rather than local time
            ##TODO get last datetime successfully executed from documents api
            lastdate = None
            ##TODO get current datetime from api, or use a timeoffset config?
            currentdate = None
            if lastdate != None and currentdate != None:
                lastdate = datetime.datetime.now().isoformat()
                currentdate = datetime.datetime.now().isoformat()
                qfilter = "{0} >={1},{0}<={2}".format(
                    profile.lastdatefield, lastdate, currentdate)

        # check to see if the profile contains LastModified property
        contains_lastmodified = self.profile_contains_modified_column(
            profile)
        # see how may rows are returned, if less than 10,000
        # can use the search get rather than batch - quicker as no
        # background worker process
        if contains_lastmodified:
            # has last modified field use that to get current max date and
            # record count
            max_date, totalrecords = self.get_max_date_and_count_for_search(
                profile.profileguid, profile.lastmodified_internal_value,
                profile.lastmodified_property_value)
        else:
            # just get total count, last mod date not available
            totalrecords = self.get_total_count_for_search(
                profile.profileguid, qfilter)
            max_date = None

        # Prepare SQL to be used to write task details to database
        sql = """insert into assetic_sync_manager
            (oid,taskid, profileid,profilename,tablename,keyfield,logtable,
            useinternalnames,replacespaces,spacedelimiter,setemptyasnull,
            allowdelete,replace_special,truncation_indicator
            ,status,total_records,processed_records,date_initiated,
            date_last_modified)
            values (NEWID(),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,getdate(),
            getdate())
            """

        # stringify the dict so it can be written to the db
        replace_special = str(profile.replace_special_characters)

        # Now export immediately or initiate background worker export
        if 0 < totalrecords <= 10000 and not profile.background_export:
            # use standard search api to get data
            # will need the keyfield internal name to sort by
            order_by_field = self.get_profile_internal_name_for_label(
                profile, profile.keyfield)
            metadata = self.get_search_columns(profile.profileguid)

            csvstring = self.run_search_for_pages(
                profile.profileguid, order_by_field, metadata)
            if csvstring == None:
                return 0
            returncode = self.csv_string_to_db(csvstring, profile, dbtools,
                                               metadata)
            if returncode != 0:
                return returncode

            # update as processed
            if max_date:
                taskidcomment = "not required {0}".format(max_date)
            else:
                taskidcomment = "not required"
            record = taskidcomment, \
                     profile.profileguid, \
                     profile.profilename, \
                     profile.tablename, profile.keyfield, profile.logtable, \
                     profile.useinternalnames, profile.replacespaces, \
                     profile.spacedelimiter, profile.set_empty_as_null, \
                     profile.allow_delete, replace_special, \
                     profile.truncation_indicator, "Complete", totalrecords, \
                     totalrecords
            returncode = dbtools.execute_single(sql, record)

            self.logger.info(
                "Completed immediate export for '{0}', profile id {1}".format(
                    profile.profilename, profile.profileguid
                ))
        else:
            # else create export task
            taskid = self.create_export_task(profile.profileguid)

            self.logger.info(
                "Initiated bulk export for '{0}', profile id {1}".format(
                    profile.profilename, profile.profileguid
                ))
            if taskid != None:
                record = taskid, profile.profileguid, profile.profilename, \
                         profile.tablename, profile.keyfield, profile.logtable, \
                         profile.useinternalnames, profile.replacespaces, \
                         profile.spacedelimiter, profile.set_empty_as_null, \
                         profile.allow_delete, replace_special, \
                         profile.truncation_indicator, \
                         "In Progress", totalrecords, None
                returncode = dbtools.execute_single(sql, record)
            else:
                returncode = 1

        return returncode

    def create_export_task(self, profileguid):
        """
        Given a search profile initiate a bulk export job
        :param profileguid: The search profile guid
        Returned: taskid or None if error
        """
        try:
            taskid = self.searchapi.search_post_export_profile(profileguid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            return None
        return taskid

    def get_export_docid(self, exporttaskguid):
        """
        Given a background worker export job GUID check status
        Param1: the guid of the export task
        Returned: A tuple (2 fields)
        1. The status or None if profile not found
        2. docid if ready for download, otherwise None
        """
        bwapi = BackgroundWorkerApi(self.api_client)
        try:
            response = bwapi.background_worker_get(exporttaskguid)
        except ApiException as e:
            msg = "Get background worker for task {0}".format(
                exporttaskguid)
            self.logger.error('{0}: Status {0}, Reason: {1} {2}'.format(
                msg, e.status, e.reason, e.body))
            return None, None
        status = response.get("Status")
        docid = None

        if status == "Completed":
            docid = response.get("DocumentId")
            # check if the export was requested on a profile 0 search results (doc id will be None)
            if docid is None:
                return status, docid
            try:
                docapi = DocumentApi(self.api_client)
                response = docapi.document_get_0(docid)
                if response["IsExpired"]:
                    return "Expired", docid

            except ApiException as e:
                msg = "Get document for Document ID {0}".format(
                    docid)
                self.logger.error('{0}: Status {0}, Reason: {1} {2}'.format(
                    msg, e.status, e.reason, e.body))
                return None, None
        return status, docid

    def get_task_start_date(self, exporttaskguid):
        """
        Given a background worker export job GUID get start date
        exporttaskguid: the guid of the export task
        Returned: The start date or none if error/not found
        """
        bwapi = BackgroundWorkerApi(self.api_client)
        try:
            response = bwapi.background_worker_get(exporttaskguid)
        except ApiException as e:
            msg = "Get background worker for task {0}".format(
                exporttaskguid)
            self.logger.error('{0}: Status {0}, Reason: {1} {2}'.format(
                msg, e.status, e.reason, e.body))
            return None
        start_time = None

        if response["Status"] == "Completed":
            start_time = response["StartTime"]

        if response["DocumentId"] and not response["DocumentId"] == "":
            try:
                docapi = DocumentApi(self.api_client)
                response = docapi.document_get_0(response["DocumentId"])
                if response["IsExpired"]:
                    return None

            except ApiException as e:
                msg = "Get document for Document ID {0}".format(
                    response["DocumentId"])
                self.logger.error('{0}: Status {0}, Reason: {1} {2}'.format(
                    msg, e.status, e.reason, e.body))
                return None

        return start_time

    def csvstring_to_file(self, csvstring, fullfilename):
        """
        Given an array of strings, write each string to file as a new row
        :param csvstring: String array
        :param fullfilename: The file to save including directory path
        Returned: 0 if success, else error number
        """
        try:
            if six.PY2:
                with open(fullfilename, 'w') as out_file:
                    out_file.write(csvstring)
                self.logger.info("Created file {0}".format(fullfilename))
            else:
                with open(fullfilename, 'w', newline="",
                          encoding="UTF-8") as out_file:
                    out_file.write(csvstring)
                self.logger.info("Created file {0}".format(fullfilename))
        except Exception as e:
            self.logger.error("Error creating file {0}: {1}".format(
                fullfilename, e))
            return 1
        return 0

    def get_document(self, docid):
        """
        Gets document from Assetic, but doesn't write to disk
        Param docid: document ID to retrieve
        Returned: the data component of the document only. File not saved
        """
        docapi = DocumentApi(self.api_client)
        try:
            data = docapi.document_get_document_file(docid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            return None
        except ValueError as ex:
            self.logger.error("Error getting document: {0}".format(ex))
            return None
        # ensure encoding is ok
        datadec = self.decode_bom(data)
        return datadec

    def decode_bom(self, data):
        """
        Remove BOM from data
        Param data: Data to decode
        Returned: input data decoded to UTF-8
        """
        if sys.version_info < (3, 0):
            if data.startswith(codecs.BOM_UTF8):
                self.logger.debug("removing BOM_UTF8 codec from document start")
                data = data.strip(codecs.BOM_UTF8)
            return data
        else:
            # v3.  Remove BOM if present
            if data.startswith(codecs.BOM_UTF8.decode("utf8")):
                self.logger.debug("removing BOM_UTF8 codec from document start")
                data = data.strip(codecs.BOM_UTF8.decode("utf8"))
            return data

    def get_active_task_doclist_db(self, dbtools):
        """
        get active tasks from assetic_sync_manager table using filter
        status='inprogress'
        Param dbtools: dbtools object        
        Returned: a list of active tasks and document id
        """

        # verify sync table is up to date
        returncode = self.upgrade_assetic_sync_manager_table(dbtools)
        if returncode != 0:
            return returncode

        activetasks = []
        # get all tasks
        sql = """select convert(nvarchar(36),oid),taskid, profileid
        , profilename, tablename, keyfield, logtable, useinternalnames
        , replacespaces, spacedelimiter, setemptyasnull, replace_special
        , truncation_indicator, allowdelete
            from assetic_sync_manager 
            where status='In Progress'
            order by [date_initiated] asc"""

        sql_update = """update assetic_sync_manager set documentid = ?,
            status = ?, processed_records = ?,
            date_last_modified=getdate()
            where oid=CONVERT(uniqueidentifier,?)"""

        returncode, tasks = dbtools.execute_select(sql)
        if returncode != 0:
            return returncode, None

        ##format to task representation
        for task in tasks:
            ##first check if export document ready
            taskstatus, docid = self.get_export_docid(task[1])
            if docid != None:
                tr = ExportTaskRepresentation()
                pr = SearchProfileRepresentation()
                tr.oid = task[0]
                tr.taskguid = task[1]
                tr.documentid = docid
                pr.profileguid = task[2]
                pr.profilename = task[3]
                pr.tablename = task[4]
                pr.keyfield = task[5]
                pr.logtable = task[6]
                pr.useinternalnames = task[7]
                pr.replacespaces = task[8]
                pr.spacedelimiter = task[9]
                pr.set_empty_as_null = task[10]
                if task[11] and task[11].strip():
                    try:
                        pr.replace_special_characters = literal_eval(task[11])
                    except Exception as ex:
                        self.logger.error("Unable to build special character "
                                          "dictionary.\n{0}".format(ex))
                        return 1, None
                pr.truncation_indicator = task.truncation_indicator
                pr.allow_delete = task.allowdelete
                tr.profile = pr
                activetasks.append(tr)
            # Check if the Assetic BGW status is 'Complete' but no DocID (search profile with 0 results)
            elif taskstatus == "Completed" and docid is None:
                status = "Processed"
                record_count = 0
                task_oid = task[0]
                vals = [docid, status, record_count, task_oid]
                returncode = dbtools.execute_single(sql_update, vals)
                if returncode != 0:
                    return returncode

                msg = "The export requested for search profile [{0}] contained 0 results. " \
                      "No file was downloaded.".format(task[3])
                self.logger.info(msg)

            # Check if the Assetic BGW status is 'Error' and has failed
            elif taskstatus == "Error":
                status = "Error"
                record_count = 0
                task_oid = task[0]
                vals = [docid, status, record_count, task_oid]
                returncode = dbtools.execute_single(sql_update, vals)
                if returncode != 0:
                    return returncode

                msg = "The Background Worker [{0}] is in 'Error' status. " \
                      "The requested export for profile [{1}] was not successful. " \
                      "No file was downloaded.".format(task[1], task[3])
                self.logger.info(msg)
            # Export file is not ready yet
            else:
                msg = "Export file for profile [{0}] is not ready for download" \
                      ".  The status of the background worker process is [{1}]" \
                      ".  Please retry later when the file is ready".format(
                    task[3], taskstatus)
                self.logger.info(msg)
        return returncode, activetasks

    def csv_string_to_db(self, csvstring, profile, dbtools, metadata):
        """
        For a given single column array sync data to db.
        Assumes data in column is comma delimited, but no need to split
        Assumes a header row
        param csvstring: a string of csv data (multiple lines)
        param profile: instance of SearchProfileRepresentation
        param dbtools: instance of dbtools
        param metadata: instance of search profile column metadata
        Returned: 0 if success, else 1
        """

        dbtable = profile.tablename
        keyfield = profile.keyfield
        logtable = profile.logtable

        # get list of columns
        bIsHeader = True
        allrows = []
        saved_row = []
        csvarray = csvstring.splitlines()

        reader = csv.reader(csvarray)
        for row in reader:
            if bIsHeader == True:
                bIsHeader = False
                columns = self._prepare_column_names_for_column_headers(
                    row, profile, metadata)
            else:
                # cater for carriage returns in a column
                if len(saved_row):
                    row_tail = saved_row.pop()  # gets last item in the list
                    row[0] = row_tail + '\r' + row[
                        0]  # reconstitute field broken by newline
                    row = saved_row + row  # and reassemble the row (possibly only partially)
                if len(row) >= len(columns):
                    decodedrow = row
                    if sys.version_info < (3, 0):
                        # need to encode as unicode for python 2 otherwise issues
                        # with special characters
                        try:
                            decodedrow = [field.decode("utf8") for field in row]
                        except:
                            decodedrow = row
                    allrows.append(decodedrow)
                    saved_row = []
                else:
                    saved_row = row
        if profile.set_empty_as_null:
            # replace "" with None
            allrows = [[field if field.strip() != "" else None for field in row]
                       for row in allrows]

        # create table if it doesn't exist (method first checks if existing)
        chk = self.build_table_from_search(dbtools, metadata, profile, False)
        if chk > 0:
            return chk
        returncode = dbtools.data_sync_to_db(
            allrows, columns, dbtable, keyfield, logtable
            , profile.allow_delete, profile.truncation_indicator)
        return returncode

    def get_total_count_for_search(self, searchguid, searchfilter=None):
        """
        Get the total results and return
        Param searchguid: the search profile guid
        Param searchfilter: optional filter
        Returned: number of records
        """
        kw = {'request_params_id': searchguid,
              'request_params_page': 1,
              'request_params_page_size': 1}
        if searchfilter != None:
            kw['request_params_filters'] = searchfilter

        try:
            sg = self.searchapi.search_get(**kw)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            returncode = int(e.status)
            return -1
        totalrecords = int(sg['TotalResults'])

        return totalrecords

    def get_max_date_and_count_for_search(
            self, searchguid, date_field, date_label, searchfilter=None):
        """
        Get the max last modified date for the search
        Param searchguid: the search profile guid
        Param date_field: the field name for the last modified date
        Param searchfilter: optional filter
        Returned: number of records
        """
        kw = {'request_params_id': searchguid,
              'request_params_page': 1,
              'request_params_page_size': 1,
              'request_params_sorts': "{0}-desc".format(date_field)}
        if searchfilter != None:
            kw['request_params_filters'] = searchfilter

        try:
            sg = self.searchapi.search_get(**kw)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            returncode = int(e.status)
            return None, returncode
        if "ResourceList" in sg and len(sg["ResourceList"]) > 0 and \
                "Data" in sg["ResourceList"][0] and \
                len(sg["ResourceList"][0]["Data"]) > 0 and \
                date_label in sg["ResourceList"][0]["Data"][0]:
            maxdate = sg["ResourceList"][0]["Data"][0][date_label]
        else:
            maxdate = datetime.datetime(2000, 1, 1, 0, 0, 0).isoformat()
        totalrecords = int(sg['TotalResults'])
        return maxdate, totalrecords

    def run_search_for_pages(self, searchguid, order_by_field
                             , metadata, searchfilter=None):
        """
        Use to get data across multiple pages
        Limited to 10,000 records.
        Formats data as comma delimited, but no need to split
        Includes a header row
        Param searchguid: the search profile guid
        Param order_by_field: use to apply sort, ideally by primary key field
        Param metadata: The metadata response object for the search profile
        Param searchfilter: optional filter
        Returned: search data as csv or None
        """

        # set parameters for search
        numpagesize = 500  # max number of pagess
        startpage = 1
        pagelimit = 20
        kw = {'request_params_id': searchguid,
              'request_params_page': startpage,
              'request_params_page_size': numpagesize}

        if searchfilter:
            kw['request_params_filters'] = searchfilter
        if order_by_field:
            kw['request_params_sorts'] = order_by_field + "-desc"
        else:
            e = ("order_by_field not set for paginated search. "
                 "Using a sort helps ensure pagination results "
                 "are consistent. This may be caused by a mispelling "
                 "of the profile's KeyField ({0}), as {0} is not "
                 "found within the columns of the search profile."
                 ).format(order_by_field)
            self.logger.warning(e)

        # Get first page of results
        try:
            sg = self.searchapi.search_get(**kw)
        except ApiException as e:
            msg = "Run search for pages"
            self.logger.error('{0}: Status {1}, Reason: {2} {3}'.format(
                msg, e.status, e.reason, e.body))
            return None
        morepages = True
        totalresults = int(sg.get('TotalResults'))
        if totalresults == 0:
            morepages = False
            return None
        numpages = int(sg.get('TotalPages')) - (startpage - 1)
        self.logger.debug('Total Pages: {0}'.format(numpages))
        if pagelimit > int(numpages):
            ##page limit defines the number of pages we'll process
            pagelimit = numpages
        if numpages <= pagelimit:
            morepages = False
        endpage = (startpage - 1) + pagelimit
        self.logger.debug(
            "Start page: {0}, End page: {1}, pages left: {2}".format(startpage,
                                                                     endpage,
                                                                     numpages))

        ##get actual data from nested output
        resourcelist = sg.get('ResourceList')
        resource = resourcelist[0]
        data = resource.get('Data')
        ##Copy as alldata becuase we will be appending to this
        alldata = data

        ##Get a list of columns
        # columns = map(lambda x: x.keys(), data)
        # if six.PY2:
        #    columns = reduce(lambda x, y: x + y, columns)
        # else:
        #    columns = functools.reduce(lambda x, y: x | y, columns)

        # self.logger.debug("First page, columns are: {0}".format(columns))
        ##Write list of columns to the 'all' list as this may grow
        # allcolumns = columns

        ##Now loop through remaining pages
        if numpages > 1:
            for pagenum in range(startpage + 1, endpage + 1):
                ##set page number to get
                kw['request_params_page'] = pagenum
                self.logger.debug('Page: {0}'.format(kw['request_params_page']))

                ##Now get results for this page
                try:
                    sg = self.searchapi.search_get(**kw)
                except ApiException as e:
                    msg = "Run search for pages - additional pages"
                    self.logger.error(
                        '{0}: Status {1}, Reason: {2} {3}'.format(
                            msg, e.status, e.reason, e.body))
                    # returncode = int(e.status)
                    return None

                totalresults = int(sg.get('TotalResults'))
                if totalresults == 0:
                    # morepages = False
                    break
                # get actual data from nested output
                resourcelist = sg.get('ResourceList')
                resource = resourcelist[0]
                data = resource.get('Data')

                # Get column list for this page - there may be new columns
                # columns = map(lambda x: x.keys(), data)
                if six.PY2:
                    #    columns = reduce(lambda x, y: x + y, columns)
                    ##Add new column list to "allcolumns", will get unique list later
                    #    allcolumns = allcolumns + columns
                    # append new data to "alldata"
                    alldata = alldata + data
                else:
                    #    columns = functools.reduce(lambda x, y: x | y, columns)
                    ##merge column list sets
                    #    allcolumns = allcolumns | columns
                    # append new data to "alldata"
                    alldata.extend(data)

                # debug comment
                # self.logger.debug("in page loop, columns are: {0}".format(
                #    columns))

                if startpage + pagenum > 20:
                    ##catchall escape
                    # morepages = False
                    break
        # if six.PY2:
        # column list not unique, so get unique list using set
        #    columns = list(set(allcolumns))
        # elif sys.version_info.minor == 4:
        # python 3.4, csv writer error if pass in set, so make it a list
        #    columns = list(allcolumns)
        # else:
        # for PY3 the list is already unique, able to build unique using merge
        #    columns = allcolumns

        # get the full list of columns in search because the data may not have
        # all columns
        columns = [x["Label"] for x in metadata["ResourceList"]]

        # set csv writer output to string
        if six.PY2:
            output = io.BytesIO()
            writer = csv.writer(output)
        else:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        # write header columns
        writer.writerow(columns)
        # loop through data and write to csv
        for i_r in alldata:
            # map data to column list by key to avoid issues with column order
            # and insert "" for additional columns not in the data
            if six.PY2:
                writer.writerow(
                    map(lambda x: i_r.get(x).encode('utf-8')
                    if isinstance(i_r.get(x), unicode)
                    else i_r.get(x, "")
                        , columns)
                )
            else:
                writer.writerow(list(
                    map(lambda x: i_r.get(x, ""), columns)))

        csvdata = output.getvalue()
        output.close()
        return csvdata

    def _prepare_column_names_for_column_headers(
            self, header_row, profile, metadata):
        # type: (list,SearchProfileRepresentation,dict) -> list
        """
        Prepare a list of column names for the given column headers and
        profile definition
        :param header_row: the list of column headers, typicaly from the
        csv file downloaded from Assetic
        :param profile: SearchProfileRepresntation that defines any
        modifications to the label to be made
        :param metadata: metadata from Assetric Search API that has
        internal field name for user friendly label
        :return: A list of column names in the same order as supplied
        """

        columns = []
        for header in header_row:
            columns.append(self._get_column_name_for_label(header, profile
                                                           , metadata))

        # if self._custom_field_list:
        #    # change some/all field names from defaults to custom name
        #    for cfn in self._custom_field_list:
        #        if cfn.profileguid == profile.profileguid:
        #            columns = [x if x not in cfn.custom_field_names
        #                       else cfn.custom_field_names[x]
        #                       for x in columns]
        return columns

    def _get_column_name_for_label(self, label, profile, metadata):
        # type: (str,SearchProfileRepresentation,dict) -> str
        """
        Prepare a list of column names for the given column headers and
        profile definition
        :param label: a column label to get the column namr for
        :param profile: SearchProfileRepresntation that defines any
        modifications to the label to be made
        :param metadata: metadata from Assetric Search API that has
        internal field name for user friendly label
        :return: column name
        """
        # initiate column name as label name in case column not found
        column = label
        if profile.useinternalnames:
            columnmap = metadata.get("ResourceList")
            for columnset in columnmap:
                if columnset.get('Label') == label:
                    column = columnset.get('Name')
                    return column
        else:
            if profile.replacespaces:
                # replace spaces in field name with delimiter
                if profile.spacedelimiter is None:
                    # remove whitespaces from label
                    profile.spacedelimiter = ""
                # add to dict that replaces special chars
                profile.replace_special_characters[" "] = \
                    profile.spacedelimiter
                self.logger.debug("Using label names without "
                                  "whitespaces for column names")

            # remove special characters
            for k, v in six.iteritems(
                    profile.replace_special_characters):
                label = label.replace(k, v)
            column = label

        if self._custom_field_list:
            # change some/all field names from defaults to custom name
            for cfn in self._custom_field_list:
                if cfn.profileguid == profile.profileguid:
                    for k, v in cfn.custom_field_names:
                        if k.lower() == column.lower():
                            column = v
        return column

    def get_profile_internal_name_for_label(self, profile, formatted_label):
        """
        For the given label use the profile settings to allow the profile
        metadata label to match the formatted label
        If profile setting is to use internal names then just return the
        passed in value
        :param profile: the profile object
        :param formatted_label: The label to get the internal name for
        :return: internal name of search field
        """
        # remove square braces regardless
        formatted_label = formatted_label.strip('[').strip(']')

        # get metadata for search
        response = self.get_search_columns(profile.profileguid)
        metadata = response["ResourceList"]
        if profile.useinternalnames:
            # should already be internal name - verify
            for row in metadata:
                if row["Name"] == formatted_label:
                    return row["Name"]
        if profile.replacespaces:
            # the label is formatted
            if profile.spacedelimiter is None:
                # No delimiter meaning whitepaces are removed
                profile.spacedelimiter = ""
            for row in metadata:
                if row["Label"].replace(" ", profile.spacedelimiter) == \
                        formatted_label:
                    return row["Name"]
        else:
            # the label is not reformatted so should be direct match
            for row in metadata:
                if row["Label"] == formatted_label:
                    return row["Name"]
        # didn't find an internal name - return None
        return None

    def build_assetic_sync_manager_table(self, dbserver, dbname, username=None,
                                         password=None,
                                         driver="ODBC Driver 13 for SQL Server"):
        """
        Builds the db table used to manager the sync process
        Assumes trusted connection to database
        param dbserver: the name of the SQL Server instance
        param dbname: the name of the the SQL Server database
        Returned: Success (Boolean) - True if no error 
        """
        dbtools = DB_Tools(dbserver, dbname, username, password, driver)
        sqlchk = "select object_id('assetic_sync_manager') as objectid"
        sqlcreate = """CREATE TABLE assetic_sync_manager(
            [oid] [uniqueidentifier],            
            [taskid] [nvarchar](50),
            [profileid] [nvarchar](50),
            [profilename] [nvarchar](100),
            [tablename] [nvarchar](50),
            [keyfield] [nvarchar](50),
            [logtable] [nvarchar](50),
            [documentid] [nvarchar](50),
            [useinternalnames] bit,
            [replacespaces] bit,
            [spacedelimiter] [nvarchar](50),
            [setemptyasnull] bit,
            [allowdelete] bit,
            [replace_special] nvarchar(500),
            [truncation_indicator] nvarchar(50)
            [date_initiated] datetime,
            [date_last_modified] datetime,
            [status] [nvarchar](50)),
            [total_records] [int],
            [processed_records] [int]"""
        returncode, result = dbtools.execute_select(sqlchk)
        if returncode == 0 and result[0][0] == None:
            returncode = dbtools.execute_single(sqlcreate)
        return returncode

    def upgrade_assetic_sync_manager_table(self, dbtools):
        """
        Builds the db table used to manager the sync process
        param dbtools: initiated instance of dbtools
        Returned: Success=0, nonzero = error 
        """
        # have added a new field to assetic_sync_manager Feb2017
        # check to see it is there and create if not
        returncode, existingcolumns = dbtools.get_columns_for_table(
            "assetic_sync_manager")
        if returncode != 0:
            return returncode
        if "replacespaces" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add replacespaces bit"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error(
                'Table assetic_sync_manager missing field "replacespaces"')
            return returncode
        # Add spacedelimiter field to allow an underscore or other delimiter
        # to replace the space.  Must also set replacespaces = True to use
        if "spacedelimiter" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "spacedelimiter [nvarchar](50)"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"spacedelimiter"')
            return returncode

        # Add spacedelimiter field to allow an underscore or other delimiter
        # to replace the space.  Must also set replacespaces = True to use
        if "setemptyasnull" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "setemptyasnull bit"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"setemptyasnull"')
            return returncode

        # Add allowdelete field to allow records in target table to be deleted
        # if not in the source data.  Log table will hold deleted record
        if "allowdelete" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "allowdelete bit"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"allowdelete"')
            return returncode

        # Add replace_special field to allow special characters to be
        # substituted in the field names
        if "replace_special" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "replace_special nvarchar(500)"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"replace_special"')
            return returncode

        # add field to allow truncation of data with optional suffix
        if "truncation_indicator" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "truncation_indicator nvarchar(50)"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"truncation_indicator"')
            return returncode

        # add field to record total number of records
        if "total_records" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "total_records int"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"total_records"')
            return returncode

        # add field to record total number of records
        if "processed_records" not in existingcolumns:
            # need to create
            sql = "alter table assetic_sync_manager add " \
                  "processed_records int"
            returncode = dbtools.execute_single(sql)
        if returncode != 0:
            self.logger.error('Table assetic_sync_manger missing field '
                              '"processed_records"')
            return returncode

        # all good
        return 0

    def table_exists_not_empty(self, dbtools, profile):
        """
        Does the target table exist and does it have any records?
        Param dbtools: instance of dbtools
        Param profile: instance of search profile definition
        return: true if table exists and not empty
        """
        sqlchk = "select object_id('{0}') as objectid".format(
            profile.tablename)
        # check to see if table exists
        returncode, result = dbtools.execute_select(sqlchk)
        if returncode == 0 and result[0][0] != None:
            # count records
            sqlchk = "select count(*) from {0}".format(profile.tablename)
            returncode, result = dbtools.execute_select(sqlchk)
            if returncode == 0 and result[0][0] > 0:
                return True
        # table not exists or empty
        return False

    def build_table_from_search(self, dbtools, metadata, profile,
                                printonly=False):
        """
        Builds the sync target db table based on search fields
        Optionally print creation SQL instead of creating
        Can use standalone.  Is also used when sync is peformed
        :param dbtools: instance of dbtools
        :param metadata: instance of search profile metadata.
        if None then profile ID will be used to get the metadata from api
        SearchMetadataRepresentationList
        :param profile: instance of search profile definition
        :param printonly: If true the column name is based on the
        user visible field label in export, else internal field name is used
        default is False
        If true then table is not created but SQL for table create is.
        Allows manual edit of datatypes and manual creation of table.
        Returned: 0=Success, 1=error
        """
        if metadata == None:
            metadata = self.get_search_columns(profile.profileguid)
        if metadata == None:
            return 1
        sqlchk = "select object_id('{0}') as objectid".format(profile.tablename)
        # check to see if table exists
        returncode, result = dbtools.execute_select(sqlchk)
        if returncode == 0 and result[0][0] != None:
            self.logger.debug(
                "Target table [{0}] already exists".format(profile.tablename))
            return returncode

        # prepare table sql
        resourcelist = metadata.get("ResourceList")
        keyfield = profile.keyfield
        if "[" not in keyfield:
            keyfield = "[{0}]".format(keyfield)
        columnddl = []
        for columndef in resourcelist:
            # by default set column name to user friendly column header
            # in export file
            # colname = "[{0}]".format(columndef.get("Label"))
            # if profile.useinternalnames == True:
            #    # change column name to assetic internal field name for the
            #    label
            #    colname = "[{0}]".format(columndef.get("Name"))
            # elif profile.replacespaces == True:
            #    ##replace spaces in field name with delimiter
            #    if profile.spacedelimiter == None:
            #        ##remove whitespaces from label
            #        profile.spacedelimiter = ""
            #    # replace whitespaces from Label names
            #    colname = colname.replace(" ", profile.spacedelimiter)
            colname = self._get_column_name_for_label(columndef.get(
                "Label"), profile, metadata)
            colname = "[{0}]".format(colname)
            # set datatype
            datatype = "nvarchar(500)"  # default datatype - e.g System.String
            typedef = columndef.get("Type").lower()
            if typedef.find('integer') > 0:
                datatype = 'int'
            elif typedef.find('double') > 0:
                datatype = 'float'
            elif typedef.find('decimal') > 0:
                datatype = 'float'
            elif typedef.find('datetime') > 0:
                datatype = 'datetime'
            elif typedef.find('bool') > 0:
                datatype = 'bit'

            # cater for known long fields - this is not definitive
            if datatype == "nvarchar(500)" and \
                    columndef.get("Label") in self.long_text_field_list:
                datatype = "nvarchar(4000)"
            # set NULL/NOT NULL
            allownull = "NULL"
            if colname.lower() == keyfield.lower():
                allownull = "NOT NULL CONSTRAINT [{0}_PK] PRIMARY KEY " \
                            "CLUSTERED".format(profile.tablename)
                datatype = "nvarchar(100)"
            columnddl.append("{0} {1} {2}".format(colname, datatype, allownull))

        # finalise create string
        sqlcreate = "create table {0}({1})".format(profile.tablename,
                                                   ",".join(columnddl))
        # create table
        if printonly:
            print(sqlcreate)
            returncode = 0
        else:
            # create table
            returncode = dbtools.execute_single(sqlcreate)
        return returncode

    def get_search_columns(self, profileid):
        """
        Use the api to get column mappings for search profile
        Param profileid: search profile guid
        Returned: array of SearchProfileColumnRepresentation or None if error or
        profile not found
        """

        try:
            response = self.searchapi.search_get_profile_metadata(profileid)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            return None
        return response

    def create_immediate_export_as_doclink(self, profilename, profileguid,
                                           record_count, max_last_modified,
                                           hidecontroldoc=False, doc_group=None,
                                           doc_category=None,
                                           doc_subcategory=None):
        """
        Use Assetic documents to record the completed export of a profile
        For this case the export was completed in one step
        Allow document status of deleted, can still find history via API but
        not clog up searches with these documents.
        :Param profilename: name of profile
        :Param profileguid: The GUID of the search profile
        :param record_count: number of records processed
        :param: max_last_modified: the max last modified date of the records
        :Param hidecontroldoc: once created, set status as deleted
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        :Returned: 0=success, else error
        """
        # Document categorisation - initialise document properties object
        # and populate
        document = DocumentRepresentation()
        docurl = "{0}/Search/AdvancedSearchProfile/SPDashboard/Default/{1}" \
                 "".format(self.api_client.configuration.host, profileguid)
        document.document_group = doc_group
        document.document_category = doc_category
        document.document_sub_category = doc_subcategory
        document.document_link = docurl
        document.label = "Export Backup Process Task for {0}".format(
            profilename)
        document.external_id = "Immediate export via paginated search"
        document.description = \
            "Record Count:{0}; Max_Last_Modified {1}".format(
                record_count, max_last_modified)

        # Perform upload
        try:
            doc = self.docapi.document_post(document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        # Now optionally delete the record, it's retained with status 500
        if hidecontroldoc and doc and len(doc) > 0:
            try:
                self.docapi.document_delete_document_file_by_id(doc[0]["Id"])
                # doc = self.docapi.document_delete(doc["Id"])
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return e.status
        return 0

    def create_export_task_as_doclink(self, profilename, profileguid, taskid,
                                      doc_group=None, doc_category=None,
                                      doc_subcategory=None):
        """
        Use Assetic documents to record the creation of a search profile export
        via the background worker task
        :Param profilename: The name of the search profile
        :Param profileguid: The GUID of the search profile
        :Param task: guid of background worker export task
        :Param doc_group: optional document group id (int)
        :Param doc_group: optional document category id (int)
        :Param doc_group: optional document sub category id (int)
        :Returned: 0=success, else error
        """

        # Document categorisation - initialise document properties object
        # and populate
        document = DocumentRepresentation()
        docurl = "{0}/Search/AdvancedSearchProfile/SPDashboard/Default/{1}" \
                 "".format(self.api_client.configuration.host, profileguid)
        document.document_group = doc_group
        document.document_category = doc_category
        document.document_sub_category = doc_subcategory
        document.document_link = docurl
        document.external_id = "TaskID={0};DocumentId={1}".format(
            taskid, "Not Processed")
        document.label = "Export Backup Process Task for {0}".format(
            profilename)

        # Perform upload
        try:
            self.docapi.document_post(document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        return 0

    def update_completed_export_task_as_doclink(
            self, document, exportdocid, record_count, hidecontroldoc=False):
        """
        Use Assetic documents to record the completed export of a profile
        Allow document status of deleted, can still find history via API but
        not clog up searches with these documents.
        :Param document: json DocumentRepresentation
        :Param exportdocid: The document ID of the exported document
        :Param record_count: The total number of records
        :Param hidecontroldoc: optionally delete if True.  Default = False
        :Returned: 0=success, else error
        """
        # Flag export as processed by replacing "Not Processed" with export id
        if "Not Processed" in document["ExternalId"]:
            document["ExternalId"] = document["ExternalId"].replace(
                "Not Processed",
                exportdocid)
        else:
            # just in case....
            document["ExternalId"] = "DocumentId={0}".format(exportdocid)
        #set the record count in the description
        document["Description"] = "Record Count:{0}".format(record_count)
        # Perform upload
        try:
            self.docapi.document_put(document["Id"], document)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        # Now optionally delete the record, it's retained with status 500
        if hidecontroldoc == True:
            try:
                self.docapi.document_delete_document_file_by_id(document["Id"])
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return e.status
        return 0

    def get_active_export_tasks_from_doclink(self):
        """
        Use Assetic documents to get a list of active background worker exports
        :Returned: A list of document representations or empty list if none.
        """
        ##set search criteria as keyword args
        searchsort = "Label-desc,CreatedDate-desc"
        searchfilter = "label~contains~'Export Backup Process Task for'" \
                       "~and~ExternalId~contains~'Not Processed'"
        numpagesize = 500

        documents = list()
        ##loop for 10 pages, add task Ids to list, break when no results
        for numpage in range(1, 11):
            kw = {"request_params_page": numpage,
                  "request_params_page_size": numpagesize,
                  "request_params_sorts": searchsort,
                  "request_params_filters": searchfilter}

            ###Perform get
            try:
                docs = self.docapi.document_get(**kw)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                break
            documents = documents + docs["ResourceList"]
            if len(docs["ResourceList"]) < numpagesize:
                # last page so break
                break
        ##loop through documents, check if current document label same as previous
        currentprofile = ""
        uniqueprofiledocuments = []
        for document in documents:
            if not document["Label"] == currentprofile:
                uniqueprofiledocuments.append(document)
                currentprofile = document["Label"]

        return uniqueprofiledocuments

    def get_last_immediate_export_from_doclink(self, profile):
        """
        Use Assetic documents API to get the details of the last immediate
        export using the search api rather than bulk export
        This is used to see if the records have changed since last export
        :Returned: a dict of record count and max record last modified
        :Param profile: The instance of the search profile
        :returns: dict with last max and record_count, values None if not found
        """
        # set search criteria as keyword args
        searchfilter = "label~contains~'Export Backup Process Task for {0}'" \
                       "~and~ExternalId~contains~" \
                       "'Immediate export via paginated search'".format(
            profile.profilename)

        kw = {"request_params_page": 1,
              "request_params_page_size": 1,
              "request_params_sorts": "LastModified-desc",
              "request_params_filters": searchfilter}

        response = {
            "record_count": 0
            , "max_last_modified":
                datetime.datetime(2000, 1, 1, 0, 0, 0).isoformat()
        }
        # Perform get
        try:
            docs = self.docapi.document_get(**kw)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return response

        if len(docs["ResourceList"]) > 0:
            doc = docs["ResourceList"][0]
            if doc["Description"] and len(doc["Description"]) > 0:
                # The description is something like:
                # "Record Count:655; Max_Last_Modified {1}"
                parts = doc["Description"].split(";")
                if len(parts) == 2:
                    response["record_count"] = int(parts[0].split(":")[1])
                    response["max_last_modified"] = \
                        parts[1].strip().split(" ")[1]
        return response

    def get_last_completed_export_task_from_doclink(self, profilename):
        """
        Use Assetic documents API to get a list of finalised exports
        This is used to see if the assets have changed since last export
        :Returned: A list of document representations or empty list if none.
        :Param profilename: The name of the search profile
        :returns: dict with taskid and record_count, values None if not found
        """
        ##set search criteria as keyword args
        searchfilter = "label~contains~'Export Backup Process Task for {0}'" \
                       "~and~ExternalId~contains~'DocumentId'".format(
            profilename)

        kw = {"request_params_page": 1,
              "request_params_page_size": 1,
              "request_params_sorts": "LastModified-desc",
              "request_params_filters": searchfilter}

        response = {"record_count": 0, "taskid": None}
        ###Perform get
        try:
            docs = self.docapi.document_get(**kw)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return response

        if len(docs["ResourceList"]) > 0:
            doc = docs["ResourceList"][0]
            x = doc["ExternalId"]
            try:
                response["taskid"] = x[x.find("TaskId=") + 8:x.find(";")]
            except Exception as ex:
                msg = "Unable to parse Task ID from external ID {0} for "
                "document {1}  Error is : {2}".format(x, doc["Id"], ex)
                self.logger.error(msg)
            else:
                #also get previous record count
                if doc["Description"] and len(doc["Description"]) > 0:
                    # The description is something like "Record Count:89766"
                    parts = doc["Description"].split(":")
                    if len(parts) == 2:
                        response["record_count"] = int(parts[1])
        return response

    def initiate_export_process(self, searchid, dbtools):
        """
        For a given search profile initiate the bulk export
        Returned: True = Success, False = Error
        Also create a file named after the task id.  This file is in the
        'inprogress' folder.
        Later we can check this folder for 'inprogress' tasks
        OBSOLETE
        """
        taskid = self.create_export_task_db(searchid, dbtools)
        if taskid == None:
            return False
        return True

    def dbsync_csvfile_process(self, dbserver, dbname, profiles, username=None,
                               password=None,
                               driver="ODBC Driver 13 for SQL Server"):
        """
        Look in the working folder 'csvexports' for file
        The file name is the profile name of the job.
        Upload to database and move to csvsynced folder
        """
        sourcedir = self.workingdir + "/inprogress/"
        downloaddir = self.workingdir + "/csvexports"
        processedcsv = self.workingdir + "/processedcsv"
        errorcsv = self.workingdir + "/errorcsv"

        files = os.listdir(downloaddir)
        if len(files) == 0:
            return
        dbtools = DB_Tools(dbserver, dbname, username, password, driver)
        for filename in files:
            self.logger.debug(filename)
            fullfilename = downloaddir + "/" + filename
            for profile in profiles:
                if profile.profilename + ".csv" == filename:
                    self.logger.debug(
                        "profile: {0},file: {1}".format(profile.profilename,
                                                        filename))
                    success = self.csvfile_to_db(fullfilename, profile, dbtools)
                    # dt = datetime.datetime.utcnow().isoformat()
                    dt = str(int(time.time()))
                    filename = dt + "_" + filename
                    if success:
                        shutil.move(fullfilename, processedcsv + "/" + filename)
                    else:
                        shutil.move(fullfilename, errorcsv + "/" + filename)

    def csvfile_to_db(self, csvfile, profile, dbtools):
        """
        For a given csv file sync data to db.  Assumes a header row
        param csvfile: the full filename and path of csv file
        param profile: instance of SearchProfileRepresentation
        Param dbtools: dbtools object        
        Returned: 0 if success, else 1
        """

        dbtable = profile.tablename
        keyfield = profile.keyfield
        logtable = profile.logtable

        # get list of columns
        bIsHeader = True
        allrows = []
        saved_row = []

        with open(csvfile, 'rt', encoding='utf-8', newline='') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if bIsHeader == True:
                    bIsHeader = False
                    columns = row
                else:
                    # cater for carriage returns in a column
                    if len(saved_row):
                        row_tail = saved_row.pop()  # gets last item in the list
                        row[0] = row_tail + '\r' + row[
                            0]  # reconstitute field broken by newline
                        row = saved_row + row  # and reassemble the row (possibly only partially)
                    if len(row) >= len(columns):
                        allrows.append(row)
                        saved_row = []
                    else:
                        saved_row = row
        returncode = dbtools.data_sync_to_db(
            allrows, columns, dbtable, keyfield, logtable
            , profile.allow_delete, profile.truncation_indicator)

        return returncode


class SearchProfileRepresentation(object):
    """"
    A structure for defining table metadata and relationships between
    search profile names, id's and tables
    """

    def __init__(self, profileguid=None, profilename=None, tablename=None,
                 keyfield=None, logtable=None, useinternalnames=False,
                 replacespaces=False, spacedelimiter=None, lastdatefield=None,
                 set_empty_as_null=False, allow_delete=False,
                 replace_special_characters=None, truncation_indicator=None, background_export=False):
        # type: (str, str, str,str,str,bool,bool,str,str,bool,bool,dict,str,bool) -> None
        """
        SearchProfileRepresentation - a model defining metadata for syncing a
        search profile to a local database table via bulk export api
        """
        self.fieldtypes = {
            "profileguid": "str",
            "profilename": "str",
            "tablename": "str",
            "keyfield": "str",
            "logtable": "str",
            "useinternalnames": "bool",
            "replacespaces": "bool",
            "spacedelimiter": "str",
            "lastdatefield": "string",
            "set_empty_as_null": "bool",
            "allow_delete": "bool",
            "replace_special_characters": "dict",
            "truncation_indicator": "string",
            "background_export": "bool"
        }

        # this dictionary will be used to test for special characters
        # in field names and retain by default unless an alternate
        # is provided by the user via replace_special_characters
        # self.default_special_characters = {
        #    "(": "(",
        #    ")": ")",
        #    "-": "-",
        #    "/": "/"
        # }
        # Decided not to apply a default.  Special characters will only be
        # changed if set by the user.
        self.default_special_characters = dict()

        if replace_special_characters and \
                isinstance(replace_special_characters, dict):
            for k, v in six.iteritems(replace_special_characters):
                self.default_special_characters[k] = v
        self._profileguid = profileguid
        self._profilename = profilename
        self._tablename = tablename
        self._keyfield = keyfield
        self._logtable = logtable
        self._useinternalnames = useinternalnames
        self._replacespaces = replacespaces
        self._spacedelimiter = spacedelimiter
        self._lastdatefield = lastdatefield
        self._set_empty_as_null = set_empty_as_null
        self._allow_delete = allow_delete
        self._replace_special_characters = self.default_special_characters
        self._truncation_indicator = truncation_indicator
        self._background_export = background_export

        # friendly last modified property value, e.g. "Asset Last Modified"
        # input by client, used to check filtering available via search-
        # metadata API
        self.lastmodified_property_value = None

        # internal last modified property value, e.g. "ComplexAssetLastModified"
        # for filtering via search API
        self.lastmodified_internal_value = None

        self.prop_lastmod_key = {
            "ComplexAssetId": "ComplexAssetLastModified",
            "ComponentId": "ComponentLastModified",
            "WorkOrderId": "WOLastModified",
            "WorkRequestId": "WRLastModified",
            "FormResultId": "FormResultLastModified",
            "FriendlyNetworkMeasureRecordId": "LastModifiedOn"
        }

        self.lastmodinternal_label_key = {
            "ComplexAssetLastModified": "Asset Last Modified",
            "ComponentLastModified": "Component Last Modified",
            "WOLastModified": "Work Order Last Modified Date",
            "WRLastModified": "Work Request Last Modified Date",
            "FormResultLastModified": "Form Result Last Modified Date",
            "LastModifiedOn": "Last Modified Date"
        }

    @property
    def profileguid(self):
        return self._profileguid

    @profileguid.setter
    def profileguid(self, profileguid):
        self._profileguid = profileguid

    @property
    def profilename(self):
        return self._profilename

    @profilename.setter
    def profilename(self, profilename):
        self._profilename = profilename

    @property
    def tablename(self):
        return self._tablename

    @tablename.setter
    def tablename(self, tablename):
        self._tablename = tablename

    @property
    def keyfield(self):
        return self._keyfield

    @keyfield.setter
    def keyfield(self, keyfield):
        self._keyfield = keyfield

    @property
    def logtable(self):
        return self._logtable

    @logtable.setter
    def logtable(self, logtable):
        self._logtable = logtable

    @property
    def useinternalnames(self):
        return self._useinternalnames

    @useinternalnames.setter
    def useinternalnames(self, useinternalnames):
        self._useinternalnames = useinternalnames

    @property
    def replacespaces(self):
        return self._replacespaces

    @replacespaces.setter
    def replacespaces(self, replacespaces):
        self._replacespaces = replacespaces

    @property
    def spacedelimiter(self):
        return self._spacedelimiter

    @spacedelimiter.setter
    def spacedelimiter(self, spacedelimiter):
        self._spacedelimiter = spacedelimiter

    @property
    def lastdatefield(self):
        return self._lastdatefield

    @lastdatefield.setter
    def lastdatefield(self, lastdatefield):
        self._lastdatefield = lastdatefield

    @property
    def set_empty_as_null(self):
        return self._set_empty_as_null

    @set_empty_as_null.setter
    def set_empty_as_null(self, set_empty_as_null):
        self._set_empty_as_null = set_empty_as_null

    @property
    def allow_delete(self):
        return self._allow_delete

    @allow_delete.setter
    def allow_delete(self, value):
        self._allow_delete = value

    @property
    def replace_special_characters(self):
        return self._replace_special_characters

    @replace_special_characters.setter
    def replace_special_characters(self, value):
        # ensure that the default list of special characters is retained
        # and add any new keys or update values for defaults
        if value and \
                isinstance(value, dict):
            for k, v in six.iteritems(value):
                self._replace_special_characters[k] = v

    @property
    def truncation_indicator(self):
        return self._truncation_indicator

    @truncation_indicator.setter
    def truncation_indicator(self, value):
        self._truncation_indicator = value

    @property
    def background_export(self):
        return self._background_export

    @background_export.setter
    def background_export(self, value):
        self._background_export = value

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

    def reconcile_lastmodified_properties(self, internalfield):
        """
        Accepts internal field value from BulkExportTools and
        attempts to set internal values for property last modified values.

        Ignores if values cannot be set and will return False on whether
        the search profile contains LastModified properties - preventing any bugs
        if this breaks existing scripts.
        """
        try:
            self.lastmodified_internal_value = self.prop_lastmod_key[internalfield]
        except KeyError:
            pass

        try:
            self.lastmodified_property_value = self.lastmodinternal_label_key[self.lastmodified_internal_value]
        except KeyError:
            pass


class SyncProcessCustomFieldRepresentation(object):
    """"
    A structure for defining field names for a search that are different to the
    search label or internal name.  Provides a dict where the key is the field
    name as it appears after 'use internal names' and 'replace spaces' is
    applied.  The value is the field name to use when inserting into db.
    """

    def __init__(self, profileguid=None, custom_field_names=None):
        """
        SyncProcessCustomFieldRepresentation
        """
        self.fieldtypes = {
            "profileguid": "str",
            "custom_field_names": "dict"
        }
        self._profileguid = profileguid
        self._custom_field_names = custom_field_names

    @property
    def profileguid(self):
        return self._profileguid

    @profileguid.setter
    def profileguid(self, profileguid):
        self._profileguid = profileguid

    @property
    def custom_field_names(self):
        return self._custom_field_names

    @custom_field_names.setter
    def custom_field_names(self, custom_field_names):
        self._custom_field_names = custom_field_names

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


class ExportTaskRepresentation(object):
    """"
    A structure for defining table metadata and relationships between
    search profile names, id's and tables
    """

    def __init__(self, oid=None, taskguid=None, documentid=None, profile=None):
        """
        SearchProfileRepresentation - a model defining metadata for syncing a
        search profile to a local database table via bulk export api
        """
        self.fieldtypes = {
            "oid": "str",
            "taskguid": "str",
            "documentid": "str",
            "profile": "SearchProfileRepresentation"
        }
        self._oid = oid
        self._taskguid = taskguid
        self._documentid = documentid
        self._profile = profile

    @property
    def oid(self):
        return self._oid

    @oid.setter
    def oid(self, oid):
        self._oid = oid

    @property
    def taskguid(self):
        return self._taskguid

    @taskguid.setter
    def taskguid(self, taskguid):
        self._taskguid = taskguid

    @property
    def documentid(self):
        return self._documentid

    @documentid.setter
    def documentid(self, documentid):
        self._documentid = documentid

    @property
    def profile(self):
        return self._profile

    @profile.setter
    def profile(self, profile):
        self._profile = profile

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


class DB_Tools(object):
    """
    Class to manage connections to databases and typical processes
    """

    def __init__(self, dbserver, dbname, username=None, password=None,
                 driver="ODBC Driver 13 for SQL Server"):
        """
        Initialise DB_Tools class
        :param dbserver: database instance (SQL Server)
        :param dbname: database name.
        :param username: database username. Optional.
        If None then trusted connection.  Password required if not None
        :param password: database password.  Optional, used with username
        :param driver: Optional. default="ODBC Driver 13 for SQL Server".
        Could also use "SQL Server" but this is an old driver and must use
        trusted connection for that driver
        """
        api_client = ApiClient()
        self.logger = api_client.configuration.packagelogger
        self.logger.debug("Initiated Database module")
        driver = self.check_sql_server_driver(driver)
        if driver == None:
            raise ValueError("ODBC Driver [{0}] not found".format(driver))
        if username == None:
            self.connstr = "Driver={" + driver + "};" + """
            Server={0};Database={1};Trusted_Connection=yes;
            APP=Assetic Asset Sync""".format(dbserver, dbname)
            # ;Charset=utf-8
        else:
            self.connstr = "Driver={" + driver + "};" + """
            Server={0};Database={1};UID={2};PWD={3};
            APP=Assetic Asset Sync""".format(dbserver, dbname, username,
                                             password)

    def check_sql_server_driver(self, driver):
        """
        Check that the driver passed in is installed.  If not found will
        find a SQL Server driver to use
        Will log a warning if passed in driver not found 
        :param driver: driver name
        :returns: driver name or none if no valid drivers found
        """
        try:
            drivers = pyodbc.drivers()
            if len(drivers) == 0:
                ##can't get driver list so have to assume ok
                return driver
            if driver in drivers:
                ##passed in driver exists
                return driver
            ##look for a driver.  Best to use more recent drivers so will look
            ##for drivers in a specific order
            preferred_drivers = ["ODBC Driver 17 for SQL Server",
                                 "ODBC Driver 13 for SQL Server",
                                 "ODBC Driver 11 for SQL Server",
                                 "SQL Server Native Client 11.0",
                                 "SQL Server Native Client 10.0",
                                 "SQL Server"]
            for preferred_driver in preferred_drivers:
                if preferred_driver in drivers:
                    msg = "Using default ODBC driver [{0}] because driver " \
                          "[{1}] not installed".format(preferred_driver, driver)
                    self.logger.warning(msg)
                    return preferred_driver
                ##not in list
                return None
        except:
            ##can't get driver list so have to assume ok
            return driver

    @contextmanager
    def open_db_connection(self, commit=False):
        """
        Use contextmanager to manage connections so we cleanup connection
        as we go to avoid database locking issues on exception
        """
        self.logger.debug("in open db connection")
        try:
            connection = pyodbc.connect(self.connstr)
        except pyodbc.Error as err:
            self.logger.error(str(err), exc_info=True)
            raise err
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise ex
        try:
            if six.PY2:
                connection.setencoding(str, 'utf-8')
                connection.setencoding(unicode, 'utf-16le')
                connection.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
                connection.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-16le')
                # connection.setencoding(str, encoding='utf-8')
                # connection.setencoding(unicode, encoding='utf-8', ctype=pyodbc.SQL_WCHAR)

            cursor = connection.cursor()
            yield cursor
        except pyodbc.DatabaseError as err:
            cursor.rollback()
            self.logger.error(str(err), exc_info=True)
            raise err
        except UnicodeDecodeError as ex:
            self.logger.error(str(ex), exc_info=True)
            cursor.rollback()
            raise ex
        except Exception as ex:
            cursor.rollback()
            self.logger.error(ex, exc_info=True)
            raise ex
        else:
            if commit:
                cursor.commit()
            else:
                cursor.rollback()
        finally:
            connection.close()

    def data_sync_to_db(self, allrows, columns, dbtable, keyfield, logtable
                        , allow_delete=False, truncation_indicator=None):
        """
        For a array containing csv delimited data sync to db.
        Assumes data in columns parameter is the headers for the csv array
        Param allrows: the array of data to sync
        Param columns: the list of column headers in same order as data
        Param dbtable: the database table to sync with
        Param keyfield: the primary key used to determine if new or update
        Param logtable: the name of the table to log inserts,updates,deletes
        Param allow_delete: if True then delete from dbtable if not in allrows
        Param truncation_indicator: if emtpty string or a string value then
        the data will be truncated to field length less length of
        truncation_indicator which will be applied as a suffix.
        Only applies to nvarchar field
        Returned: 0= Success (no db error) else 1 (Exception)
        """

        # default column length to apply if no table
        default_length = 500

        # name for tmp table we'll write data dump to
        tmpdbtable = "#{0}_tmp".format(dbtable)

        # get list of columns in target table (first check if it exists)
        existingcolumns = []
        returncode, dbtable_exists = self.chk_table_exists(dbtable)
        if returncode != 0:
            return returncode
        if dbtable_exists == True:
            returncode, existingcolumns = self.get_columns_for_table(dbtable)
            if returncode != 0:
                return returncode
        if len(existingcolumns) == 0:
            ##no existing output table so match to columns passed in
            # use [:] (strip) to instead of columns.copy() for 2.7 compatibility
            existingcolumns = columns[:]

        # get list of columns in log table (first check if it exists)
        existinglogcolumns = []
        returncode, log_exists = self.chk_table_exists(logtable)
        if returncode != 0:
            return returncode
        if log_exists == True:
            returncode, existinglogcolumns = self.get_columns_for_table(
                logtable)
            if returncode != 0:
                return returncode
        if len(existinglogcolumns) == 0:
            # no existing log table so set to be same as target table
            # use [:] (strip) to instead of .copy() for 2.7 compatibility
            existinglogcolumns = existingcolumns[:]

        # make sure key field in target table
        # unicode lower() handled differently in PY2 and PY3
        keyexists = True
        if six.PY3:
            if not (keyfield.lower().strip('[').strip(']') in map(
                    str.lower, existingcolumns)):
                keyexists = False
        else:
            if not (keyfield.lower().strip('[').strip(']') in map(
                    string.lower, existingcolumns)):
                keyexists = False

        if keyexists == False:
            msg = (
                "Key field '{0}' is not a column in the table '{1}', task will"
                " not be processed").format(keyfield, dbtable)
            self.logger.error(msg)
            return 1

        # make sure key field in log table
        # unicode lower() handled differently in PY2 and PY3
        keyexists = True
        if six.PY3:
            if not (keyfield.lower().strip('[').strip(']') in map(
                    str.lower, existinglogcolumns)):
                keyexists = False
        else:
            if not (keyfield.lower().strip('[').strip(']') in map(
                    string.lower, existinglogcolumns)):
                keyexists = False

        if not keyexists:
            msg = (
                "Key field [{0}] is not a column in the table [{1}], task will"
                " not be processed").format(keyfield, logtable)
            self.logger.error(msg)
            return 1
        else:
            # don't need key field for log data output so remove from list
            for chk in existinglogcolumns:
                if chk.lower() == keyfield.lower().strip('[').strip(']'):
                    existinglogcolumns.remove(chk)
                    break

        # get the database table column names and build the various tables
        insertcolumns = []
        diffinsertcolumns = []
        diffupdatecolumns = []
        diff_compare_columns = []
        createtmpcolsbyselect = []
        logcreatecolumns = []
        logoutputcolumns = []
        cteselectcolumns = []

        if truncation_indicator:
            # Need column lengths so can apply data truncation
            col_lengths = self._build_column_length_dict(dbtable, columns,
                                                         default_length)

        # add a "?" for each column to use in sql parameter settings
        parammark = []

        # 'columns' is the complete list of columns in the source data
        for column in columns:
            insertcolumns.append("[{0}]".format(column))
            parammark.append("?")

            if column in existingcolumns:
                diffinsertcolumns.append("[{0}]".format(column))
                diffupdatecolumns.append("a.[{0}]=c.[{0}]".format(column))
                createtmpcolsbyselect.append("[{0}]".format(column))
                if column.lower() != keyfield.lower().strip('[').strip(']'):
                    logcreatecolumns.append("[{0}]".format(column))
                    diff_compare_columns.append(
                        "isnull(a.[{0}],'')<>isnull(c.[{0}],'')".format(column))
            else:
                # this column will be loaded in tmp table, but not synced
                msg = ("column [{0}] in export data is not in table [{1}] "
                       "and will be excluded").format(column, dbtable)
                self.logger.warning(msg)
                # set a default datatype since it's not in target table
                createtmpcolsbyselect.append(
                    "convert(nvarchar({1}),'') as [{0}]"
                        .format(column, default_length))

            if truncation_indicator:
                # define the field list to select from
                if column in col_lengths and col_lengths[column] > 0:
                    # truncating data, so apply truncation and suffix to select
                    # from cte
                    cteselectcolumns.append(
                        """case when len([{0}])>{1} then concat(left([{0}],
                        {2}),'{3}') else [{0}] end""".format(
                            column, col_lengths[column],
                            col_lengths[column] - len(truncation_indicator),
                            truncation_indicator)
                    )
                else:
                    # this column won't be truncated
                    cteselectcolumns.append("[{0}]".format(column))

        if len(diff_compare_columns) == 0:
            # dummy sqlcompare so merge statement not break
            diff_compare_columns.append("1=1")

        for logcolumn in existinglogcolumns:
            if logcolumn in columns and logcolumn in existingcolumns:
                logoutputcolumns.append("[{0}]".format(logcolumn))
            else:
                if logcolumn not in ['action', 'syncdate']:
                    # the column is not in the data
                    if logcolumn not in columns \
                            and logcolumn in existingcolumns \
                            and "[{0}]".format(logcolumn) \
                            not in logcreatecolumns:
                        # the column is in the target table so include in log
                        # table (if we are creating the log table.)
                        logcreatecolumns.append("[{0}]".format(logcolumn))
                    else:
                        msg = ("column [{0}] in log table is not in the "
                               "export data and is not in the target "
                               "table [{1}] and so it will be ignored").format(
                            logcolumn, dbtable)
                        self.logger.warning(msg)

        # need to remove spurious characters from tmpdbtable street number field
        sqlstnumupdate = None
        strnumwords = ["asset", "street", "number"]
        for insertcol in diffinsertcolumns:
            if all(word in insertcol.lower() for word in strnumwords):
                # Asset Street Number is in the column name
                sqlstnumupdate = "update {0} set {1} = " \
                                 "replace(replace({1},'=',''),'\"','')".format(
                    tmpdbtable, insertcol)

        sqltblchktmp = "select object_id('{0}')".format(tmpdbtable)
        sqltruncatetmp = "drop table  {0}".format(tmpdbtable)
        sqlcreatetmp = """select {0} into {1} from {2} where 1=0""".format(
            ",".join(createtmpcolsbyselect), tmpdbtable, dbtable)

        # determine if primary key set for tables, if not prepare sql
        sqltempkeynotnull = None
        sqlsetkeynotnull = None
        sqlkeypk = None
        if dbtable_exists == False:
            sqlsetkeynotnull = "alter table {0} alter column {1} " \
                               "nvarchar(100) not null".format(dbtable,
                                                               keyfield)
            sqlkeypk = "alter table {0} " \
                       "add CONSTRAINT {0}_key_PK PRIMARY KEY({1})".format(
                dbtable, keyfield)
        else:
            # target table exists, check if key field is not null
            keychk, keyinfo = self.get_column_info(dbtable,
                                                   keyfield.strip("[").strip(
                                                       "]"))
            if keychk != 0:
                msg = "Unable to get column info for key field {0}".format(
                    keyfield)
                self.logger.warning(msg)
            else:
                kcollation = keyinfo[0]
                knullable = keyinfo[1]
                kmax = keyinfo[2]

                if knullable.upper() == "YES":
                    msg = "Key field {0} in table {1} should be set as " \
                          "'NOT NULL' with a unique index/primary key " \
                          "constraint".format(keyfield, dbtable)
                    self.logger.warning(msg)
                    # SQL to make the temp table key field nullable
                    sqltempkeynotnull = "alter table {0} " \
                                        "alter column {1} nvarchar({2})" \
                                        " COLLATE {3} not null".format(
                        tmpdbtable, keyfield, kmax, kcollation)
        sqltempkeypk = "alter table {0} " \
                       "add CONSTRAINT tmp{1}key_PK PRIMARY KEY({2})".format(
            tmpdbtable, dbtable, keyfield)

        sqlcreate = """create table {0} ({2} nvarchar({1}))
            """.format(
            dbtable, default_length
            , "nvarchar({0}),".format(default_length).join(insertcolumns))

        sqllogcreate = """select convert([nvarchar](10),'') as action,
            {1},convert([datetime],getdate()) as [syncdate],{2} into {0}
            from {3} where 1=0""".format(
            logtable, keyfield,
            ",".join(logcreatecolumns), dbtable)

        if truncation_indicator:
            # this will build an statement where the data is loaded to the cte
            # and then the truncating using case statements to test length
            # will be applied against the cte table.  This means we only
            # need to have a single binding variable (parameter) for each
            # field, because the case statement references the field
            # multiple times.  The case is defined in cteselectcolumns
            sqlinsert = """with cte ({0}) as (select {1})
            insert into {2} ({3}) select {4} from cte
            """.format(",".join(insertcolumns)
                       , ",".join(parammark)
                       , tmpdbtable
                       , ",".join(insertcolumns)
                       , ",".join(cteselectcolumns))
        else:
            # insert string if not truncating fields
            sqlinsert = "insert into {0} (".format(tmpdbtable)
            sqlinsert = sqlinsert + ",".join(insertcolumns) + ") values ("
            sqlinsert = sqlinsert + ",".join(parammark) + ")"

        # Now add data to sql insert string and do insert
        # (using 'insertmany' effectively row by row)
        # now refresh base table from temp table where there are changes
        # write the change to the archive file

        # include DELETE option which requires a change to the sql
        # sqldiff = """
        # WITH diff as ( select {2}
        #     FROM {0}
        #     except select {2}
        #     FROM {1}
        #     )
        #     MERGE {1} as a using diff as c on
        #     (c.{5} COLLATE database_default=a.{5} COLLATE database_default)
        #     when MATCHED then update set {3}
        #     When not matched then insert
        #     ({2})
        #     values ({2})
        #     output $action,inserted.{5},getdate(),deleted.{6} into {4}
        #     ([action],{5},[syncdate],{7});
        # """.format(tmpdbtable, dbtable, ",".join(diffinsertcolumns),
        #            ",".join(diffupdatecolumns), logtable, keyfield,
        #            ",deleted.".join(logoutputcolumns),
        #            ",".join(logoutputcolumns))
        delete_syntax = ""
        if allow_delete:
            delete_syntax = " when not matched by source then delete "

        sqldiff = """
        WITH diff as ( select {2}
            FROM {0}
            )
            MERGE {1} as a using diff as c on
            (c.{5} COLLATE database_default=a.{5} COLLATE database_default)
            when MATCHED and {8} then update set {3}
            When not matched by target then insert
            ({2}) 
            values ({2})
            {9}
            output $action,isnull(inserted.{5},deleted.{5}),getdate(),
            deleted.{6} into {4}([action],{5},[syncdate],{7});
        """.format(tmpdbtable, dbtable, ",".join(diffinsertcolumns),
                   ",".join(diffupdatecolumns), logtable, keyfield,
                   ",deleted.".join(logoutputcolumns),
                   ",".join(logoutputcolumns),
                   " or ".join(diff_compare_columns), delete_syntax)

        # Now execute all the sql statements in the one transaction block
        # Bit slow opening & closing db connection, but transaction block
        # works well
        try:
            with self.open_db_connection(True) as cursor:
                # if permanent table not exist then create
                if dbtable_exists == False:
                    # table not found - create permament table for current data
                    self.logger.debug(sqlcreate)
                    cursor.execute(sqlcreate)
                    if sqlsetkeynotnull != None:
                        self.logger.debug(sqlsetkeynotnull)
                        cursor.execute(sqlsetkeynotnull)
                    if sqlkeypk != None:
                        self.logger.debug(sqlkeypk)
                        cursor.execute(sqlkeypk)

                # check if temporary table exists
                self.logger.debug(sqltblchktmp)
                cursor.execute(sqltblchktmp)
                row = cursor.fetchone()
                if row[0] == None:
                    self.logger.debug(sqlcreatetmp)
                    cursor.execute(sqlcreatetmp)
                    if sqltempkeynotnull != None:
                        # set the key field as not null
                        self.logger.debug(sqltempkeynotnull)
                        cursor.execute(sqltempkeynotnull)
                        sqltempkeynotnull = None
                else:
                    self.logger.debug(sqltruncatetmp)
                    cursor.execute(sqltruncatetmp)

                # if log table not exist then create
                if log_exists == False:
                    # table not found - create permament table for logging changes
                    self.logger.debug(sqllogcreate)
                    cursor.execute(sqllogcreate)
                # write all the data to the temp table in db.
                self.logger.debug(sqlinsert)
                cursor.executemany(sqlinsert, allrows)
                # update street number field to remove spurious chars
                if sqlstnumupdate != None:
                    self.logger.debug(sqlstnumupdate)
                    cursor.execute(sqlstnumupdate)
                # set pk on tmp table if not null set on field
                if sqltempkeynotnull == None:
                    self.logger.debug(sqltempkeypk)
                    cursor.execute(sqltempkeypk)
                # execute diff statement to populate permanent tables from temp table
                self.logger.debug(sqldiff)
                cursor.execute(sqldiff)
                # drop temp table
                self.logger.debug(sqltruncatetmp)
                cursor.execute(sqltruncatetmp)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0

    def _build_column_length_dict(self, dbtable, csv_columns, default_length):
        """
        Get the char length for each field in the table, set as 0 if no char
        length.  Also make sure each field in csv column list also has a
        dault length if there is not equivalent db field
        Also make sure the
        :param dbtable: The database table to build the dict for
        :param csv_columns: List of column names in csv file
        :param default_length: default length if no column in DB
        :return:  A dictionary of column names as key, with length as value
        """
        column_lengths = dict()
        # get field lengths for columns so we can build truncation logic
        chk, colinfo = self.get_columns_info_for_table(dbtable)
        if chk == 0:
            # no errors add to dict
            for col in colinfo:
                if col.CHARACTER_MAXIMUM_LENGTH:
                    column_lengths[col.column_name] = \
                        col.CHARACTER_MAXIMUM_LENGTH
                else:
                    column_lengths[col.column_name] = 0
        # Now make sure all fields in csv data have a default length
        for csv_col in csv_columns:
            if csv_col not in column_lengths:
                column_lengths[csv_col] = default_length
        # return dict
        return column_lengths

    def get_columns_for_table(self, dbtable):
        """
        Get list of columns in database table
        :param dbtable: The database table
        :returns: Tuple - 0= success (no db error), else 1 and
        results (an array of columns)
        """
        sql = """select column_name from Information_schema.columns 
            where table_name='{0}' order by ORDINAL_POSITION asc""".format(
            dbtable)
        returncode, results = self.execute_select(sql)
        if returncode > 0:
            msg = "Error checking columns for table [{0}]. ".format(dbtable)
            self.logger.error(msg)
            return returncode, None

        msg = "No columns found for table [{0}]. " \
              "Check that table exists and columns can be selected " \
              "from INFORMATION_SCHEMA.COLUMNS".format(dbtable)
        if results is None:
            self.logger.error(msg)
            return 1, None
        if returncode == 0 and len(results) == 0:
            self.logger.error(msg)
            return 1, None
        columnarr = []
        for result in results:
            # results come back as a tuple even though only 1 column per record
            columnarr.append(result[0])
        return returncode, columnarr

    def get_columns_info_for_table(self, dbtable):
        """
        Get list of columns in database table with data type,nulls,
        collation and length
        :param dbtable: The database table
        :returns: Tuple - 0= success (no db error), else 1 and
        results (an array of name, collation_name, nullable, max_size, type)
        """
        sql = """select column_name, COLLATION_NAME,IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH, DATA_TYPE from 
            Information_schema.columns 
            where table_name='{0}' order by ORDINAL_POSITION asc""".format(
            dbtable)
        returncode, results = self.execute_select(sql)
        if returncode > 0:
            msg = "Error checking columns for table [{0}]. ".format(dbtable)
            self.logger.error(msg)
            return returncode, None

        msg = "No columns found for table [{0}]. " \
              "Check that table exists and columns can be selected " \
              "from INFORMATION_SCHEMA.COLUMNS".format(dbtable)
        if results is None:
            self.logger.error(msg)
            return 1, None
        if returncode == 0 and len(results) == 0:
            self.logger.error(msg)
            return 1, None
        return returncode, results

    def get_column_info(self, dbtable, column):
        """
        Get info about a column
        :param dbtable: The database table
        :returns: Tuple - 0= success (no db error), else 1 and
        array of collation_name, nullable, max_size
        """
        sql = """select COLLATION_NAME,IS_NULLABLE,
            CHARACTER_MAXIMUM_LENGTH from INFORMATION_SCHEMA.COLUMNS
            where COLUMN_NAME='{0}' and TABLE_NAME='{1}'""".format(
            column, dbtable)
        returncode, results = self.execute_select(sql)
        if returncode > 0:
            msg = "Error checking column [{0}] for table [{1}]. ".format(
                column, dbtable)
            self.logger.error(msg)
            return returncode, None

        msg = "No column [{0}] found for table [{1}]. " \
              "Check that table exists and column can be selected " \
              "from INFORMATION_SCHEMA.COLUMNS".format(column, dbtable)
        if results == None:
            self.logger.error(msg)
            return 1, None
        if returncode == 0 and len(results) == 0:
            self.logger.error(msg)
            return 1, None

        for result in results:
            ##results come back as a tuple even though only 1 column per record
            columninfo = result
        if len(columninfo) != 3:
            returncode = 1
        return returncode, columninfo

    def chk_table_exists(self, dbtable):
        """
        checks if db table exists
        :param dbtable: The database table
        :returns: tuple, returncode indicating if there was an erorr (nonzero)
        and True/False for table existance
        """
        sql = "select object_id('{0}')".format(dbtable)
        returncode, results = self.execute_select(sql)
        if returncode != 0:
            msg = "Error checking if table [{0}] exists. ".format(dbtable)
            self.logger.error(msg)
            return returncode, None
        exists = True
        if results[0][0] == None:
            exists = False

        return returncode, exists

    def execute_select(self, sql):
        """
        Helper method to run an SQL select
        param sql: SQL select statement
        Returned: Tuple - 0= success (no db error), else 1 and
        results (an array of results)
        """
        self.logger.debug(sql)
        try:
            with self.open_db_connection(True) as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as ex:
            self.logger.exception(ex)
            return 1, None

        return 0, results

    def execute_single(self, sql, datarow=None):
        """
        Helper method to run a single record SQL insert, update, or delete
        param sql: the sql statement
        param datarow is optional parameter.  Has data as tuple for sql
        Returned: 0= Success (no db error) else 1 (Exception)
        """
        self.logger.debug(sql)
        self.logger.debug(datarow)
        try:
            with self.open_db_connection(True) as cursor:
                if datarow != None:
                    cursor.execute(sql, datarow)
                else:
                    cursor.execute(sql)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0

    def execute_many(self, sql, datarows):
        """
        Helper method to run a multiple record SQL insert, update, or delete
        Returned: 0= Success (no db error) else 1 (Exception)
        """
        try:
            with self.open_db_connection(True) as cursor:
                cursor.executemany(sql, datarows)
        except Exception as ex:
            self.logger.exception(ex)
            return 1
        return 0


class FullAssetExport(object):
    """
    Class to manage the process that exports an asset with it's components
    and dimensions etc on a single row per asset
    """

    def __init__(self, api_client=None):
        """
        initialise the CompleteAssetExport module
        :param api_client: api client connection def
        """
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger

        self.asset_tools = AssetTools()
        self.sync_processes = SyncToLocalProcesses()
        self.api_helper = APIHelper()

        self.core_attributes = dict()
        self.core_attributes["Id"] = "id"
        self.core_attributes["AssetId"] = "asset_id"
        self.core_attributes["AssetName"] = "asset_name"
        self.core_attributes["AssetCategory"] = "asset_category"
        self.core_attributes["AssetCategoryId"] = "asset_category_id"
        self.core_attributes["AssetExternalIdentifier"] = "asset_external_identifier"
        self.core_attributes["LastModified"] = "last_modified"
        self.core_attributes["AssetClass"] = "asset_class"
        self.core_attributes["AssetSubClass"] = "asset_sub_class"
        self.core_attributes["AssetType"] = "asset_type"
        self.core_attributes["AssetSubType"] = "asset_sub_type"
        self.core_attributes["AssetCriticality"] = "asset_criticality"
        self.core_attributes["AssetWorkGroup"] = "asset_work_group"
        self.core_attributes["Status"] = "status"
        self.core_attributes["AssetMaintenanceType"] = "asset_maintenance_type"
        self.core_attributes["AssetMaintenanceSubType"] = "asset_maintenance_sub_type"

    def export_asset(self, search_filter, export_defs):
        """
        Export assets to one or more csv file based on export definition.
        The same assets are exported for each def, but the attributes etc
        can vary for each export.
        :param search_filter: a filter on the asset search
        :param export_defs: a list of definitions defining the output
        :return: success =0 else error
        """
        if not isinstance(export_defs, list):
            self.logger.error("Require a list of definition objects")
            return 1

        template_list = list()
        inclusions = list()
        attributes = list()
        for x in export_defs:
            if "config_file" not in x:
                msg = "'config_file' key missing from export definition"
                self.logger.error(msg)
                return 1

            mapping, column_order = self.prepare_fields_from_config(
                x["config_file"])
            for k, v in six.iteritems(mapping):
                if v.level_type == "asset":
                    if v.asset_field in self.core_attributes:
                        # convert the core field name to the API pythonic name
                        v.asset_field = self.core_attributes[v.asset_field]
                    else:
                        # add to list of attributes for search to get and flag
                        # as attribute
                        if v.asset_field not in attributes:
                            attributes.append(v.asset_field)
                        v.level_type = "attributes"
                elif v.level_type == "location":
                    if "location" not in inclusions:
                        inclusions.append("location")
                elif v.level_type == "component":
                    if "component" not in inclusions:
                        inclusions.append("components")
                elif v.level_type == "dimensions":
                    if "dimensions" not in inclusions:
                        inclusions.append("dimensions")
                elif v.level_type == "extended_dimensions":
                    if "extended_dimensions" not in inclusions:
                        inclusions.append("extended_dimensions")
                elif v.level_type == "service criteria":
                    if "service_criteria" not in inclusions:
                        inclusions.append("service_criteria")
            template = {"template": mapping,
                        "file": x["output_file"],
                        "prependrow": x["prependrow"],
                        "postpendrow": x["postpendrow"],
                        "column_order": column_order}
            template_list.append(template)

        if len(template_list) > 0:
            kwargs = {"search_filter": search_filter}
            chk = self.process(template_list, attributes, inclusions, **kwargs)
            if chk != 0:
                return chk
        return 0

    def export_category_changes(self, category, export_defs):
        """
        Export assets for a asset category that have been modified in time range
        Export to one or more csv files based on export definition.
        The same assets are exported for each def, but the attributes etc
        can vary for each export.
        :param category: the category to export
        :param export_defs: a list of definitions defining the output
        :return: success =0 else error
        """
        if not isinstance(export_defs, list):
            self.logger.error("Require a list of definition objects")
            return 1

        template_list = list()
        inclusions = list()
        attributes = list()
        for x in export_defs:
            if "config_file" not in x:
                msg = "'config_file' key missing from export definition"
                self.logger.error(msg)
                return 1

            mapping, column_order = self.prepare_fields_from_config(
                x["config_file"])
            for k, v in six.iteritems(mapping):
                if v.level_type == "asset":
                    if v.asset_field in self.core_attributes:
                        # convert the core field name to the API pythonic name
                        v.asset_field = self.core_attributes[v.asset_field]
                    else:
                        # add to list of attributes for search to get and flag
                        # as attribute
                        if v.asset_field not in attributes:
                            attributes.append(v.asset_field)
                        v.level_type = "attributes"
                elif v.level_type == "location":
                    if "location" not in inclusions:
                        inclusions.append("location")
                elif v.level_type == "component":
                    if "component" not in inclusions:
                        inclusions.append("components")
                elif v.level_type == "dimensions":
                    if "dimensions" not in inclusions:
                        inclusions.append("dimensions")
                elif v.level_type == "extended_dimensions":
                    if "extended_dimensions" not in inclusions:
                        inclusions.append("extended_dimensions")
                elif v.level_type == "service criteria":
                    if "service_criteria" not in inclusions:
                        inclusions.append("service_criteria")
            template = {"template": mapping,
                        "file": x["output_file"],
                        "prependrow": x["prependrow"],
                        "postpendrow": x["postpendrow"],
                        "column_order": column_order}
            template_list.append(template)

        if len(template_list) > 0:
            integration_name = "{0}_modified_asset_export".format(category)
            start_date = self.api_helper.get_last_integration_datetime(
                integration_name)
            end_date = datetime.datetime.now()
            kwargs = {"category": category, "start_date": start_date,
                      "end_date": end_date}
            chk = self.process(template_list, attributes, inclusions, **kwargs)
            if chk != 0:
                return chk
            self.api_helper.set_last_integration_datetime(integration_name,
                                                          end_date)
        return 0

    def prepare_fields_from_config(self, config_file):
        """
        Build the dict that defines what fields to get
        csv config file holds the definition.  Must have columns in following
        order:
        output_field - the field name in the output csv
        level_type - one of 'asset','component,'dimension','constant'
        level_value - if component then the name of the component
        asset_field - the field name of the asset, component, dimension
        constant - if a constant then the value of the constant
        field_size - if need to truncate to max length
        :param config_file: full fill path and name of config csv file
        :return: tuple of field dict that define mapping of field and column
        order list
        """
        # get a list of dict objects from config file
        structure = ("output_field", "level_type", "asset_field"
                     , "component_type", "network_measure_type"
                     , "nm_record_type", "service_criteria_type", "constant"
                     , "field_size")
        config_list = self.api_helper.read_csv_file_into_dict(config_file
                                                              , structure)
        if len(config_list) > 0 and \
                config_list[0]["output_field"] == "Output Field Name" and \
                config_list[0]["level_type"] == "Asset Level" and \
                config_list[0]["asset_field"] == "Assetic Field Name":
            # remove header row
            config_list.pop(0)
        column_order = [i["output_field"] for i in config_list]

        mapping = dict()
        asset_levels = ["asset", "attributes", "component", "dimensions"
            , "location", "service criteria", "extended_dimensions"]
        for config in config_list:
            field = CompleteAssetExportFieldMappings()
            if config["level_type"] and config["asset_field"] and \
                    config["level_type"] in asset_levels:
                field.asset_field = config["asset_field"]
                field.level_type = config["level_type"]
                field.component_type = config["component_type"]  # may be null
                field.network_measure_type = config["network_measure_type"]
                field.nm_record_type = config["nm_record_type"]
                field.service_criteria_type = config["service_criteria_type"]
            else:
                field.constant = config["constant"]
            field.field_size = config["field_size"]

            mapping[config["output_field"]] = field
        return mapping, column_order

    def process(self, templates, attributes=None,
                inclusions=[], **kwargs):
        """
        Control method.  Get assets and then output to one or more files
        :param templates: a list of templates that define the output files
        :param attributes: any additional asset attributes or None
        :param inclusions: a list of asset data to get - e.g. components,
        dimensions.  Use to avoid unnecessary API calls
        :param kwargs: use to specify export type.  If "asset_filter" is set
        then export uses a filter to get list of assets, at asset level,
        alternatively set "category", "start_date" and "end_date" for category
        specific export that also finds changes to component and service
        criteria
        :return 0 if success, else error
        """
        self.logger.info("Process New Assets - Start")
        if "asset_filter" in kwargs and kwargs["asset_filter"]:
            asset_filter = kwargs["asset_filter"]
            all_assets = self. \
                asset_tools.get_list_of_complete_assets(asset_filter
                                                        , attributes
                                                        , inclusions)
            if all_assets is None:
                return 1
        elif "category" in kwargs and "start_date" in kwargs and \
                "end_date" in kwargs and kwargs["category"] and \
                kwargs["start_date"] and kwargs["end_date"]:
            all_assets = self. \
                asset_tools.get_list_of_modified_complete_assets_for_category(
                kwargs["category"], kwargs["start_date"], kwargs["end_date"]
                , attributes, inclusions)
            if all_assets is None:
                return 1
        else:
            self.logger.error('Expecting "asset_filter" in kwargs or "category"'
                              '"start_date" and "end_date"')
            return 1
        self.logger.info("{0} assets to export to csv".format(len(all_assets)))
        if len(all_assets) == 0:
            return 0
        chk = 0
        for template in templates:
            self.logger.info("Start Create file {0}".format(template["file"]))
            chk = self.process_assets(all_assets, **template)
            if chk == 0:
                self.logger.info("End Create file {0}".format(template["file"]))
        self.logger.info("Process Assets - Complete")
        return chk

    def process_assets(self, allassets, **kwargs):
        """
        Given list of assets and template create output file
        :param allassets: the assets to process
        :param **kwargs: keys=template,outfile,prependrow,postpendrow
        'template' defines the output file
        'file': the full path and 'outfile' of the file to write
        'prependrow': string to flace at start of file
        'postpendrow':string to place at end of file
        :return 0 if no errors, else non-zero
        """
        if "template" in kwargs:
            template = kwargs["template"]
        else:
            self.logger.error("'template' key missing from kwargs")
            return 1
        if "file" in kwargs:
            file = kwargs["file"]
        else:
            self.logger.error("'file' key missing from kwargs")
            return 1
        column_order = None
        if "column_order" in kwargs:
            column_order = kwargs["column_order"]

        alldata = list()
        for asset in allassets:
            data = self.asset_to_template(asset, template)
            if data is not None:
                alldata.append(data)

        if len(alldata) == 0:
            self.logger.warning("No data for file {0}".format(file))
            return 0

        # now get in csv format
        csvstring = self.format_as_csv(alldata, column_order)
        # prepend row
        if "prependrow" in kwargs and kwargs["prependrow"] != None:
            csvstring = kwargs["prependrow"] + "\r\n" + csvstring
        if "postendrow" in kwargs and kwargs["postendrow"] != None:
            csvstring = csvstring + "\r\n" + kwargs["postpendrow"]

        chk = 0
        if csvstring:
            chk = self.sync_processes.csvstring_to_file(csvstring, file)
        return chk

    def asset_to_template(self, asset, template):
        """
        Get the relevant data based on template from asset object and return
        :param asset: assetic.AssetToolsCompleteAssetRepresentation()
        :param template: the template that defines the columns to create
        :return data: return a dict with the data for each column name
        """
        data = dict()
        for k, v in six.iteritems(template):
            if v.constant is not None:
                data[k] = v.constant
            else:
                # get data from asset
                if v.level_type.lower() == "asset":
                    try:
                        data[k] = getattr(asset.asset_representation,
                                          v.asset_field)
                    except Exception as ex:
                        msg = "asset mapping issue: {0}".format(ex)
                        self.logger.warning(msg)
                        data[k] = None
                elif v.level_type.lower() == "attributes":
                    if v.asset_field not in \
                            asset.asset_representation.attributes:
                        msg = "{0} is not in the asset attributes".format(
                            v.asset_field)
                        self.logger.warning(msg)
                        data[k] = None
                    else:
                        try:
                            data[k] = asset.asset_representation.attributes \
                                [v.asset_field]
                        except Exception as ex:
                            msg = "attribute mapping issue: {0}".format(ex)
                            self.logger.warning(msg)
                            data[k] = None
                elif v.level_type.lower() == "location":
                    if asset.location_representation:
                        locn = asset.location_representation
                        if locn["Data"] and locn["Data"]["properties"] and \
                                locn["Data"]["properties"] \
                                        ["AssetPhysicalLocation"]:
                            # we have an address!
                            addr_obj = locn["Data"]["properties"] \
                                ["AssetPhysicalLocation"]
                            if v.asset_field == "Address":
                                if not addr_obj["StreetNumber"]:
                                    addr_obj["StreetNumber"] = ""
                                if not addr_obj["StreetAddress"]:
                                    addr_obj["StreetAddress"] = ""
                                if not addr_obj["CitySuburb"]:
                                    addr_obj["CitySuburb"] = ""
                                if not addr_obj["State"]:
                                    addr_obj["State"] = ""
                                if not addr_obj["ZipPostcode"]:
                                    addr_obj["ZipPostcode"] = ""
                                if not addr_obj["Country"]:
                                    addr_obj["Country"] = ""
                                flds = [addr_obj["StreetNumber"]
                                    , addr_obj["StreetAddress"]
                                    , addr_obj["CitySuburb"]
                                    , addr_obj["State"]
                                    , addr_obj["ZipPostcode"]
                                    , addr_obj["Country"]]
                                data[k] = " ".join(flds).replace("  ", " "). \
                                    strip()
                            else:
                                if v.asset_field in addr_obj:
                                    data[k] = addr_obj[v.asset_field]
                elif v.level_type.lower() in ("component", "dimensions"
                                              , "service criteria"
                                              , "extended_dimensions"):
                    for comp in asset.components:
                        if getattr(comp.component_representation,
                                   "component_type") == v.component_type:
                            if v.level_type.lower() == "component" and \
                                    not v.service_criteria_type.strip() and \
                                    not v.network_measure_type.strip():
                                # no network measure or service criteria fields
                                # defines so it must be a component field
                                try:
                                    data[k] = getattr(
                                        comp.component_representation
                                        , v.asset_field)
                                except Exception as ex:
                                    msg = "component mapping issue: {0}".format(
                                        ex)
                                    self.logger.warning(msg)
                                    data[k] = None
                            elif v.level_type.lower() == "dimensions" and \
                                    v.network_measure_type.strip() and \
                                    v.nm_record_type.strip():
                                # network measure fields defined so loop through
                                # measures within this component till get
                                # record that matches the fields
                                dims = comp.dimensions
                                for dim in dims:
                                    if getattr(dim,
                                               "network_measure_type") \
                                            == v.network_measure_type \
                                            and getattr(dim,
                                                        "record_type") \
                                            == v.nm_record_type:
                                        try:
                                            data[k] = getattr(dim
                                                              , v.asset_field)
                                            break
                                        except Exception as ex:
                                            msg = "component mapping issue: " \
                                                  "{0}".format(ex)
                                            self.logger.warning(msg)
                                            data[k] = None
                            elif v.level_type.lower() == "extended_dimensions":
                                # loop through measures within this component
                                # till get record that matches the fields
                                dims = comp.extended_dimensions
                                for dim in dims:
                                    if dim["NetworkMeasureType"] \
                                            == v.network_measure_type \
                                            and dim["RecordType"] \
                                            == v.nm_record_type:
                                        try:
                                            data[k] = dim[v.asset_field]
                                            break
                                        except Exception as ex:
                                            msg = "component mapping issue: " \
                                                  "{0}".format(ex)
                                            self.logger.warning(msg)
                                            data[k] = None
                            elif v.level_type.lower() == "service criteria" \
                                    and v.service_criteria_type.strip():
                                # service criteria type label defined so loop
                                # through service criteria till match that type
                                sc_s = comp.service_criteria
                                for sc in sc_s:
                                    if getattr(sc,
                                               "service_criteria_type_label") \
                                            == v.service_criteria_type:
                                        try:
                                            data[k] = getattr(sc
                                                              , v.asset_field)
                                            break
                                        except Exception as ex:
                                            msg = "service criteria mapping " \
                                                  "issue: {0}".format(ex)
                                            self.logger.warning(msg)
                                            data[k] = None
                else:
                    # Assume it is a constant
                    data[k] = v.constant
        return data

    def format_as_csv(self, alldata, column_order=None):
        """
        Given a list of dictionaries get the csv header row from dictionary
        keys and format dictionary values as csv rows
        :param alldata: a list of dictionaries
        :param column_order: a list of column names in order, names match data
        :return csvdata: a list of csvstrings
        """
        if len(alldata) == 0:
            # just return empty string
            return ""

        if column_order is None:
            # Get a list of columns
            columns = map(lambda x: x.keys(), alldata)
            if six.PY2:
                column_order = reduce(lambda x, y: x + y, columns)
            else:
                column_order = functools.reduce(lambda x, y: x | y, columns)

        # set csv writer output to string
        if six.PY2:
            output = io.BytesIO()
            writer = csv.writer(output)
        else:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        # write header columns
        writer.writerow(column_order)
        # loop through data and write to csv
        for i_r in alldata:
            # map data to column list by key to avoid issues with column order
            if six.PY2:
                writer.writerow(map(lambda x: i_r.get(x, "").encode('utf-8')
                                    , column_order))
            else:
                writer.writerow(list(
                    map(lambda x: i_r.get(x, ""), column_order)))
        csvdata = output.getvalue()
        output.close()
        return csvdata


class CompleteAssetExportFieldMappings(object):
    """"
    A structure for defining the output columns of complete asset representation
    """

    def __init__(self, output_field=None, asset_field=None, level_type=None,
                 component_type=None, network_measure_type=None,
                 nm_record_type=None, service_criteria_type=None,
                 constant=None, field_size=0):
        """
        AssetOutputFieldMappings - a model defining output structure
        """
        self.fieldtypes = {
            "output_field": "str",
            "asset_field": "str",
            "level_type": "str",
            "component_type": "str",
            "network_measure_type": "str",
            "nm_record_type": "str",
            "service_criteria_type": "str",
            "constant": "str",
            "field_size": "int"
        }
        self._output_field = output_field
        self._asset_field = asset_field
        self._level_type = level_type
        self._component_type = component_type
        self._network_measure_type = network_measure_type
        self._nm_record_type = nm_record_type
        self._service_criteria_type = service_criteria_type
        self._constant = constant
        self._field_size = field_size

    @property
    def output_field(self):
        return self._output_field

    @output_field.setter
    def output_field(self, output_field):
        self._output_field = output_field

    @property
    def asset_field(self):
        return self._asset_field

    @asset_field.setter
    def asset_field(self, asset_field):
        self._asset_field = asset_field

    @property
    def level_type(self):
        return self._level_type

    @level_type.setter
    def level_type(self, level_type):
        self._level_type = level_type

    @property
    def component_type(self):
        return self._component_type

    @component_type.setter
    def component_type(self, component_type):
        self._component_type = component_type

    @property
    def network_measure_type(self):
        return self._network_measure_type

    @network_measure_type.setter
    def network_measure_type(self, network_measure_type):
        self._network_measure_type = network_measure_type

    @property
    def nm_record_type(self):
        return self._nm_record_type

    @nm_record_type.setter
    def nm_record_type(self, nm_record_type):
        self._nm_record_type = nm_record_type

    @property
    def service_criteria_type(self):
        return self._service_criteria_type

    @service_criteria_type.setter
    def service_criteria_type(self, service_criteria_type):
        self._service_criteria_type = service_criteria_type

    @property
    def constant(self):
        return self._constant

    @constant.setter
    def constant(self, constant):
        self._constant = constant

    @property
    def field_size(self):
        return self._field_size

    @field_size.setter
    def field_size(self, field_size):
        self._field_size = field_size

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

##class UTF8Recoder:
##    def __init__(self, f, encoding):
##        self.reader = codecs.getreader(encoding)(f)
##    def __iter__(self):
##        return self
##    def next(self):
##        return self.reader.next().encode("utf-8")
##
##class UnicodeReader:
##    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
##        f = UTF8Recoder(f, encoding)
##        self.reader = csv.reader(f, dialect=dialect, **kwds)
##    def next(self):
##        '''next() -> unicode
##        This function reads and returns the next line as a Unicode string.
##        '''
##        row = self.reader.next()
##        return [unicode(s, "utf-8") for s in row]
##    def __iter__(self):
##        return self
