"""
    Create Assetic requests from CRM and Update CRM with Assetic changes
"""
import abc
# import base64
import datetime
import os
# import sys
import time
from operator import itemgetter
from pprint import pformat
import dateutil.parser
import six
# from assetic import FilePropertiesRepresentation

from ..api import AuthApi
from ..api import DocumentApi
from ..api import WorkOrderApi
from ..api import WorkRequestApi
from ..api import ResourceApi
from ..api_client import ApiClient

from ..models.document_representation \
    import DocumentRepresentation
from ..models.work_request \
    import WorkRequest
from ..rest import ApiException
from ..tools.odata import OData


class CRMTools(object):
    """
    Class to provide Work Request integration processes
    """

    def __init__(self, crm, api_client=None, **kwargs):
        """
        initialise object
        :param crm: The CRM to integrated to. Currently support "Authority"
        or an instantiated class that implements CRMPluginBase
        :param api_client: sdk client object, optional
        :param **kwargs: provide any config specific to the CRM
        """
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger
        self.resourceapi = ResourceApi()
        self.wrapi = WorkRequestApi()
        self.wkoapi = WorkOrderApi()
        self.auth_api = AuthApi()
        self.odata = OData()
        self.docapi = DocumentApi()

        self._crm_tools = None
        if isinstance(crm, str):
            self._crm_name = crm
            if crm.lower() == "authority":
                self._crm_tools = self.init_authority_crm(**kwargs)
            elif crm.lower() == "authoritytest":
                self._crm_tools = self.init_authority_crm_test(**kwargs)
        elif isinstance(crm, CRMPluginBase):
            self._crm_tools = crm
            self._crm_name = ""
        if not self._crm_tools:
            self.logger.error("'{0}' is an unsupported CRM plugin.\nSupported"
                              " CRM plugins are 'Authority'".format(crm))

        self._wo_status_note = dict()
        self._wr_status_note = dict()

        # use Assetic documents to record last integration dates
        self._wr_last_date_doc_id = None
        self._wo_last_date_doc_id = None

        self._wr_supporting_info_to_crm = True
        self._wo_supporting_info_to_crm = True
        self._wo_schedule_dates_to_crm = False
        self._wo_target_dates_to_crm = False

        self._wo_actual_finish_date_for_crm_close = False

        # default WR Status to initiate CRM Close
        self._close_crm_statuses = [5, 6, 7, 8]

        # get the guid of the integration user so can exclude comments that
        # were added by the integration user
        self._integration_user_guid = self._get_integration_user_guid()
        if isinstance(self._integration_user_guid, int):
            raise Exception

    @property
    def crm_tools(self):
        """
        Reference to the instantiated CRM class
        """
        return self._crm_tools

    @property
    def wo_status_note(self):
        """
        A dictionary where key is wo status and value is what to use for note
        """
        return self._wo_status_note

    @wo_status_note.setter
    def wo_status_note(self, wo_status_note):
        self._wo_status_note = wo_status_note

    @property
    def wr_status_note(self):
        """
        A dictionary where key is wr status and value is what to use for note
        """
        return self._wr_status_note

    @wr_status_note.setter
    def wr_status_note(self, wr_status_note):
        self._wr_status_note = wr_status_note

    @property
    def wr_supporting_info_to_crm(self):
        """
        Get Boolean indicating if Work Request Supporting Information
        should be sent to CRM as a note
        """
        return self._wr_supporting_info_to_crm

    @wr_supporting_info_to_crm.setter
    def wr_supporting_info_to_crm(self, wr_supporting_info_to_crm):
        """
        Set Boolean indicating if Work Request Supporting Information
        should be sent to CRM as a note
        """
        self._wr_supporting_info_to_crm = wr_supporting_info_to_crm

    @property
    def wo_supporting_info_to_crm(self):
        """
        Get Boolean indicating if Work Order Supporting Information
        should be sent to CRM as a note
        """
        return self._wo_supporting_info_to_crm

    @wo_supporting_info_to_crm.setter
    def wo_supporting_info_to_crm(self, wo_supporting_info_to_crm):
        """
        Set Boolean indicating if Work Order Supporting Information
        should be sent to CRM as a note
        """
        self._wo_supporting_info_to_crm = wo_supporting_info_to_crm

    @property
    def wo_schedule_dates_to_crm(self):
        """
        Get Boolean indicating if Work Order Scheduled dates
        should be sent to CRM as a note
        """
        return self._wo_schedule_dates_to_crm

    @wo_schedule_dates_to_crm.setter
    def wo_schedule_dates_to_crm(self, value):
        """
        Set Boolean indicating if Work Order Scheduled dates
        should be sent to CRM as a note
        """
        self._wo_schedule_dates_to_crm = value

    @property
    def wo_target_dates_to_crm(self):
        """
        Get Boolean indicating if Work Order Target dates
        should be sent to CRM as a note
        """
        return self._wo_target_dates_to_crm

    @wo_target_dates_to_crm.setter
    def wo_target_dates_to_crm(self, value):
        """
        Set Boolean indicating if Work Order Target dates
        should be sent to CRM as a note
        """
        self._wo_target_dates_to_crm = value

    @property
    def close_crm_statuses(self):
        """
        Get list of WR statuses used to flag CRM close
        """
        return self._close_crm_statuses

    @close_crm_statuses.setter
    def close_crm_statuses(self, close_crm_statuses):
        """
        Set list of WR statuses used to flag CRM close
        """
        if isinstance(close_crm_statuses, list):
            self._close_crm_statuses = close_crm_statuses
        else:
            self.logger.error("close_crm_statuses should be a list")

    @property
    def wo_actual_finish_date_for_crm_close(self):
        """
        Get Boolean indicating if Work Order Actual Finish Date should be
        used as the 'close date' for a CRM
        """
        return self._wo_target_dates_to_crm

    @wo_actual_finish_date_for_crm_close.setter
    def wo_actual_finish_date_for_crm_close(self, value):
        """
        Set Boolean indicating if Work Order Actual Finish Date should be
        used as the 'close date' for a CRM
        """
        self._wo_actual_finish_date_for_crm_close = value

    # end of property definitions #--------------------------------------------

    def _config_applied(self, config_type):
        # type: (str) -> bool
        """
        Check to return if any configuration options have been manually applied
        durign the plugin setup.

        If no configurations have been manually set, some checks (for new work
        orders, etc.) can be skipped, reducing overhead.

        Some clients do not want any WO stuff at all, so this removes
        the requirement to look for new WOs.

        :param config_type: either 'work order' or 'work request'
        :return:
        """

        if config_type not in ['work request', 'work order']:
            raise TypeError(
                "Pass either 'work order' or 'work request' as config_type "
                "argument. Unrecognised: '{0}'".format(config_type))

        if config_type == 'work order':
            if len(self.wo_status_note) > 0 or \
                    self._wo_schedule_dates_to_crm or \
                    self._wo_target_dates_to_crm or \
                    self._wo_supporting_info_to_crm:
                return True
            else:
                return False
            # return len(self.wo_status_note) > 0
        else:
            if len(self.wr_status_note) > 0 or self._wr_supporting_info_to_crm:
                return True
            else:
                return False
            # return len(self.wr_status_note) > 0

    def init_authority_crm(self, **kwargs):
        """
        Initialise the plugin for Authority integration
        :param kwargs: set of keyword arguments with Authority specific
        parameters
        :return: The plugin which implements class ECMSPluginBase
        """
        try:
            from .crm_plugins.authority_crm import AuthorityCRM
            crm_plugin = AuthorityCRM(**kwargs)
            return crm_plugin
        except ImportError as ex:
            self.logger.error(str(ex))
            return None

    def init_authority_crm_test(self, **kwargs):
        """
        Initialise the test plugin for Authority integration
        :param kwargs: set of keyword arguments with Authority specific
        parameters
        :return: The plugin which implements class ECMSPluginBase
        """
        try:
            from .crm_plugins.authority_crm import AuthorityCRMtest
            crm_plugin = AuthorityCRMtest(**kwargs)
            return crm_plugin
        except ImportError as ex:
            self.logger.error(str(ex))
            return None

    def process(self, check_all_active_crms=False):
        """
        Initiate the CRM-Assetic Work Request integration
        :param check_all_active_crms: If true will use the active CRMs as the
        list to iterate through Assetic Work Requests, instead of using work
        request last modified date to just iterate over changed requests.
        List built from all active currently CRM's. Use periodically as a
        failsafe check - it will take longer to run.
        :return:
        """
        # first process existing requests
        self.logger.info("Process Changed Work Requests - Start")
        chk = self.process_changed_work_requests(check_all_active_crms)
        if chk != 0:
            self.logger.info("Process Changed Work Requests - Aborted")
        else:
            self.logger.info("Process Changed Work Requests - Complete")

        # next process new requests
        self.logger.info("Create Work Requests for new CRM - Start")
        chk = self.process_new_crms()
        if chk != 0:
            self.logger.info("Create Work Requests for new CRM - Aborted")
        else:
            self.logger.info("Create Work Requests for new CRM - Complete")

        # Allow plugin to finalise any connections etc
        chk = self.crm_tools.finalise()

        return chk

    def process_new_crms(self):
        """
        Look for new customer requests and process them.
        Returned: 0=success, else error
        """
        crms = self.crm_tools.get_crm_requests(integrated=False)
        if isinstance(crms, int):
            # there was an error so exit
            return crms
        if crms is None:
            # expecting a list from plugin, empty list if no records
            self.logger.warning("Alter plugin to return an empty list if there"
                                "are no new requests.  Assuming there are no"
                                " new requests.")
            crms = list()
        self.logger.info("Found {0} new CRM's to create a Work Request for".
                         format(len(crms)))
        for wr_crm_obj in crms:
            # wr = WorkRequest()
            # Double check to see if CRM ID already in Assetic
            # return wr as WorkRequest
            wr_guid = self.get_wr_guid_for_crm_id(wr_crm_obj.crm_id)
            if isinstance(wr_guid, int):
                # there was an error
                return wr_guid
            if wr_guid is None:
                # CRM definitely not in Assetic yet.  So create it
                self.logger.info("Create new Work Request for CRM {0}".format(wr_crm_obj.crm_id))
                wr_json = self.create_request(wr_crm_obj)

                if isinstance(wr_json, int):
                    # There was an error
                    chk = self.crm_tools.handle_create_error(wr_crm_obj)
                    if (chk == True):
                        # If error is handled by the client
                        self.logger.info(
                            "Error handled for CRM {0}".format(wr_crm_obj.crm_id))
                        continue
                    else:
                        # If error is not handled
                        self.logger.info(
                            "Error not handled for CRM {0}".format(wr_crm_obj.crm_id))
                        return wr_json

            else:
                # there is an existing WR, so just update CRM.  May have
                # failed on last attempt to update
                self.logger.warning("Work Request [{0}] already exists for CRM "
                                    "[{1}]".format(wr_guid, wr_crm_obj.crm_id))
                try:
                    wr_json = self.wrapi.work_request_get(wr_guid)
                except ApiException as e:
                    self.logger.error("Error getting created work request."
                                      "  Status {0}, Reason {1} {2}".format(
                        e.status, e.reason, e.body))
                    return e.status

            # create the wr representation from the wr json response
            wr = self.api_client.deserialize(
                wr_json, "WorkRequest")

            wr_crm_obj.assetic_wr_representation = wr

            # update CRM with AsseticID and note if there is a status map
            new_note_list = []
            if 2 in self.wr_status_note:
                new_note_list = [
                    WrNote(note=self.wr_status_note[2]
                           , context="Status"
                           , note_date=self._get_datetime_from_string(
                            wr_json["CreatedDateTime"])
                           , assetic_fid=wr.friendly_id_str)]

            chk = self.crm_tools.update_crm_for_new_wr(
                wr_crm_obj, new_note_list)

            if chk != 0:
                # there was an error
                return chk

            self.logger.info("Created new Work Request {0} for CRM ID {1}"
                             "".format(wr.friendly_id_str, wr_crm_obj.crm_id))
        return 0

    def create_request(self, wr_crm_obj):
        """
        Create a new Work Request in Assetic that corresponds with a
        Customer Request task.
        This will update the crm with the new Assetic Work Request GUID
        :param wr_crm_obj: object with raw crm data and work request
        representation
        :return work request json object, else error code
        """

        # create request
        try:
            wr_guid = self.wrapi.work_request_post(
                wr_crm_obj.assetic_wr_representation)
        except ApiException as e:
            self.logger.error("Error creating work request.  Status {0}"
                              ", Reason {1} {2}".format(e.status, e.reason
                                                        , e.body))
            return e.status

        # get the the Assetic work request and return.  It has the generated Id
        return self.get_request(wr_guid)

    def process_changed_work_requests(self, check_all_active_crms=False):
        """
        Get list of requests from CRM where the CRM is still
        active. Assumes CRM is not closed until Assetic request is closed
        :param check_all_active_crms: If true will use the active CRMs as the
        list to iterate through Assetic Work Requests, instead of using work
        request last modified date to just iterate over changed requests.
        List built from all active currently CRM's. Use periodically as a
        failsafe check - it will take longer to run.
        Returned: 0=success, else error
        """

        # get CRM's from CRM that are still active - this will be efficient
        # for a database query since we can get all CRMs with a single query.
        # May not be efficient for a web service?
        crms = self.crm_tools.get_crm_requests(integrated=True)
        if isinstance(crms, int):
            # there was an error so exit
            return crms
        # build a list of active integrated crm's to make it easier to check
        # if a wr is in the active list
        active_crm_wr_guid_list = [i.assetic_wr_representation.id for i in crms]

        # get the last datetime the process ran
        lastdate = self.get_last_integration_datetime_from_doc_link(
            "workrequest")

        # seed max change date to last datetime
        maxdate = lastdate
        self.logger.info("Search for Assetic Work Request changes since {0}"
                         "".format(lastdate))

        if check_all_active_crms:
            # this slower option could be used nightly to catch any wr's that
            # weren't updated, perhaps due to some kind of failure with the date
            # check
            wrs = self.get_wr_list_via_api(active_crm_wr_guid_list)
        else:
            # get list of modified work requests from Assetic since last run
            wrs = self.get_changed_wr_since_date(lastdate)
        if isinstance(wrs, int):
            # there was an error so exit
            return wrs

        # get a list of work orders that are linked to work requests that are
        # linked to active customer requests. Use 'set' get get unique list
        active_crm_wo_guid_list = list(set([i["WorkOrderId"] for i in wrs]))

        if self._config_applied('work order'):
            # First Apply work order status changes and comments
            # because request may close CRM and so can't find crm
            chk = self.apply_wo_status_comment(
                crms, active_crm_wr_guid_list, active_crm_wo_guid_list
                , check_all_active_crms)
            if chk != 0:
                # there was an error so exit
                return chk
        else:
            chk = 0

        if len(wrs) > 0:
            # search ordered by last_mod_date desc, so get max date
            maxdate = self._get_datetime_from_string(wrs[0]["LastModified"])
            self.logger.info("Most recent Assetic Work Request change was {0}"
                             "".format(maxdate))
        else:
            self.logger.info(
                "No changes to Assetic Requests found since last check")

        for wr in wrs:
            # new_note = None
            bclose_crm_task = False
            new_status = None
            new_note_list = list()

            # find the crm from the list of active crms or get the CRM
            wr_crm_obj = None
            if wr["Id"] in active_crm_wr_guid_list:
                # get the crm object from the active list built earlier
                for chk_wr_crm_obj in crms:
                    if chk_wr_crm_obj.assetic_wr_representation.id == \
                            wr["Id"]:
                        wr_crm_obj = chk_wr_crm_obj
                        break
            if not wr_crm_obj:
                # get the crm from the crm using wr guid
                try:
                    wr_crm_obj = self.crm_tools.get_crm_request_for_wr(
                        wr["Id"], wr)
                except TypeError:
                    # Original method only accepted one argument so
                    # TypeError indicates its the original method in place
                    wr_crm_obj = self.crm_tools.get_crm_request_for_wr(
                        wr["Id"])
            # get status and supporting info unless newly created request
            if wr_crm_obj and wr["CreatedDateTime"] != wr["LastModified"]:
                # something has changed in this work request since last check.
                # Don't know if status has changed, but can ignore 'New' (Id=2)
                if wr["WorkRequestStatusId"] != 2:
                    new_status = wr["WorkRequestStatusId"]

                enddate = maxdate
                if wr["WorkRequestStatusId"] in self._close_crm_statuses:
                    # flag to update CRM Task as complete
                    bclose_crm_task = True

                info_list = None
                if self._wr_supporting_info_to_crm:
                    # flag set to include comments in CRM note
                    # get WR comments in date range
                    try:
                        info_list = self.get_wr_comments_in_range(
                            wr["Id"], lastdate, enddate)
                    except Exception:
                        # there was an error so exit
                        return wr
                    for info in info_list:
                        # the note object needs the friendly id and object
                        info.assetic_fid = wr["FriendlyIdStr"]
                        info.wr_obj = wr

                if new_status or (info_list and len(info_list) > 0):
                    # get current CRM note to make sure we aren't
                    # doubling up
                    current_note = self.crm_tools.get_task_note_from_crm(
                        wr_crm_obj.crm_representation)
                    if isinstance(current_note, int):
                        # there was an error getting note
                        return current_note

                    if new_status in self.wr_status_note and \
                            self.wr_status_note[new_status] not in current_note:
                        # this status not in crm note so include
                        new_note_list.append(
                            WrNote(note=self.wr_status_note[new_status]
                                   , context="Status"
                                   , note_date=self._get_datetime_from_string(
                                    wr["LastModified"])
                                   , assetic_fid=wr["FriendlyIdStr"]
                                   , wr_obj=wr))
                    if info_list and len(info_list) > 0:
                        new_info_list = [i for i in info_list if i.note
                                         not in current_note]
                        new_note_list += new_info_list

            if len(new_note_list) > 0 or bclose_crm_task:
                # add comment as a note to task in CRM
                if wr_crm_obj:
                    if new_note_list and len(new_note_list) > 0:
                        # new_note = "[{0}]".format(new_note)
                        self.crm_tools.add_task_note_to_crm(new_note_list
                                                            , wr_crm_obj)
                        # could also add comment at the request level?
                        # self.add_file_note_to_crm(new_note_list,crm.formatted_account)
                    if bclose_crm_task:
                        crm_code_obj = self.crm_tools. \
                            get_resolution_code_for_status(
                            wr["WorkRequestStatusId"]
                            , wr_crm_obj.crm_representation)
                        close_date = None
                        if self._wo_actual_finish_date_for_crm_close and \
                            wr["WorkRequestStatusId"] in [5, 7]:
                                # the work request is closed or resolved
                                # which means there should be a work order
                                # actual finish date
                                close_date = self.get_wko_actual_finish_date(
                                    wo_guid=wr["WorkOrderId"])
                        if not close_date:
                            close_date = self._get_datetime_from_string(
                                wr["LastModified"])
                        if crm_code_obj.crm_resolution_code:
                            # update task status as complete
                            chk = self.crm_tools.update_crm_task_status(
                                wr_crm_obj.crm_representation
                                , crm_code_obj.crm_resolution_code
                                , close_date)
                        # update entire CRM record status as complete
                        if crm_code_obj.close_crm and \
                                crm_code_obj.crm_resolution_code:
                            chk = self.crm_tools.update_crm_master_status(
                                wr_crm_obj.crm_representation
                                , crm_code_obj.crm_resolution_code
                                , close_date)
                        # if cancelled reset ext_ref to allow new potential new
                        # task to be added to CRM and linked to Assetic.
                        # Cancelled ID=8
                        if wr["WorkRequestStatusId"] == 8:
                            chk = self.crm_tools.clear_cancelled_wr_from_crm(
                                wr_crm_obj)
                else:
                    # couldn't find the crm in the. Just log a warning
                    msg = "Couldn't find {0} CRM task for " \
                          "Assetic Request {1}".format(self._crm_name,
                                                       wr["FriendlyIdStr"])
                    self.logger.warning(msg)

        if maxdate > lastdate:
            # update sync date
            chk = self.set_last_integration_datetime_via_doc_link(
                "workrequest", maxdate)
        return chk

    def get_wr_comments_in_range(self, wrguid, startdate, enddate):
        """
        Given a work request object get comments in date range.
        Currently ignoring date range because timestamp not reliable
        :param wrguid: The id of the work request
        :param startdate: the minimum date
        :param enddate: the maximum date
        Returned: return formatted comment string
        """
        try:
            info_list = self.get_supporting_info(wrguid)
        except Exception:
            raise

        comment_list = list()
        for h in info_list:
            # test against system add time, but use 'CreatedDateTime' in
            # comment becuase 'CreatedDateTime' is user (Assetic Mobility)
            # defined
            hdate = dateutil.parser.parse(h["SystemAddedTime"])
            if startdate < hdate <= enddate and \
                    h["CreatedBy"] != self._integration_user_guid:
                # comment_list.append(h["Description"])
                note = WrNote(note=h["Description"], context="Supporting Info"
                              , note_date=self._get_datetime_from_string(
                        h["CreatedDateTime"])
                              , display_name=h["CreatedByDisplayName"]
                              , assetic_uid=h["Id"])
                comment_list.append(note)
        return comment_list

    def apply_wo_status_comment(self, crms, active_crm_wr_guid_list
                                , active_crm_wo_guid_list
                                , check_all_active_crms=False):
        """
        apply any work order comments or status changes since last check
        :param crms: a list of active crm objects from CRM
        :param active_crm_wr_guid_list: a list of WR GUID for active CRMs. Main
        purpose is to make it easier to see if a WR has a crm object in crms
        :param active_crm_wo_guid_list: A list of work orders linked to work
        requests that are linked to active customer requests
        :param check_all_active_crms: If true will iterate through all Assetic
        Work Requests regardless of last mod date.
        List built from all active currently CRM's. Use periodically as a
        failsafe check - it will take longer to run.
        :return 0=success, else error
        """

        # get the last datetime the process ran
        last_date = self.get_last_integration_datetime_from_doc_link(
            "workorder")
        self.logger.info("Search for Assetic Work Order changes since {0}"
                         "".format(last_date))

        # comment_status is a list of mappings indicating if status warrants
        # a comment in CRM
        comment_status = self._wo_status_note

        if not check_all_active_crms:
            # Get a list of request related work orders
            # where something has changed
            wos = self.get_changed_wo(last_date)
            # get a list of work orders where status has changed
            wos_new_status = self.get_wos_with_new_status(last_date)
        else:
            # Get a list of request related work orders
            # WOWorkOrderId
            wos = self.get_wkos_cascade_for_wkos(active_crm_wo_guid_list)
            # assume they all have a new status to ensure status is checked
            wos_new_status = active_crm_wo_guid_list

        if isinstance(wos_new_status, int):
            return wos_new_status

        if isinstance(wos, int):
            return wos
        max_date = last_date
        if len(wos) > 0:
            max_date = dateutil.parser.parse(wos[0]["LastModified"])
        if max_date == last_date:
            # no changes so return
            self.logger.info("No Assetic Work Order changes found since {0}"
                             "".format(last_date))
            return 0
        else:
            self.logger.info("Most recent Assetic Work Order change was {0}"
                             "".format(max_date))
        for wo in wos:
            # get each linked work request and process for each
            if not wo["LinkedWorkRequests"]:
                wo["LinkedWorkRequests"] = list()
            for wr in wo["LinkedWorkRequests"]:
                new_comments = list()
                new_note_list = list()
                if self._wo_supporting_info_to_crm:
                    # flag set to include comments in CRM note
                    # are there new supporting info comments?

                    # each element of supporting info is a dict containing
                    # supp info comment and create date, create resource, etc.
                    for supp_info in wo["SupportingInformation"]:

                        # parse the creation date of the note
                        note_cr_dt = dateutil.parser.parse(
                            supp_info["SystemAddedTime"])

                        # parse the creation date of the work order
                        wo_dt = dateutil.parser.parse(wo["CreatedDateTime"])

                        # Not filter by date because Assetic Mobility may
                        # set the datetime in the past
                        # check to see if there is a comment in date range
                        # valid_dt_check = last_date < note_cr_dt <= max_date

                        # check to see if the note created after the wo creation date
                        creation_dt_check = note_cr_dt > wo_dt

                        # if both are true, copy across the note
                        # if valid_dt_check and creation_dt_check:
                        if creation_dt_check and \
                                supp_info["CreatedBy"] != \
                                self._integration_user_guid:
                            new_comments.append(supp_info)

                    for wo_task in wo["WorkTasks"]:
                        for supp_info in wo_task['SupportingInformation']:
                            note_cr_dt = dateutil.parser.parse(
                                supp_info["SystemAddedTime"])
                            # parse the creation date of the work order
                            wo_dt = dateutil.parser.parse(wo["CreatedDateTime"])

                            creation_dt_check = note_cr_dt > wo_dt
                            if creation_dt_check and \
                                    supp_info["CreatedBy"] != \
                                    self._integration_user_guid:
                                new_comments.append(supp_info)

                date_note = None
                if self._wo_schedule_dates_to_crm \
                        and wo["Scheduling"]["ScheduledStart"] \
                        and wo["Scheduling"]["ScheduledFinish"]:
                    sched_start = dateutil.parser.parse(
                        wo["Scheduling"]["ScheduledStart"]
                    ).strftime("%d-%m-%Y %H:%M")
                    sched_end = dateutil.parser.parse(
                        wo["Scheduling"]["ScheduledFinish"]
                    ).strftime("%d-%m-%Y %H:%M")
                    if sched_start.find(" 00:00") > 0 \
                            and sched_end.find(" 00:00") > 0:
                        # remove meaningless 00:00 (midnight default for start
                        # & finish times - clearly user is not setting times)
                        # This way the CRM note looks nicer.
                        sched_start = sched_start[0:sched_start.find(" 00:00")]
                        sched_end = sched_end[0:sched_end.find(" 00:00")]
                    date_note = "Work Scheduled between {0} and {1}".format(
                        sched_start, sched_end)

                target_note = None
                if self._wo_target_dates_to_crm \
                        and wo["Scheduling"]["TargetStart"] \
                        and wo["Scheduling"]["TargetFinish"] \
                        and wo["Status"] not in ["PREP", "WAPPR"]:
                    target_start = None
                    target_end = None
                    if wo["Scheduling"]["TargetStart"]:
                        target_start = dateutil.parser.parse(
                            wo["Scheduling"]["TargetStart"]
                        ).strftime("%d-%m-%Y %H:%M")
                    if wo["Scheduling"]["TargetFinish"]:
                        target_end = dateutil.parser.parse(
                            wo["Scheduling"]["TargetFinish"]
                        ).strftime("%d-%m-%Y %H:%M")
                    if target_start and target_end and \
                            target_start.find(" 00:00") > 0 \
                            and target_end.find(" 00:00") > 0:
                        # remove meaningless 00:00 (midnight default for start
                        # & finish times - clearly user is not setting times)
                        # This way the CRM note looks nicer.
                        target_start = target_start[0:target_start.find(" 00:00")]
                        target_end = target_end[0:target_end.find(" 00:00")]
                    if target_start and target_end:
                        target_note = "Work Target Dates between {0} and {1}" \
                            .format(target_start, target_end)

                # if there is either status or history then get CRM
                # so we can get current note and make sure not doubling up
                # and then add note to CRM
                if wo["Id"] in wos_new_status or len(new_comments) > 0 \
                        or date_note or target_note:
                    # find the crm from the list of active crms or get the CRM
                    crm = None
                    if wr["ID"] in active_crm_wr_guid_list:
                        # get the crm object from the active list built earlier
                        for crm_chk in crms:
                            if crm_chk.assetic_wr_representation.id == \
                                    wr["ID"]:
                                crm = crm_chk
                                break
                    else:
                        # get the crm from the crm using wr guid
                        # format the wr dict to match the standard structure
                        wr_dict = {"Id": wr["ID"],
                                   "FriendlyIdStr": wr["FriendlyID"]}
                        try:
                            crm = self.crm_tools.get_crm_request_for_wr(
                                wr["ID"], wr_dict)
                        except TypeError:
                            # originally this method only passed in the id.
                            # If TypeError implies an older plugin with 1 param
                            crm = self.crm_tools.get_crm_request_for_wr(
                                wr["ID"])
                        if isinstance(crm, int):
                            # there was an error, should be of type pyodbc.Row
                            return crm
                    if crm:
                        # get current comments in crm
                        current_note = self.crm_tools.get_task_note_from_crm(
                            crm.crm_representation)
                        if isinstance(current_note, int):
                            # there was an error getting note
                            return current_note
                    else:
                        # couldn't find crm.
                        msg = "Couldn't find a {0} CRM task for " \
                              "Assetic Request {1}".format(self._crm_name
                                                           , wr["FriendlyID"])
                        self.logger.warning(msg)
                        # can't add note so break to next work request
                        break

                    wo_obj = self.api_client.deserialize(
                        wo, "MaintenanceWorkOrder")
                    if wo["Status"] in comment_status and \
                            comment_status[wo["Status"]] not in current_note:
                        new_note_list.append(
                            WrNote(note=comment_status[wo["Status"]]
                                   , context="Status"
                                   , note_date=self._get_datetime_from_string(
                                    wo["LastModified"])
                                   , assetic_fid=wo["FriendlyIdStr"]
                                   , assetic_uid=wo["Id"]
                                   , wr_obj=wr, wo_obj=wo_obj))
                    for comment in new_comments:
                        if comment["Description"] not in current_note:
                            new_note_list.append(
                                WrNote(note=comment["Description"]
                                       , context="Supporting Info"
                                       , note_date=
                                       self._get_datetime_from_string(
                                           comment["CreatedDateTime"])
                                       , assetic_fid=wo["FriendlyIdStr"]
                                       , display_name=
                                       comment["CreatedByDisplayName"]
                                       , assetic_uid=comment["Id"]
                                       , wr_obj=wr, wo_obj=wo_obj))
                    if date_note and date_note not in current_note:
                        new_note_list.append(
                            WrNote(note=date_note
                                   , context="Work Schedule"
                                   , note_date=self._get_datetime_from_string(
                                    wo["LastModified"])
                                   , assetic_fid=wo["FriendlyIdStr"]
                                   , assetic_uid=wo["Id"]
                                   , wr_obj=wr, wo_obj=wo_obj))
                    if target_note and target_note not in current_note:
                        new_note_list.append(
                            WrNote(note=target_note
                                   , context="Work Target"
                                   , note_date=self._get_datetime_from_string(
                                    wo["LastModified"])
                                   , assetic_fid=wo["FriendlyIdStr"]
                                   , assetic_uid=wo["Id"]
                                   , wr_obj=wr, wo_obj=wo_obj))

                    if len(new_note_list) > 0:
                        self.crm_tools.add_task_note_to_crm(new_note_list, crm)

        self.set_last_integration_datetime_via_doc_link("workorder", max_date)
        return 0

    def get_request(self, wrguid):
        """
        Get the work request object for a given work request guid
        :param wrguid: work request guid
        :return: assetic.WorkRequest
        """
        try:
            wrget = self.wrapi.work_request_get(wrguid)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        return wrget

    def get_supporting_info(self, wrguid):
        """
        Get the work request object for a given work request guid
        :param wrguid: work request guid
        :return: list of supporting information objects
        """
        try:
            wr_info = self. \
                wrapi.work_request_get_supporting_information_for_work_request(
                wrguid)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            raise
        return wr_info["ResourceList"]

    def get_changed_wr_since_date_odata(self, min_date):
        """
        Get a list of Assetic requests that have status date greater than
        or equal to supplied date.  Filter not down to milliseconds so need to
        consider a change within the mindate second
        Uses OData as there is no filtered get for requests, also statusdate
        is only available in OData search and not the API
        :param min_date: the date to filter by
        :returns: list of request id's and status as JSON from OData endpoint
        """
        # search require datetime with offset. Might be a bit awkward for the
        # couple of hours around daylight savings changeover
        # date_filter = self._get_utc_string_with_offset(min_date)
        date_filter = self._get_date_string_for_search(min_date)
        if date_filter is None:
            return 1
        fields = "WorkRequestId,WRStatus,WRStatusDateTime,WRLastModified" \
                 ",WorkRequestFID,WRCreatedDateTime,WRExternalId,WOWorkOrderId"
        top = 10000
        skip = 0
        qfilter = "WRLastModified ge {0} and WRExternalId ne null".format(
            date_filter)
        orderby = "WRLastModified desc"
        try:
            wrs = self.odata.get_odata_data("workrequest", fields, qfilter,
                                            top, skip, orderby)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        if not wrs:
            # no records found, but no error. Return empty list
            wrs = list()
        return wrs

    def get_changed_wr_since_date(self, min_date):
        # type: (datetime.datetime) -> []
        """
        Get a list of Assetic requests that have:
            1.  status date greater than or equal to supplied date
            2.  creator ID that matches integration user

        Filter not down to milliseconds so need to consider a change
        within the mindate second

        :param min_date: the date to filter by
        :returns: list of work request objects as json
        """

        if not isinstance(min_date, datetime.datetime):
            self.logger.error("Must provide a datetime object for date search")
            return 1

        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500,
            'request_params_sorts': "LastModified-desc",
            'request_params_filters': (
                "LastModified~gt~'{0}'"
                "~and~ExternalIdentifier~neq~''"
                "~and~CreatedBy~eq~'{1}'".format(
                    min_date.strftime("%Y-%m-%dT%H:%M:%S"), self._integration_user_guid)
            )
        }

        try:
            wr = self.wrapi.work_request_get_0(**kwargs)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status

        wr_list = wr['ResourceList']

        # loop through remaining pages
        for page in range(2, int(wr["TotalPages"]) + 1):
            kwargs["request_params_page"] = page
            # now execute the request
            try:
                response = self.wrapi.work_request_get_0(**kwargs)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return e.status
            wr_list = wr_list + response["ResourceList"]
        return wr_list

    def get_wr_list_via_api(self, wr_guids):
        """
        For a given list of work request guids use the API to get
        the wr details.
        :param wr_guids: A list of work request guids
        :return: a list of wr objects, sorted in descending last modified
        date, else error code
        """
        wrs = list()
        for wr_guid in wr_guids:
            try:
                wrget = self.wrapi.work_request_get(wr_guid)
            except ApiException as e:
                if e.status == 404:
                    # wr_guid not found
                    self.logger.warning(
                        "No Assetic work request found for GUID {0}".format(
                            wr_guid))
                else:
                    # consider it a fatal error and exit
                    self.logger.error(
                        "Status {0}, Reason: {1} {2}".format(
                            e.status, e.reason, e.body))
                    return e.status
            else:
                # now copy date into a field for sorting
                wrget["UseToSort"] = self._get_datetime_from_string(
                    wrget["LastModified"])
                # append to list
                wrs.append(wrget)
        return sorted(wrs, key=itemgetter('UseToSort'), reverse=True)

    def get_wr_guid_for_crm_id(self, crm_id):
        """
        Get Assetic work request for given crm_id.
        Filter on ExternalIdentifier
        :param crm_id: the CRM id to filter by
        :returns: a single request id or None
        """
        kwargs = {'request_params_page': 1,
                  'request_params_page_size': 1,
                  'request_params_filters':
                      "ExternalIdentifier~eq~'{0}'".format(crm_id)
                  }
        try:
            wr = self.wrapi.work_request_get_0(**kwargs)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status

        if len(wr["ResourceList"]) > 0:
            return wr["ResourceList"][0]["Id"]
        else:
            return None

    def get_changed_wo(self, min_date):
        """
        Get a list of Assetic work orders that have last mod date greater than
        supplied date
        :param min_date: the min date to filter by
        :returns: list of work orders
        """
        if not isinstance(min_date, datetime.datetime):
            self.logger.error("Must provide a datetime object for date search")
            return 1

        kwargs = {'request_params_page': 1,
                  'request_params_page_size': 500,
                  'request_params_sorts': "LastModified-desc",
                  'request_params_filters':
                      "LastModified~gt~'{0}'".format(
                          min_date.strftime("%Y-%m-%dT%H:%M:%S"))
                  }
        try:
            wko = self.wkoapi.work_order_integration_api_get(**kwargs)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status

        wko_list = wko.get('ResourceList')
        for i in range(0, len(wko_list)):
            # if the work order is a child of a work order that is linked to a
            # work request, then add the work requests to the child
            if wko_list[i]["ReferenceWorkOrderId"] and \
                    len(wko_list[i]["LinkedWorkRequests"]) == 0:
                # this work order has no wr's, but has a parent, so try parent
                wko_list[i]["LinkedWorkRequests"] = self.get_wr_for_child_wo(
                    wko_list[i]["ReferenceWorkOrderId"])
        return wko_list

    def get_wr_for_child_wo(self, wo_guid):
        """
        A work order may be a child of a work order that is linked to a work
        request
        :param wo_guid: the wo guid to get the wr's for
        :returns: list of LinkedWorkRequests object or None if no ext ref
        """
        ext_id = None
        for i in range(0, 5):
            # try max 5 levels of parent then give up. Will exit earlier if
            # it runs out of parents
            try:
                wko = self.wkoapi.work_order_integration_api_get_0(wo_guid)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return e.status
            if len(wko["LinkedWorkRequests"]) > 0 \
                    or not wko["ReferenceWorkOrderId"]:
                # now have linked wr's or have reach the end of the line
                return wko["LinkedWorkRequests"]

            # this work order has no linked wr, but has a parent, so try parent
            # on next iteration of loop
            wo_guid = wko["ReferenceWorkOrderId"]
        return ext_id

    def get_wkos_cascade_for_wkos(self, wo_guids):
        """
        Get a list of Assetic work orders and their child work orders.
        The child work order will have the work request guid set based on the
        parent
        :param wo_guids: a list of work order guids.  These work orders are
        expected to be linked to a work request
        :returns: list of work orders
        """
        wko_list = list()
        for wo_guid in wo_guids:
            try:
                wko = self.wkoapi.work_order_integration_api_get_0(wo_guid)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return e.status
            wko_list.append(wko)

        for i in range(0, len(wko_list)):
            # if the work order is a child of a work order that is linked to a
            # work request, then add the work requests to the child
            if wko_list[i]["ReferenceWorkOrderId"] and \
                    len(wko_list[i]["LinkedWorkRequests"]) == 0:
                # this work order has no wr's, but has a parent, so try parent
                wko_list[i]["LinkedWorkRequests"] = self.get_wr_for_child_wo(
                    wko_list[i]["Id"])
        return wko_list

    def get_wko_actual_finish_date(self, wo_guid):
        """
        Get a list of Assetic work orders and their child work orders.
        The child work order will have the work request guid set based on the
        parent
        :param wo_guid: the work order to get the actual finish date for
        :returns: actual finish date or none
        """

        try:
            wko = self.wkoapi.work_order_integration_api_get_0(wo_guid)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status

        if wko["Scheduling"]["ActualFinish"]:
            finish_date_str = wko["Scheduling"]["ActualFinish"]
            # convert the string to a date object
            finish_date = self._get_datetime_from_string(finish_date_str)
            if not finish_date:
                msg = "Unable to correctly read work order finish " \
                      "datetime {0}.".format(finish_date_str)
                self.logger.warning(msg)
                finish_date = None
        else:
            if wko["FriendlyIdStr"]:
                wo_id = wko["FriendlyIdStr"]
            else:
                wo_id = wo_guid
            msg = "Work Order finish datetime not set for {0}.".format(wo_id)
            self.logger.warning(msg)
            return None
        return finish_date

    def get_wos_with_new_status(self, min_date):
        """
        Get a list of Assetic work orders that have status date greater than
        supplied date, or null status date where last_modified greater than
        supplied date
        Uses OData as status date is only available in OData search
        and not the API
        :param min_date: the date to filter by
        :returns: list of work order ids or error number (non zero)
        """

        fields = "Id,WOStatusDateTime"
        fields_no_status = "Id,WOLastModified"
        top = 10000
        skip = 0
        # search require datetime with offset. Might be a bit awkward for the
        # couple of hours around daylight savings changeover
        # date_filter = self._get_utc_string_with_offset(min_date)
        date_filter = self._get_date_string_for_search(min_date)
        if date_filter is None:
            return 1
        qfilter = "WOStatusDateTime ge {0}".format(date_filter)
        orderby = "WOStatusDateTime desc"
        qfilter_no_status = "WOLastModified ge {0}".format(date_filter)
        orderby_no_status = "WOLastModified desc"
        try:
            wos = self.odata.get_odata_data("workorder", fields, qfilter,
                                            top, skip, orderby)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        # now get wos with no status date - could be new wko
        try:
            wos_no_status = self.odata.get_odata_data("workorder"
                                                      , fields_no_status
                                                      , qfilter_no_status
                                                      , top, skip
                                                      , orderby_no_status)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        # check if any OData GET had an error and returned 'None', if so return with error
        if isinstance(wos, type(None)) or isinstance(wos_no_status, type(None)):
            self.logger.error("Error retrieving updated Work Orders via OData.")
            return 1

        # The search currently works at the 'day' level, so time is ignored
        # will remove times earlier than requested time
        # and convert the json into a list with just wo ID
        wo_status = [x["Id"] for x in wos
                     if self._get_datetime_from_string(
                x["WOStatusDateTime"]) >= min_date]
        wo_no_status = [x["Id"] for x in wos_no_status
                        if self._get_datetime_from_string(
                x["WOLastModified"]) >= min_date]
        return wo_status + wo_no_status

    def set_last_integration_datetime(self, module, lastdate):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Write date in a text file in %APPDATA%/Assetic
        :param module: 'workorder' or "workrequest"
        :param lastdate: the datetime to record
        :return 0=success, else error
        """
        appdata = os.environ.get("APPDATA")
        if module == "workorder":
            file = os.path.join(appdata, "Assetic", "crm_wo_last_process_date.txt")
        else:
            file = os.path.join(appdata, "Assetic", "crm_wr_last_process_date.txt")
        try:
            with open(file, "w+") as f:
                f.write(lastdate.isoformat())
        except Exception as e:
            msg = "Unable to write datetime file {0} with error: {1}".format(
                file, str(e))
            self.logger.error(msg)
            return 1
        else:
            return 0

    def set_last_integration_datetime_via_doc_link(self, module, lastdate):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Write date in a text file in %APPDATA%/Assetic
        :param module: 'workorder' or "workrequest"
        :param lastdate: the datetime to record
        :return 0=success, else error
        """
        doc_id = None
        if module == "workorder":
            label = "crm_wo_last_process_date for crm integration"
            doc_id = self._wo_last_date_doc_id
        elif module == "workrequest":
            label = "crm_wr_last_process_date for crm integration"
            doc_id = self._wr_last_date_doc_id
        else:
            self.logger.warning("Unsupported module {0} for setting "
                                "integration date. Date cannot be recorded")
            return 1

        # Document categorisation - initialise document properties object
        # and populate
        document = DocumentRepresentation()
        docurl = "{0}/Maintenance/Operational/" \
                 "".format(self.api_client.configuration.host)
        document.document_group = 10  # Hard code as 'document'
        # document.document_category = doc_category
        # document.document_sub_category = doc_subcategory
        document.document_link = docurl
        document.external_id = lastdate.isoformat()
        document.label = label
        document.id = doc_id

        if not doc_id:
            # Perform upload of new doc
            try:
                doc = self.docapi.document_post(document)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return 1
        else:
            # Perform update of existing doc
            try:
                doc = self.docapi.document_put(document.id, document)
            except ApiException as e:
                self.logger.error("Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
                return 1
        return 0

    def get_last_integration_datetime(self, module, seed_date_if_null=None):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Read date from a text file in %APPDATA%/Assetic. If not found then
        use seed date if provided, else current date less 1 week.
        :param module: workorder or workrequest
        :param seed_date_if_null: optional datetime to seed the process if no
        date file is found
        :return: date
        """
        appdata = os.environ.get("APPDATA")
        if module == "workorder":
            file = os.path.join(appdata, "Assetic", "crm_wo_last_process_date.txt")
        else:
            file = os.path.join(appdata, "Assetic", "crm_wr_last_process_date.txt")
        if seed_date_if_null is not None and \
                isinstance(seed_date_if_null, datetime.datetime) == False:
            self.logger.warning("Seed date is not a datetime, will use default")
            seed_date_if_null = None
        if seed_date_if_null is None:
            seed_date_if_null = datetime.datetime.now() - datetime.timedelta(
                days=7)
        return_date = seed_date_if_null
        if os.path.isfile(file):
            try:
                with open(file) as f:
                    read_data = f.read()
            except Exception as e:
                msg = "Unable to read datetime file {0} with error: {1}\n" \
                      "Will use date {2} instead".format(
                    file, str(e), str(return_date))
                self.logger.warning(msg)
                return return_date
            try:
                return_date = dateutil.parser.parse(read_data)
            except Exception as e:
                msg = "Unable to correctly read datetime from file {0}, " \
                      "value is {1}.  Using default of {2} instead" \
                      "\nError is: {3}".format(
                    file, read_data, str(seed_date_if_null), str(e))
                self.logger.warning(msg)
                return_date = seed_date_if_null
        return return_date

    def get_last_integration_datetime_from_doc_link(self, module,
                                                    seed_date_if_null=None):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Read date from a document link record in Assetic. If not found then
        use seed date if provided, else current date less 1 week.
        :param module: workorder or workrequest
        :param seed_date_if_null: optional datetime to seed the process if no
        date file is found
        :return: date
        """
        if seed_date_if_null is not None and \
                isinstance(seed_date_if_null, datetime.datetime) == False:
            self.logger.warning("Seed date is not a datetime, will use default")
            seed_date_if_null = None
        if seed_date_if_null is None:
            seed_date_if_null = datetime.datetime.now() - datetime.timedelta(
                days=7)
        return_date = seed_date_if_null
        # set search criteria
        if module == "workorder":
            label = "crm_wo_last_process_date for crm integration"
        elif module == "workrequest":
            label = "crm_wr_last_process_date for crm integration"
        else:
            self.logger.warning("Unsupported module {0} for getting "
                                "integration date. Will use default")
            return return_date

        search_filter = "label~eq~'{0}'".format(label)
        kw = {"request_params_page": 1,
              "request_params_page_size": 1,
              "request_params_filters": search_filter}

        # Perform get
        try:
            docs = self.docapi.document_get(**kw)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return return_date
        if len(docs["ResourceList"]) > 0 and \
                docs["ResourceList"][0]["ExternalId"] != "":
            if module == "workorder":
                self._wo_last_date_doc_id = docs["ResourceList"][0]["Id"]
            elif module == "workrequest":
                self._wr_last_date_doc_id = docs["ResourceList"][0]["Id"]
            return_date = docs["ResourceList"][0]["ExternalId"]
            # convert the string to a date object
            try:
                return_date = dateutil.parser.parse(return_date)
            except Exception as e:
                msg = "Unable to correctly read datetime {0}.  " \
                      "Using default of {1} instead" \
                      "\nError is: {2}".format(return_date,
                                               str(seed_date_if_null), str(e))
                self.logger.warning(msg)
                return_date = seed_date_if_null

        return return_date

    def _get_integration_user_guid(self):
        """
        Get the Assetic guid for the integration user
        :return: Assetic guid for the integration user
        """
        try:
            user_info = self.auth_api.auth_get()
        except ApiException as e:
            self.logger.error("Error getting the auth details of the "
                              "integration user\nStatus {0}, Reason: {1} {2}"
                              "".format(e.status, e.reason, e.body))
            return e.status
        return user_info["Id"]

    # def _get_datetime_from_utc_string(self, utc_string):
    #     """
    #     Convert UTC string to local datetime
    #     Assumes server time is local time
    #     :param utc_string: the string to convert to local datetime
    #     :returns: datetime, or None if error
    #     """
    #     if utc_string is None:
    #         return None
    #     if "+" in utc_string:
    #         tz_offset_hr = int(utc_string.split("+")[1].split(":")[0])
    #         tz_offset_min = int(utc_string.split("+")[1].split(":")[1])
    #         try:
    #             dt = dateutil.parser.parse(utc_string.split("+")[0])
    #             dt = dt + datetime.timedelta(hours=tz_offset_hr,
    #                                          minutes=tz_offset_min)
    #         except Exception as e:
    #             self.logger.error(
    #                 "Error converting datetime {0}".format(str(e)))
    #             return None
    #     else:
    #         try:
    #             dt = dateutil.parser.parse(utc_string)
    #         except Exception as e:
    #             self.logger.error(
    #                 "Error converting datetime {0}".format(str(e)))
    #             return None
    #     return dt

    def _get_datetime_from_string(self, datetime_string):
        """
        Convert string to datetime without timezone
        :param datetime_string: the string to convert to datetime
        :returns: datetime, or None if error
        """
        if datetime_string is None:
            return None
        if "+" in datetime_string:
            try:
                dt = dateutil.parser.parse(datetime_string.split("+")[0])
            except Exception as e:
                self.logger.error("Error converting datetime {0}".format(
                    str(e)))
                return None
        else:
            try:
                dt = dateutil.parser.parse(datetime_string)
            except Exception as e:
                self.logger.error(
                    "Error converting datetime {0}".format(str(e)))
                return None
        return dt

    # def _get_utc_string_with_offset(self, dt):
    #     """
    #     Convert local datetime to str for use by odata search
    #     Assumes server time is local time
    #     :param dt: the datetime to convert
    #     :returns: datetime string including ofset from UTC, or None if error
    #     """
    #     if not isinstance(dt, datetime.datetime):
    #         self.logger.error("Must provide a datetime object for date conversion to UTC string")
    #         return 1
    #     # Get local time offset.  If daylight savings then will get alt
    #     tz_offset = time.timezone
    #     if time.localtime().tm_isdst != 0:
    #         tz_offset = time.altzone
    #
    #     # Get UTC by applying offset
    #     dt = dt + datetime.timedelta(seconds=tz_offset)
    #
    #     # Now build offset string
    #     offset = str(tz_offset / 60 / 60 * -1).split(".")
    #     if len(offset) > 1 and offset[1] != '0':
    #         # offset includes minutes
    #         offset[1] = str(int(offset[1]) * 6)
    #     else:
    #         offset[1] = "00"
    #
    #     return dt.strftime("%Y-%m-%dT%H:%M:%S+{0}:{1}".format(
    #         offset[0], offset[1]))

    def _get_date_string_for_search(self, dt):
        """
        Convert local datetime to str for use by odata search
        Assumes server time is local time
        :param dt: the datetime to convert
        :returns: local datetime string including offset, or None if error
        """
        if not isinstance(dt, datetime.datetime):
            self.logger.error("Must provide a datetime object for date "
                              "formatting to string")
            return 1
        # Get local time offset.  If daylight savings then will get alt
        tz_offset = time.timezone
        if time.localtime().tm_isdst != 0:
            tz_offset = time.altzone

        # Now build offset string
        offset = str(tz_offset / 60 / 60 * -1).split(".")
        if len(offset) > 1 and offset[1] != '0':
            # offset includes minutes
            offset[1] = str(int(offset[1]) * 6)
        else:
            if len(offset) == 1:
                # cater for python 2
                offset.append("00")
            offset[1] = "00"
        # ensure hours and seconds are each of length 2, pad with 0
        if not len(offset[0]) == 2:
            if len(offset[0]) == 1:
                offset[0] = "0{0}".format(offset[0])
            else:
                offset[0] = "00"
        if not len(offset[1]) == 2:
            if len(offset[1]) == 1:
                offset[1] = "0{0}".format(offset[1])
            else:
                offset[1] = "00"
        return dt.strftime("%Y-%m-%dT%H:%M:%S+{0}:{1}".format(
            offset[0], offset[1]))


class CRMPluginBase(object):
    """
    Base class for common CRM integration activities
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_crm_requests(self, integrated=False):
        """
        Get a list of CRMs that satisfy the criteria for an Assetic Work Request
        :param integrated: boolean. If true then only get those with an assetic
        guid that are still active, else only get those without an assetic guid
        :returns a list of wr_crm_dto objects
        """
        return []

    @abc.abstractmethod
    def get_crm_request_for_wr(self, wr_guid=None, wr=None):
        """
        Get the CRM for a given Assetic Work Request GUID
        :param wr_guid: The Assetic Work Request GUID
        :param wr: WorkRequest JSON representation
        :returns a wr_crm_dto object or None
        """
        return WrCrmRepresentation

    @abc.abstractmethod
    def handle_create_error(self, wr_crm_obj):
        """
        CRMs that does not satisfy the criteria for an Assetic Work Request is handled by Clients
        :param wr_crm_obj: Work Request / CRM object.
        :returns False = not handled, else handled by Clients
        """
        return False

    @abc.abstractmethod
    def update_crm_for_new_wr(self, wr_crm_obj, comment):
        """
        For the given Assetic work request update the crm
        :param wr_crm_obj: Work Request / CRM object
        :param comment: the comment to apply to the task
        :return: 0 = success, else error
        """
        return 0

    @abc.abstractmethod
    def add_task_note_to_crm(self, note_list, crm_obj):
        """
        Add a comment to the CRM 'task' using crm_id as the reference
        The task is the Assetic specific action (step) in the request document
        workflow.
        :param note_list: a list of crmtools.WrNote objects
        :param crm_obj: the work request/CRM object
        :returns: 0 unless error
        """
        return 0

    @abc.abstractmethod
    def get_task_note_from_crm(self, crm):
        """
        Get the comments from the CRM
        :param crm: The crm crm_representation object
        """
        return ""

    @abc.abstractmethod
    def add_file_note_to_crm(self, note_list, crm_id):
        """
        Add a comment to the CRM top level using crm_id as the reference
        :param note_list: a list of crmtools.WrNote objects
        """
        return 0

    @abc.abstractmethod
    def get_file_note_from_crm(self, crm_id):
        """
        Get the comments from the CRM top level using crm_id as the reference
        """
        return ""

    @abc.abstractmethod
    def update_crm_task_status(self, crm_obj, code, statusdate):
        """
        For the given CRM task identifier update task status
        using code and datetime (e.g. reject, close)
        :param crm_obj: The crm object
        :param code: determination code
        :param statusdate: the date the status change applies to
        :returns: 0 if success, else error
        """
        return 0

    @abc.abstractmethod
    def update_crm_master_status(self, crm_obj, code, statusdate):
        """
        For the given crm update request status (e.g. close, reject etc)
        using code and datetime.
        :param crm_obj: the crm object
        :param code: the close code
        :param statusdate: the datetime that the request is to be closed
        :returns: 0 if success, else error
        """
        return 0

    # @abc.abstractmethod
    # def get_resolution_code_for_subtask(self, wr_subtype, crm_obj):
    #     """
    #     Get the resolution codes for task and CRM based on the work request
    #     subtype and CRM Object
    #     remedy code/maintenance type?
    #     :param wr_subtype: the Assetic work request subtype entered by user
    #     :param crm_obj: the crm object
    #     :return resolution code object
    #     """
    #     return CrmAsseticResolutionCodes()

    @abc.abstractmethod
    def get_resolution_code_for_status(self, wr_status, crm_obj):
        """
        Get the resolution codes for task and CRM based on the work request
        subtype and CRM Object
        remedy code/maintenance type?
        :param wr_status: the Assetic work request status
        :param crm_obj: the crm object
        :return resolution code object
        """
        return CrmAsseticStatusResolutionCodes()

    @abc.abstractmethod
    def finalise(self):
        """
        Allow the crm plugin to close connections or other finalisation tasks
        :returns: 0 if success, else error
        """
        return 0

    @abc.abstractmethod
    def clear_cancelled_wr_from_crm(self, wr_crm_obj):
        """
        Allow the crm plugin to clear the field used to record the Assetic WR
        GUID. This is for cancelled WR's that may need to be recreated in
        Assetic under a different categorisation against a new CRM task
        :param wr_crm_obj: Work Request / CRM object
        :returns: 0 if success, else error
        """
        return 0


class WrCrmRepresentation(object):
    """
    A structure for document information to be passed between assetic
    and external enterprise content management system (ECMS)
    """

    def __init__(self, assetic_wr_representation=None, crm_representation=None
                 , crm_id=None):
        """"
        Initialise
        :param assetic_wr_representation: DocumentRepresentation
        :param crm_representation: a object unique to the particular crm
        :param: crm_id: unique reference id of the crm
        """
        self.fieldtypes = {
            "assetic_wr_representation":
                "DocumentRepresentation",
            "crm_representation": "str",
            "crm_id": "str"
        }

        self._assetic_wr_representation = assetic_wr_representation
        self._crm_representation = crm_representation
        self._crm_id = crm_id

        api_client = ApiClient()
        self.logger = api_client.configuration.packagelogger

    @property
    def assetic_wr_representation(self):
        return self._assetic_wr_representation

    @assetic_wr_representation.setter
    def assetic_wr_representation(self, assetic_wr_representation):
        ##check the type is correct
        if not isinstance(assetic_wr_representation,
                          WorkRequest):
            msg = "assetic_wr_representation is not the required type: '{0}'" \
                  "".format(
                "WorkRequest")
            self.logger.error(msg)
            self._assetic_wr_representation = None
        else:
            self._assetic_wr_representation = assetic_wr_representation

    @property
    def crm_representation(self):
        return self._crm_representation

    @crm_representation.setter
    def crm_representation(self, crm_representation):
        self._crm_representation = crm_representation

    @property
    def crm_id(self):
        return self._crm_id

    @crm_id.setter
    def crm_id(self, crm_id):
        self._crm_id = crm_id

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


class CrmAsseticStatusResolutionCodes(object):
    types = {
        "wr_status": "int",
        "crm_resolution_code": "str",
        "close_crm": "bool"
    }

    def __init__(self, wr_status=None, crm_resolution_code=None, close_crm=None):
        self._wr_status = None
        self._crm_resolution_code = None
        self._close_crm = None

        if wr_status is not None:
            self._wr_status = wr_status
        if crm_resolution_code is not None:
            self._crm_resolution_code = crm_resolution_code
        if close_crm is not None:
            self._close_crm = close_crm

    @property
    def wr_status(self):
        return self._wr_status

    @wr_status.setter
    def wr_status(self, wr_status):
        self._wr_status = wr_status

    @property
    def crm_resolution_code(self):
        return self._crm_resolution_code

    @crm_resolution_code.setter
    def crm_resolution_code(self, crm_resolution_code):
        self._crm_resolution_code = crm_resolution_code

    @property
    def close_crm(self):
        return self._close_crm

    @close_crm.setter
    def close_crm(self, close_crm):
        self._close_crm = close_crm

    def to_dict(self):
        "Returns the model properties as a dict"
        result = {}

        for attr, _ in six.iteritems(self.types):
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
        "Returns the string representation of the model"
        return pformat(self.to_dict())

    def __repr__(self):
        "For `print` and `pprint`"
        return self.to_str()

    def __eq__(self, other):
        "Returns true if both objects are equal"
        if not isinstance(other, CrmAsseticStatusResolutionCodes):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        "Returns true if both objects are not equal"
        return not self == other


class WrNote(object):
    """
    A class to record a comment/note to return to CRM
    includes context so CRM adaptor can choose how to format
    """
    types = {
        "note": "str",
        "note2": "str",
        "context": "str",
        "note_date": "str",
        "assetic_fid": "str",
        "assetic_uid": "str",
        "display_name": "str"
    }

    def __init__(self, note=None, note2=None, context=None, note_date=None
                 , assetic_fid=None, assetic_uid=None, display_name=None
                 , wr_obj=None, wo_obj=None):
        self._note = None
        self._note2 = None
        self._context = None
        self._note_date = None
        self._assetic_fid = None
        self._assetic_uid = None
        self._display_name = None
        self._wr_obj = None
        self._wo_obj = None

        if note is not None:
            self._note = note
        if note2 is not None:
            self._note2 = note2
        if context is not None:
            self._context = context
        if note_date is not None:
            self._note_date = note_date
        if assetic_fid is not None:
            self._assetic_fid = assetic_fid
        if assetic_uid is not None:
            self._assetic_uid = assetic_uid
        if display_name is not None:
            self._display_name = display_name
        if wr_obj is not None:
            self._wr_obj = wr_obj
        if wo_obj is not None:
            self._wo_obj = wo_obj

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, value):
        self._note = value

    @property
    def note2(self):
        return self._note2

    @note2.setter
    def note2(self, value):
        self._note2 = value

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def note_date(self):
        return self._note_date

    @note_date.setter
    def note_date(self, value):
        self._note_date = value

    @property
    def assetic_fid(self):
        return self._assetic_fid

    @assetic_fid.setter
    def assetic_fid(self, value):
        self._assetic_fid = value

    @property
    def assetic_uid(self):
        return self._assetic_uid

    @assetic_uid.setter
    def assetic_uid(self, value):
        self._assetic_uid = value

    @property
    def display_name(self):
        return self._display_name

    @display_name.setter
    def display_name(self, value):
        self._display_name = value

    @property
    def wr_obj(self):
        return self._wr_obj

    @wr_obj.setter
    def wr_obj(self, value):
        self._wr_obj = value

    @property
    def wo_obj(self):
        return self._wo_obj

    @wo_obj.setter
    def wo_obj(self, value):
        self._wo_obj = value

    def to_dict(self):
        "Returns the model properties as a dict"
        result = {}

        for attr, _ in six.iteritems(self.types):
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
        "Returns the string representation of the model"
        return pformat(self.to_dict())

    def __repr__(self):
        "For `print` and `pprint`"
        return self.to_str()

    def __eq__(self, other):
        "Returns true if both objects are equal"
        if not isinstance(other, CrmAsseticStatusResolutionCodes):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        "Returns true if both objects are not equal"
        return not self == other

# class CrmAsseticResolutionCodes(object):
#     types = {
#         "wr_subtype": "str",
#         "wo_remedy_id": "str",
#         "crm_resolution_code": "str",
#         "crm_rejection_code": "str",
#         "crm_cancellation_code": "str",
#         "close_crm": "bool"
#     }
#
#     def __init__(self, wr_subtype=None, wo_remedy_id=None
#                  , crm_resolution_code=None, crm_rejection_code=None
#                  , crm_cancellation_code=None, close_crm=None):
#         self._wr_subtype = None
#         self._wo_remedy_id = None
#         self._crm_resolution_code = None
#         self._crm_rejection_code = None
#         self._crm_cancellation_code = None
#         self._close_crm = None
#
#         if wr_subtype is not None:
#             self._wr_subtype = wr_subtype
#         if wo_remedy_id is not None:
#             self._wo_remedy_id = wo_remedy_id
#         if crm_resolution_code is not None:
#             self._crm_resolution_code = crm_resolution_code
#         if crm_rejection_code is not None:
#             self._crm_rejection_code = crm_rejection_code
#         if crm_cancellation_code is not None:
#             self._crm_cancellation_code = crm_cancellation_code
#         if close_crm is not None:
#             self._close_crm = close_crm
#
#     @property
#     def wr_subtype(self):
#         return self._wr_subtype
#
#     @wr_subtype.setter
#     def wr_subtype(self, wr_subtype):
#         self._wr_subtype = wr_subtype
#
#     @property
#     def wo_remedy_id(self):
#         return self._wo_remedy_id
#
#     @wo_remedy_id.setter
#     def wo_remedy_id(self, wo_remedy_id):
#         self._wo_remedy_id = wo_remedy_id
#
#     @property
#     def crm_resolution_code(self):
#         return self._crm_resolution_code
#
#     @crm_resolution_code.setter
#     def crm_resolution_code(self, crm_resolution_code):
#         self._crm_resolution_code = crm_resolution_code
#
#     @property
#     def crm_rejection_code(self):
#         return self._crm_rejection_code
#
#     @crm_rejection_code.setter
#     def crm_rejection_code(self, crm_rejection_code):
#         self._crm_rejection_code = crm_rejection_code
#
#     @property
#     def crm_cancellation_code(self):
#         return self._crm_cancellation_code
#
#     @crm_cancellation_code.setter
#     def crm_cancellation_code(self, crm_cancellation_code):
#         self._crm_cancellation_code = crm_cancellation_code
#
#     @property
#     def close_crm(self):
#         return self._close_crm
#
#     @close_crm.setter
#     def close_crm(self, close_crm):
#         self._close_crm = close_crm
#
#     def to_dict(self):
#         "Returns the model properties as a dict"
#         result = {}
#
#         for attr, _ in six.iteritems(self.types):
#             value = getattr(self, attr)
#             if isinstance(value, list):
#                 result[attr] = list(map(
#                     lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
#                     value
#                 ))
#             elif hasattr(value, "to_dict"):
#                 result[attr] = value.to_dict()
#             elif isinstance(value, dict):
#                 result[attr] = dict(map(
#                     lambda item: (item[0], item[1].to_dict())
#                     if hasattr(item[1], "to_dict") else item,
#                     value.items()
#                 ))
#             else:
#                 result[attr] = value
#
#         return result
#
#     def to_str(self):
#         "Returns the string representation of the model"
#         return pformat(self.to_dict())
#
#     def __repr__(self):
#         "For `print` and `pprint`"
#         return self.to_str()
#
#     def __eq__(self, other):
#         "Returns true if both objects are equal"
#         if not isinstance(other, CrmAsseticResolutionCodes):
#             return False
#
#         return self.__dict__ == other.__dict__
#
#     def __ne__(self, other):
#         "Returns true if both objects are not equal"
#         return not self == other
