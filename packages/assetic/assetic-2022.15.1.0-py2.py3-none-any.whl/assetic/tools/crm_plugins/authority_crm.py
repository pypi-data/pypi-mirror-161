# coding: utf-8
"""
    Create Assetic requests from Authority CRM and Update Authority CRM
"""

import pyodbc  # connect to Informix
import datetime
from contextlib import contextmanager
from pprint import pformat
from six import iteritems
import six
import logging
import copy
from ...rest import ApiException
from ...api import AssetApi
from ..crm_tools import CRMPluginBase
from ..crm_tools import WrCrmRepresentation
from ..maintenance_tools import MaintenanceTools
from ..assets import AssetTools
from ...models.work_request_spatial_location import WorkRequestSpatialLocation
from ...models.work_request import WorkRequest
from ...models.work_request_physical_location import \
    WorkRequestPhysicalLocation
from ...models.custom_address import CustomAddress
from ...models.requestor_representation import RequestorRepresentation
from ...models.requestor_type_representation import RequestorTypeRepresentation
from ..crm_tools import CrmAsseticStatusResolutionCodes


class AuthorityCRM(CRMPluginBase):
    def __init__(self, **kwargs):
        """
        initialise object
        :param **kwargs: requires  3 keywords:
        'db_connection_string' with the connection string defined
        'db_type' one of 'informix' or 'sqlserver'
        'crm_query_filter' sql to filter the list of CRM requests.  Use full
        table name and column name
        """
        logger = logging.getLogger(__name__)
        self.logger = logger
        self._db_crm_select_filter = ""
        if "db_connection_string" in kwargs:
            try:
                self._db_connection = pyodbc.connect(
                    kwargs["db_connection_string"])
            except pyodbc.Error as ex:
                self.logger.error(
                    "Error connecting to database:\r\n{0}".format(
                        ex))
                raise
        else:
            msg = "'db_connection_string' not defined when initiating " \
                  "Authority CRM plugin"
            self.logger.error(msg)
            raise AttributeError(msg)
        if "db_crm_select_filter" in kwargs:
            self._db_crm_select_filter = kwargs["db_crm_select_filter"]

        self._db_type = None
        self._db_timestamp_str = None
        if "db_type" in kwargs:
            if kwargs["db_type"].lower() == "informix":
                self._db_type = "informix"
                self._db_timestamp_str = "current"
            elif kwargs["db_type"].lower() == "sql server":
                self._db_type = "sql server"
                self._db_timestamp_str = "CURRENT_TIMESTAMP"
        if self._db_type is None:
            self._db_type = "informix"
            self.logger.warning("kwargs 'db_type' undefined or unsupported. "
                                "Supported types are 'Informix' or 'SQL Server"
                                "Assuming database is Informix")
        if self._db_type == "informix":
            try:
                self._db_connection.set_attr(pyodbc.SQL_ATTR_TXN_ISOLATION
                                             , pyodbc.SQL_TXN_READ_UNCOMMITTED)
            except pyodbc.Error as ex:
                self.logger.error(
                    "Error setting database isolation level:\r\n{0}".format(ex))
                raise

        self._sql_get_new_crm = None
        if "get_new_crm_query" in kwargs and \
                kwargs["get_new_crm_query"] is not None:
            self._sql_get_new_crm = kwargs["get_new_crm_query"]

        self._username_in_note = False
        if "username_in_note" in kwargs and \
                kwargs["username_in_note"] is not None and \
                isinstance(kwargs["username_in_note"], bool):
            # This is the name of the Assetic user that entered the note
            self._username_in_note = kwargs["username_in_note"]

        self.authority_common = AuthorityCommon(**kwargs)

        self._classification_codes = list()
        self._resolution_codes = list()
        self._wr_crm_code_mappings = list()

        self._doctype = 2
        self._mduref = "DD"
        self._typind = "T"
        self._audmnote_num_typ = "D"
        self._mod_opr = None

        self._resolution_code_representation = \
            AuthorityAsseticStatusResolutionCodes

        self._wr_crm_code_representation = AuthorityAsseticClassificationCodes

        if self._db_type == "informix":
            if not self._sql_get_new_crm:
                self._sql_get_new_crm = """
                select d.fmt_acc, d.wrk_typ
                ,trim(d.dda_cd1) as dda_cd1, trim(d.dda_cd2) as dda_cd2
                ,trim(d.dda_cd3) as dda_cd3
                ,d.doc_num,d.rec_dte,d.cre_dte_tme, d.doc_pre
                ,trim(d.ext_ref) as ext_ref
                ,d.mod_opr
                ,d.cta_mth as lodgement_method
                ,trim(trim(nvl(p.pcl_unt,'')) || trim(nvl(p.unt_alp,'')) || decode(nvl(p.pcl_unt,'NULL'),'NULL','',
                decode(nvl(p.hou_num,'NULL'),'NULL','','/')) || trim(nvl(p.hou_num,'')) || trim(nvl(p.hou_alp,'')) ||
                decode(nvl(p.hou_end,"NULL"),"NULL",'','-') || trim(nvl(p.hou_end,' ')) || trim(nvl(p.end_alp,''))) 
                as prop_st_num            
                ,trim(nvl(p.str_nme,' ')) || ' ' || trim(nvl(p.str_typ,' ')) as prop_st
                ,trim(nvl(p.sbr_nme,' ')) as prop_suburb
                ,task.key_num as task_key_num, task.rea_cde as task_rea_cde
                ,task.det_cde as task_det_cde, task.clo_dte as task_clo_dte
                ,task.due_dte as task_due_dte, task.seq_num as task_seq_num
                ,trim(nvl(cn.nam_gv1,'')) as cust_firstname
                ,trim(nvl(cn.nam_fam,'')) as cust_famname
                ,cn.bus_phn as cust_busphn
                ,cn.hme_ph1 as cust_home_phn
                ,cn.mob_phn as cust_mob_phn
                ,trim(trim(nvl(cn.res_ad1,' ')) || ' ' || trim(nvl(cn.res_ad2,' ')) || ' ' || trim(nvl(cn.res_ad3,' ')) || ' ' || trim(nvl(cn.res_ad4,' ')) || ' ' || trim(nvl(cn.res_ad5,' '))) as cust_addr
                ,gps.gps_lat, gps.gps_lon
                ,trim(nvl(l.des_acc,'')) as node_num
                ,trim(nvl(l.acc_dsc,'')) as node_desc
                ,trim(nvl(nar_ta.nam_gv1,'')) || ' ' || trim(nvl(nar_ta.nam_fam,'')) as actioning_officer
                ,l2.alp_cd3 as contact_method
                from aualdocs d 
                ,outer auallnks l
                ,outer(auallnks l2, aunrmast cn)
                ,outer(auprlink pl, auprstad p)
                ,outer aunrmast nar_ta
                ,aualtask task
                ,outer aualgpsp as gps
                where
                d.fmt_acc = task.mdu_fmt
                and nar_ta.nar_num = task.act_nar
                and d.fmt_acc = gps.mdu_acc and gps.key_num = 
                    (select max(g.key_num) from aualgpsp g where d.fmt_acc = mdu_acc)
                and d.fmt_acc = pl.mdu_fmt
                and pl.pcl_num = p.pcl_num
                and d.fmt_acc = l.src_acc and l.des_mdu = 'AM'
                and d.fmt_acc = l2.src_acc and l2.des_mdu = 'NR'
                and l2.des_num = cn.nar_num
                and d.doc_yer >2017
                and pl.mdu_acc > 0
                and p.seq_num = 0
                """

            # We don't need as much information for the active crms so simpler
            self._sql_get_active_crm = """
            select d.fmt_acc, d.wrk_typ
            ,d.dda_cd1, d.dda_cd2, d.dda_cd3, d.doc_num
            ,d.cre_dte_tme, trim(d.ext_ref) as ext_ref
            , trim(d.ext_rf2) as ext_rf2, d.mod_opr
            ,task.key_num as task_key_num, task.rea_cde as task_rea_cde
            ,task.det_cde as task_det_cde, task.clo_dte as task_clo_dte
            ,task.seq_num as task_seq_num
            from aualdocs d 
            ,aualtask task
            where
            d.fmt_acc = task.mdu_fmt
            """

        elif self._db_type == "sql server":
            if not self._sql_get_new_crm:
                self._sql_get_new_crm = """
                select
                d.fmt_acc  --mandatory
                ,d.wrk_typ   --can assist with filtering out CRMs or setting resolution code
                ,d.dda_cd1   --can assist with filtering out CRMs or setting resolution code
                ,d.dda_cd2   --can assist with filtering out CRMs or setting resolution code
                ,d.doc_num   --mandatory - used when adding task note (aualtnot.doc_num)
                ,d.rec_dte   --can assist with filtering out CRMs 
                ,d.cre_dte_tme --can assist with filtering out CRMs
                ,d.doc_pre --Assetic Work Request 'Brief Description'
                ,RTRIM(d.ext_ref) as ext_ref  -- mandatory this will hold the Assetic Work Request GUID
                ,d.mod_opr  -- currently used when inserting notes - can ommit if using an 'integration mod_opr'
                ,REPLACE(RTRIM(ISNULL(p.pcl_unt,'')) + RTRIM(ISNULL(p.unt_alp,'')) +
                case
                    when p.pcl_unt is not null then
                        case
                            when p.hou_num is not null then p.pcl_unt + '/' + p.hou_num
                            else p.pcl_unt
                        end
                    else p.hou_num
                end
                + RTRIM(ISNULL(p.hou_alp,'')) +
                case
                    when p.hou_end is not null then '-' + p.hou_end
                    else ''
                end
                + RTRIM(ISNULL(p.hou_end,'')) + RTRIM(ISNULL(p.end_alp,'')),' ','')
                as prop_st_num         --street number location of defect (not used but can be - currently location is "Australia" if CRM is not linked to an asset)
                ,p.str_nme as prop_st  -- location of defect (not used but can be - currently location is "Australia" if CRM is not linked to an asset)
                ,p.sbr_nme as prop_suburb --location of defect (not used but can be - currently location is "Australia" if CRM is not linked to an asset)
                ,task.key_num as task_key_num  --mandatory - identifies the task
                ,task.rea_cde as task_rea_cde  --mandatory - use to filter out CRMs
                ,task.det_cde as task_det_cde  --mandatory - determination code
                ,task.clo_dte as task_clo_dte  --mandatory - identifies the task as closed
                ,task.due_dte as task_due_dte  --mandatory - use to set response date in Assetic Work Request
                ,task.seq_num as task_seq_num  --mandatory - used when writing a note to the task
                ,RTRIM(ISNULL(cn.nam_gv1,'')) as cust_firstname --customer contact detail in Assetic Work Request
                ,RTRIM(ISNULL(cn.nam_fam,'')) as cust_famname   --customer contact detail in Assetic Work Request
                ,cn.bus_phn as cust_busphn                      --customer contact detail in Assetic Work Request
                ,cn.hme_ph1 as cust_home_phn                    --customer contact detail in Assetic Work Request
                ,cn.mob_phn as cust_mob_phn                     --customer contact detail in Assetic Work Request
                --create customer contact address string from fields
                ,RTRIM(RTRIM(ISNULL(cn.res_ad1,'')) + ' ' + RTRIM(ISNULL(cn.res_ad2,'')) + ' ' 
                + RTRIM(ISNULL(cn.res_ad3,'')) + ' ' + RTRIM(ISNULL(cn.res_ad4,'')) + ' ' 
                + RTRIM(ISNULL(cn.res_ad5,''))) as cust_addr   --customer contact detail in Assetic Work Request
                ,gps.gps_lat --Null unless 3rd party app is populating via integration. Can be used when creating Assetic Work Request
                ,gps.gps_lon --Null unless 3rd party app is populating via integration. Can be used when creating Assetic Work Request
                ,RTRIM(ISNULL(l.des_acc,'')) as node_num   -- if Authority has an 'asset' linked to the CRM - id (can link to Assetic asset via external reference id)
                ,RTRIM(ISNULL(l.acc_dsc,'')) as node_desc  -- if Authority has an 'asset' linked to the CRM - name
                ,RTRIM(ISNULL(nar_ta.nam_gv1,'')) + ' ' + RTRIM(ISNULL(nar_ta.nam_fam,'')) as actioning_officer --currently not used becuase can't assign in Assetic, but keep for future Assetic capability
                ,l2.alp_cd3 as contact_method --can use to set preferred contact method in Assetic.
                from aualdocs d  --CRM document
                inner join aualtask task on task.mdu_fmt = d.fmt_acc --task in workflow
                left outer join auallnks l on l.src_acc = d.fmt_acc and l.des_mdu = 'AM'  -- Authority 'assets'
                left outer join auallnks l2 on l2.src_acc = d.fmt_acc and l2.des_mdu = 'NR' --NAR
                left outer join aunrmast cn on cn.nar_num = l2.des_num  -- customer NAR
                left outer join auprlink pl on pl.mdu_fmt = d.fmt_acc  --link property/location to CRM 
                left outer join auprstad p on p.pcl_num = pl.pcl_num  -- address of property/location linked to CRM
                left outer join aunrmast nar_ta on nar_ta.nar_num = task.act_nar -- actioning officer NAR
                left outer join aualgpsp gps on gps.mdu_acc = d.fmt_acc
                where
                d.doc_yer >2017 --document year (year CRM created)
                --and pl.mdu_acc > 0 --? required?
                --and p.seq_num = 0  --? required?
                """

            # We don't need as much information for the active crms so simpler
            self._sql_get_active_crm = """
            select d.fmt_acc, d.wrk_typ, d.dda_cd1, d.dda_cd2, d.doc_num
            ,d.cre_dte_tme, RTRIM(d.ext_ref) as ext_ref
            ,RTRIM(d.ext_rf2) as ext_rf2,d.mod_opr
            ,task.key_num as task_key_num, task.rea_cde as task_rea_cde
            ,task.det_cde as task_det_cde, task.clo_dte as task_clo_dte
            ,task.seq_num as task_seq_num
            from aualdocs d 
            ,aualtask task
            where
            d.fmt_acc = task.mdu_fmt
            """

    # @property
    # def classification_codes(self):
    #     return self._classification_codes
    #
    # @classification_codes.setter
    # def classification_codes(self, classification_codes):
    #     if isinstance(classification_codes, list):
    #         self._classification_codes = classification_codes
    #     else:
    #         self.logger.error("classification_codes should be a list")

    @property
    def resolution_code_representation(self):
        """
        This makes the object AuthorityAsseticStatusResolutionCodes available to
        the user script initiating the integration
        :return: AuthorityAsseticStatusResolutionCodes object
        """
        return self._resolution_code_representation

    @property
    def resolution_codes(self):
        return self._resolution_codes

    @resolution_codes.setter
    def resolution_codes(self, value):
        if isinstance(value, list):
            self._resolution_codes = value
        else:
            self.logger.error("resolution_codes should be a list")

    @property
    def wr_crm_code_representation(self):
        """
        This makes the object AuthorityAsseticClassificationCodes available to
        the user script initiating the integration
        :return: AuthorityAsseticClassificationCodes object
        """
        return self._wr_crm_code_representation

    @property
    def wr_crm_code_mappings(self):
        """
        Get a list of objects of type AuthorityAsseticClassificationCodes
        Used to determine the wr subtype and priority to use based on
        CRM category
        """
        return self._wr_crm_code_mappings

    @wr_crm_code_mappings.setter
    def wr_crm_code_mappings(self, value):
        """
        Define a list of objects of type AuthorityAsseticClassificationCodes
        Used to determine the wr subtype and priority to use based on
        CRM category
        """
        if isinstance(value, list):
            self._wr_crm_code_mappings = [
                i if isinstance(i, AuthorityAsseticClassificationCodes)
                else
                self.logger.warning("wr_crm_code_mappings list must contain"
                                    "AuthorityAsseticClassificationCodes "
                                    "objects.  \nIgnoring invalid list item.")
                for i in value]
        else:
            self.logger.error("wr_crm_code_mappings should be a list")

    @property
    def db_connection(self):
        """
        Get the ODBC database connection to Authority database
        """
        return self._db_connection

    @property
    def db_type(self):
        """
        Get the type of database - e.g. Informix or SQL Server
        """
        return self._db_type

    @property
    def doctype(self):
        """
        Authority document type used when creating a task note
        """
        return self._doctype

    @doctype.setter
    def doctype(self, doctype):
        self._doctype = doctype

    @property
    def mduref(self):
        """
        Authority mduref code used when creating a task note
        """
        return self._mduref

    @mduref.setter
    def mduref(self, mduref):
        self._mduref = mduref

    @property
    def typind(self):
        """
        Authority typind code used when creating a task note
        """
        return self._typind

    @typind.setter
    def typind(self, typind):
        self._typind = typind

    @property
    def audmnote_num_typ(self):
        """
        Authority numtype code used when creating a crm note
        """
        return self._audmnote_num_typ

    @audmnote_num_typ.setter
    def audmnote_num_typ(self, audmnote_num_typ):
        self._audmnote_num_typ = audmnote_num_typ

    @property
    def mod_opr(self):
        """
        Authority mod_opr code used when creating a crm note, it is the ID of
        the Authority user creating the note
        """
        return self._mod_opr

    @mod_opr.setter
    def mod_opr(self, mod_opr):
        self._mod_opr = mod_opr

    def update_crm_for_new_wr(self, wr_crm_obj, note_list):
        """
        For the given Assetic work request update the crm
        :param wr_crm_obj: Work Request / CRM object
        :param note_list: a list of crmtools.WrNote objects
        :return: 0 = success, else error
        """
        wr = wr_crm_obj.assetic_wr_representation
        # Now update authority with Assetic guid
        sql = "UPDATE aualdocs SET ext_ref=? WHERE fmt_acc=?;"
        params = (wr.id, wr_crm_obj.crm_id)
        chk = self.run_query(sql, params)
        if chk != 0:
            # there was an error so exit
            return chk
        else:
            # now add a task note to authority indicating request created
            self.add_task_note_to_crm(note_list, wr_crm_obj)
            # could also add comment at the request level?
            # self.add_filenote_to_authority(comment,
            #    wr_crm_obj.crm_id)
        return 0

    # def get_resolution_code_for_subtask(self, wr_subtype, crm_obj):
    #     """
    #     Get the resolution codes for task and CRM based on the work request
    #     subtype and Authority workflow
    #     remedy code/maintenance type?
    #     :param wr_subtype: the work request subtype entered by user
    #     :param crm_obj: the crm object
    #     :return resolution code object
    #     """
    #     for row in self.resolution_codes:
    #         if row.wr_subtype == wr_subtype and \
    #                 row.crm_workflow == crm_obj.workflow:
    #             return row
    #
    #     # no definition found so return default
    #     return AuthorityAsseticResolutionCodes(crm_resolution_code="COMP"
    #                                            , crm_rejection_code="CRCA"
    #                                            , close_crm=True)

    def get_resolution_code_for_status(self, wr_status_id, crm_obj):
        """
        Get the resolution codes for task and CRM based on the work request
        status and CRM Object
        remedy code/maintenance type?
        :param wr_status_id: the Assetic work request status ID
        :param crm_obj: the crm object
        :return resolution code object
        """
        codes = copy.deepcopy(self._resolution_codes)
        for row in codes:
            # since the resolution filters are optional set the undefined ones
            # to the current value so simplify the test
            if not row.crm_category1:
                row.crm_category1 = crm_obj.category1
            if not row.crm_category2:
                row.crm_category2 = crm_obj.category2
            if not row.crm_category3:
                row.crm_category3 = crm_obj.category3
            if not row.crm_task:
                row.crm_task = crm_obj.task_cde
            if not row.crm_workflow:
                row.crm_workflow = crm_obj.workflow
            if row.wr_status == wr_status_id \
                    and row.crm_workflow == crm_obj.workflow\
                    and row.crm_category1 == crm_obj.category1 \
                    and row.crm_category2 == crm_obj.category2 \
                    and row.crm_category3 == crm_obj.category3 \
                    and row.crm_task == crm_obj.task_cde:
                return row

        # no definition found so return default - if that desirable? disabled
        # result = AuthorityAsseticStatusResolutionCodes(
        #    crm_resolution_code="COMP", close_crm=True)
        # self.logger.info("get_resolution_code_for_status - default: {0}"
        #                 "".format(result))
        # return result
        self.logger.info("get_resolution_code_for_status - no definition for "
                         "WR GUID {0}".format(crm_obj.assetic_wr_guid))
        return AuthorityAsseticStatusResolutionCodes()

    def get_crm_requests(self, integrated=False):
        """
        Use a query on the Authority database to get a list of CRMs that satisfy
        the criteria for an Assetic Work Request
        :param integrated: boolean. If true then only get those with an Assetic
        guid that are still active, else only get those without an Assetic guid
        :returns a list of authority_crm_dto objects
        """
        wr_crms = None
        if integrated:
            # get CRMs where there is no task date closed but there is an
            # Assetic id
            sql_where = " and d.ext_ref is not null and task.clo_dte is null"
            sql = "{0} {1} {2}".format(
                self._sql_get_active_crm, self._db_crm_select_filter
                , sql_where)
            wr_crms = self._crm_sql_to_object_list(sql)
        else:
            # get CRMs where there is no Assetic id
            sql_where = " and d.ext_ref is null and task.clo_dte is null"
            sql = "{0} {1} {2}".format(
                self._sql_get_new_crm, self._db_crm_select_filter, sql_where)
            wr_crms = self._crm_sql_to_object_list(sql)
            for wr_crm_obj in wr_crms:
                # also get top level notes. Separate query due to note structure
                wr_crm_obj.crm_representation.description = \
                    self.get_file_note_from_crm(
                        wr_crm_obj.crm_representation.formatted_account)
                wr_crm_obj.assetic_wr_representation = \
                    self.authority_common.prepare_new_wr_object(
                        wr_crm_obj.crm_representation
                        , self.wr_crm_code_mappings)
        return wr_crms

    def _crm_sql_to_object_list(self, sql, params=None):
        """
        Execute SQL on the Authority database and populate WrCrmRepresentation
        object(s) with results. Expects specific fields names, however the query
        does not need to return all fields in object, just mandatory fields
        :param params: Optional params to accompany the SQL
        :returns a list of WrCrmRepresentation objects or empty list if no
        records, or error code if error
        """
        result = self.run_query(sql, params, return_many=True)
        if isinstance(result, int):
            # there was an error so exit
            return result

        # populate dto object with db results
        authority_crms = list()

        for row in result:
            # create new dto object to record raw data
            authority_obj = AuthorityCrmDTO()
            try:
                authority_obj.formatted_account = row.fmt_acc
            except AttributeError:
                self.logger.error("SQL Query must return aualdocs column "
                                  "[fmt_acc]:\r\n{0}".format(sql))
                return 1
            try:
                authority_obj.workflow = row.wrk_typ
            except AttributeError:
                pass
            try:
                authority_obj.category1 = row.dda_cd1
            except AttributeError:
                pass
            try:
                authority_obj.category2 = row.dda_cd2
            except AttributeError:
                pass
            try:
                authority_obj.category3 = row.dda_cd3
            except AttributeError:
                pass
            try:
                authority_obj.crm_number = row.doc_num
            except AttributeError:
                pass
            try:
                authority_obj.received = row.rec_dte
            except AttributeError:
                pass
            try:
                authority_obj.lodgement_method = row.lodgement_method
            except AttributeError:
                pass
            try:
                authority_obj.prop_st_num = row.prop_st_num
            except AttributeError:
                pass
            try:
                authority_obj.prop_st = row.prop_st
            except AttributeError:
                pass
            try:
                authority_obj.prop_sub = row.prop_suburb
            except AttributeError:
                pass
            try:
                authority_obj.task_key = row.task_key_num
            except AttributeError:
                self.logger.error("SQL Query must return aualtask column "
                                  "[key_num] as [task_key_num]:\r\n"
                                  "{0}".format(sql))
                return 1
            try:
                authority_obj.task_cde = row.task_rea_cde
            except AttributeError:
                pass
            try:
                authority_obj.task_det = row.task_det_cde
            except AttributeError:
                pass
            try:
                authority_obj.det_date = row.task_clo_dte
            except AttributeError:
                pass
            try:
                authority_obj.task_seq_num = row.task_seq_num
            except AttributeError:
                self.logger.error("SQL Query must return aualtask column "
                                  "[seq_num] as [task_seq_num]:\r\n"
                                  "{0}".format(sql))
                return 1
            try:
                authority_obj.firstname = row.cust_firstname
            except AttributeError:
                pass
            try:
                authority_obj.familyname = row.cust_famname
            except AttributeError:
                pass
            try:
                authority_obj.business_phone = row.cust_busphn
            except AttributeError:
                pass
            try:
                authority_obj.home_phone = row.cust_home_phn
            except AttributeError:
                pass
            try:
                authority_obj.mobile_phone = row.cust_mob_phn
            except AttributeError:
                pass
            try:
                authority_obj.address_comment = row.cust_addr
            except AttributeError:
                pass
            try:
                authority_obj.due_date = row.task_due_dte
            except AttributeError:
                pass
            try:
                authority_obj.latitude = row.gps_lat
            except AttributeError:
                pass
            try:
                authority_obj.longitude = row.gps_lon
            except AttributeError:
                pass
            try:
                authority_obj.created = row.cre_dte_tme
            except AttributeError:
                pass
            try:
                authority_obj.precis = row.doc_pre
            except AttributeError:
                pass
            try:
                authority_obj.assetic_wr_guid = row.ext_ref
            except AttributeError:
                self.logger.error("SQL Query must return aualdocs column "
                                  "[ext_ref]:\r\n{0}".format(sql))
                return 1
            try:
                authority_obj.assetic_wr_guid_del = row.ext_rf2
            except AttributeError:
                pass
            try:
                authority_obj.mod_opr = row.mod_opr
            except AttributeError:
                self.logger.error("SQL Query must return aualdocs column "
                                  "[mod_opr]:\r\n{0}".format(sql))
                return 1
            try:
                authority_obj.crm_assetid = row.node_num
            except AttributeError:
                pass
            try:
                authority_obj.crm_assetdesc = row.node_desc
            except AttributeError:
                pass
            try:
                authority_obj.assigned_to = row.actioning_officer
            except AttributeError:
                pass
            try:
                authority_obj.contact_method = row.contact_method
            except AttributeError:
                pass
            try:
                authority_obj.risk_id = row.risk_id
            except AttributeError:
                pass
            # create object to return wr and crm info
            wr_crm_obj = WrCrmRepresentation()
            wr = WorkRequest()
            # Get the note if new request and then build assetic wr object
            wr.id = authority_obj.assetic_wr_guid

            wr_crm_obj.assetic_wr_representation = wr

            wr_crm_obj.crm_representation = authority_obj
            wr_crm_obj.crm_id = authority_obj.formatted_account
            # append dto to list
            authority_crms.append(wr_crm_obj)
        return authority_crms

    def get_crm_request_for_wr(self, wr_guid):
        """
        Get the CRM for a given Assetic Work Request GUID
        :param wr_guid: The Assetic Work Request GUID
        :returns a wr_crm_dto object or None
        """
        sql_where = " and d.ext_ref=?"
        params = [wr_guid]
        sql = "{0} {1}".format(self._sql_get_active_crm, sql_where)
        results = self._crm_sql_to_object_list(sql, params)
        if isinstance(results, list):
            if len(results) > 0:
                return results[0]
            else:
                return None
        else:
            return None

    def add_task_note_to_crm(self, new_note_list, wr_crm_obj):
        """
        Add a note to the task. Need to split in 70 char segments
        and append to prior notes using sequence number
        The task is the Assetic specific action (step) in the request document
        workflow.
        :param new_note_list: a list of crmtools.WrNote objects
        :param wr_crm_obj: the work request/CRM object
        :returns: 0 unless error
        """
        # get some values from wr_crm object
        # the authority request id
        crm_obj = wr_crm_obj.crm_representation
        fmt_acc = crm_obj.formatted_account
        # the authority doc number
        doc_num = crm_obj.crm_number
        # mod_opr: the authority operator
        if self._mod_opr:
            mod_opr = self._mod_opr
        else:
            mod_opr = crm_obj.mod_opr

        # some constants
        doctype = self.doctype
        mduref = self.mduref
        typind = self.typind
        doc_prt = 1
        seq_num = crm_obj.task_seq_num

        comment = self._build_comment(new_note_list)
        if not comment:
            # no comments to add
            return 0
        if self._db_type == "informix":
            # Informix error when there is an right quotation mark in data
            comment = comment.replace("’", "'")
            # remove any other unicode characters
            if six.PY2:
                comment = comment.decode('ascii', 'ignore').encode("utf-8")
            else:
                comment = comment.encode('ascii', 'ignore').decode("utf-8")
        sub_seq = self._get_last_task_note_sequence(doc_num, seq_num)

        # calc some vals
        docyer = datetime.datetime.today().year

        sql = "insert into aualtnot (doc_typ,mdu_fmt,doc_num,com_txt,mdu_acc" \
              ",mdu_ref,typ_ind,doc_yer,doc_prt,sub_seq,mod_opr,seq_num" \
              ",cre_dte_tme,mod_dte_tme) " \
              "values (?,?,?,?,?,?,?,?,?,?,?,?,{0},{0})" \
              "".format(self._db_timestamp_str)
        # need to break comment into 70 char chunks
        for chunk in self.authority_common.split_comment(comment, 70):
            sub_seq = sub_seq + 1
            params = [doctype, fmt_acc, doc_num, chunk, doc_num, mduref, typind,
                      docyer, doc_prt, sub_seq, mod_opr, seq_num]
            chk = self.run_query(sql, params)
            if chk != 0:
                # there was an error so exit
                return chk
        return 0

    def _get_last_task_note_sequence(self, doc_num, seq_num):
        """
        Get last sequence number for task note
        :param doc_num: the authority doc number
        :param seq_num: the authority task sequence within the authority doc
        :returns: integer sequence number
        """
        sql = "select max(sub_seq) from aualtnot where doc_num=? and seq_num=?"
        param = [doc_num, seq_num]
        row = self.run_query(sql, param, return_one=True)
        if isinstance(row, int):
            # there was an error, should be of type pyodbc.Row
            return row
        if row and row[0] is not None:
            return row[0]
        else:
            # return zero indicating this is the first note for this doc.
            return 0

    def get_task_note_from_crm(self, crm):
        """
        Get task note for given doc_num
        :param crm: the crm_representation for the Authority crm
        :returns: the comment for the task
        """
        sql = "select com_txt from aualtnot where mdu_fmt=? and seq_num=? " \
              "order by sub_seq asc"
        param = [crm.formatted_account, crm.task_seq_num]

        result = self.run_query(sql, param, return_many=True)
        if isinstance(result, int):
            # there was an error so exit
            return result
        if result is None:
            return ""
        else:
            # Join the result rows, put in a space if the stripped length of a
            # row is not 70 because it implies the text does not continue in the
            # new row
            return "".join([i[0] if len(i[0].strip()) == 70
                            else "{0} ".format(i[0].strip()) for i in result])

    def add_file_note_to_crm(self, new_note_list, fmt_acc):
        """
        Add a note to the request.  Need to split in 70 char segments
        and append to prior notes using sequence number
        This note is at the 'parent' level
        :param new_note_list: a list of crmtools.WrNote objects
        :param fmt_acc: the authority request id
        :returns: 0 unless error
        """

        # some hardcodes
        num_typ = self.audmnote_num_typ
        seq_num = self._get_last_file_note_sequence(fmt_acc)

        comment = self._build_comment(new_note_list)
        if not comment:
            # no comments to add
            return 0
        if self._db_type == "informix":
            # Informix error when there is an right quotation mark in data
            comment = comment.replace("’", "'")
            # remove any other unicode characters
            if six.PY2:
                comment = comment.decode('ascii', 'ignore').encode("utf-8")
            else:
                comment = comment.encode('ascii', 'ignore').decode("utf-8")

        sql = "insert into audmnote (num_typ,fil_num,seq_num,fil_not) values " \
              "(?,?,?,?)"
        # need to break comment into 70 char chunks
        for chunk in self.authority_common.split_comment(comment, 70):
            seq_num = seq_num + 1
            params = [num_typ, fmt_acc, seq_num, chunk]
            chk = self.run_query(sql, params)
            if chk != 0:
                # there was an error so exit
                return chk
        return 0

    def get_file_note_from_crm(self, fmt_acc):
        """
        Get file/document note for given doc_num
        :param fmt_acc: the authority request id
        :returns: the comment for the request
        """
        # some hardcodes
        num_typ = self.audmnote_num_typ

        sql = "select fil_not from audmnote where fil_num=? and num_typ=?" \
              " order by seq_num asc"
        param = [fmt_acc, num_typ]

        result = self.run_query(sql, param, return_many=True)
        if isinstance(result, int):
            # there was an error so exit
            return result
        if result is None:
            return ""
        else:
            # Join the result rows, put in a space if the stripped length of a
            # row is not 70 because it implies the text does not continue in the
            # new row
            return "".join([i[0] if len(i[0].strip()) == 70
                            else "{0} ".format(i[0].strip()) for i in result])

    def _get_last_file_note_sequence(self, fmt_acc):
        """
        Get last sequence number for request notes table
        :param fmt_acc: the authority doc number
        :returns: integer sequence number
        """
        # fil_num is the fmt_acc from aualdocs
        sql = "select max(seq_num) from audmnote where fil_num=?"
        param = [fmt_acc]
        row = self.run_query(sql, param, return_one=True)
        if isinstance(row, int):
            # there was an error, should be of type pyodbc.Row
            return row
        if row and row[0] is not None:
            return row[0]
        else:
            # return zero indicating this is the first note for this doc.
            return 0

    def _build_comment(self, note_list):
        """
        Build a formatted comment string from an array of comments
        :param note_list: a list of crmtools.WrNote objects
        :return: formatted comment
        """

        if len(note_list) == 0:
            return None

        # Build note
        status_note = None
        info_note = None
        schedule_note = None
        target_note = None
        general_note = None
        assetic_fid = None
        # get most recent date to use for note
        status_date = note_list[0].note_date
        for note_obj in note_list:
            if note_obj.note_date > status_date:
                status_date = note_obj.note_date

        # convert list of objects to list of dicts
        dict_list = [i.to_dict() for i in note_list]
        # now sort list of dicts by date so info ordered by date
        alt_sorted = sorted(dict_list, key=lambda k: (
            k["assetic_fid"], k["note_date"]))
        sorted_note_list = sorted(dict_list, key=lambda k: k['note_date'])
        # loop and build grouped strings
        for note_obj in sorted_note_list:
            if note_obj["context"] == "Status":
                status_note = "{0} Status: {1}".format(
                    note_obj["assetic_fid"]
                    , note_obj["note"])
            elif note_obj["context"] == "Supporting Info":
                if self._username_in_note and note_obj["display_name"]:
                    new_info = "({0}) {1}".format(
                        note_obj["display_name"], note_obj["note"])
                else:
                    new_info = "{0}".format(note_obj["note"])
                if info_note:
                    info_note += "; " + new_info
                else:
                    info_note = new_info
            elif note_obj["context"] == "Work Schedule":
                schedule_note = "{0} {1}".format(
                    note_obj["assetic_fid"]
                    , note_obj["note"])
            elif note_obj["context"] == "Work Target":
                target_note = "{0} {1}".format(
                    note_obj["assetic_fid"]
                    , note_obj["note"])
            else:
                # unhandled note type so apply a default format
                if general_note:
                    general_note += "; {0}".format(note_obj["note"])
                else:
                    general_note = "{0} {1}".format(
                        note_obj["assetic_fid"]
                        , note_obj["note"])

        # assemble grouped strings for final note
        comment = None
        if status_note:
            comment = status_note
        if info_note and comment:
            comment += "; " + info_note
        elif info_note:
            comment = info_note
        if schedule_note and comment:
            comment += "; " + schedule_note
        elif schedule_note:
            comment = schedule_note
        if target_note and comment:
            comment += "; " + target_note
        elif target_note:
            comment = target_note
        if general_note and comment:
            comment += "; " + general_note
        elif general_note:
            comment = general_note

        if comment:
            comment = "[{0} {1}]".format(
                status_date.strftime("%d-%m-%Y %H:%M"), comment)
        return comment

    def update_crm_task_status(self, crm_obj, code, statusdate):
        """
        For the given Authority task identifier update Authority task status
        using code and datetime
        :param crm_obj: The crm object
        :param code: determination code
        :param statusdate: the date the status change applies to
        :returns: 0 if success, else error
        """
        fmt_acc = crm_obj.formatted_account # the ID of the Authority Request
        key_num = crm_obj.task_key  # the ID of the task
        try:
            date = '{:%Y-%m-%d %H:%M:%S}'.format(statusdate)
        except ValueError:
            date = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        sql = "update aualtask set clo_dte=?,det_cde=?,mod_dte_tme={0} " \
              "where key_num=? and mdu_fmt=?".format(self._db_timestamp_str)
        param = [date, code, key_num, fmt_acc]
        chk = self.run_query(sql, param)
        if chk != 0:
            # there was an error so exit
            return chk
        return 0

    def update_crm_master_status(self, crm_obj, code, statusdate):
        """
        For the given Authority crm identifier update Authority request status
        using code and datetime.
        :param crm_obj: the crm object
        :param code: the close code
        :param statusdate: the datetime that the request is to be closed
        :returns: 0 if success, else error
        """
        fmt_acc = crm_obj.formatted_account # the ID of the Authority Request
        date = '{:%Y-%m-%d %H:%M:%S}'.format(statusdate)
        sql = "update aualdocs set det_dte=?,det_cde=?,mod_dte_tme={0}" \
              " where fmt_acc=?".format(self._db_timestamp_str)
        param = [date, code, fmt_acc]
        chk = self.run_query(sql, param)
        if chk != 0:
            # there was an error so exit
            return chk
        return 0

    def clear_cancelled_wr_from_crm(self, wr_crm_obj):
        """
        Allow the crm plugin to clear the field used to record the Assetic WR
        GUID. This is for cancelled WR's that may need to be recreated in
        Assetic under a different categorisation against a new CRM task
        :param wr_crm_obj: Work Request / CRM object
        :returns: 0 if success, else error
        """
        # also set mod_dte_tme?

        # if ext_rf2 already has guid's from other cancelled wr's then append
        # this guid to that list, up to a length of 50 char
        wr_guid = wr_crm_obj.assetic_wr_representation.id
        if wr_crm_obj.crm_representation.assetic_wr_guid_del:
            wr_guid = "{0};{1}".format(
                wr_crm_obj.crm_representation.assetic_wr_guid_del, wr_guid)
        sql = "UPDATE aualdocs SET ext_ref=NULL,ext_rf2=? WHERE fmt_acc=?"
        param = [wr_guid[0:50], wr_crm_obj.crm_id]
        chk = self.run_query(sql, param)
        if chk != 0:
            # there was an error so exit
            return chk
        return 0

    def format_datetime_as_str_for_db(self, datetime):
        """
        For the given datetime format as string to match db format
        :param datetime: the datetime to format
        :returns: datetime as string
        """
        if self.db_type == "informix":
            return '{:%Y-%m-%d %H:%M:%S}'.format(datetime)
        elif self.db_type == "sql server":
            return '{:%Y-%m-%d %H:%M:%S}'.format(datetime)

    def finalise(self):
        """
        Called at end of integration process to allow plugin to close db connection
        """
        result = 0
        try:
            self.db_connection.close()
        except Exception as ex:
            self.logger.error("Error closing database connection: {0}".format(
                ex))
            result = 1
        return result

    def run_query(self, sql, params=None, return_one=False, return_many=False):
        """
        Run the provided query and return results
        :params sql: the SQL to execute, may be parameterised query
        :params params: the parameters for the sql as a list
        :params return_one: return first result (use if single record expected)
        boolean - default = False
        :params return_many: return all results. Boolean - default=False
        :returns: 0 if both return_one and return_many are False, else one or
        many records. If both return_one and return_many are True return_one
        takes precedence. If error then non-zero return.
        """
        cursor = self.db_connection.cursor()

        self.logger.debug("{0}; params {1}".format(sql, params))
        try:
            if params is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, params)
            if return_one:
                result = cursor.fetchone()
            elif return_many:
                result = cursor.fetchall()
            else:
                result = 0
        except pyodbc.DatabaseError as err:
            if params:
                try:
                    param_str = "\n".join([str(x) for x in params])
                except TypeError or ValueError:
                    param_str = "Unable to print parameters"
                self.logger.error("Error for SQL {0}\r\n{1}\r\n"
                                  "Parameters:\r\n{2}"
                                  "".format(sql, err, param_str))
            else:
                self.logger.error("Error for SQL {0}\r\n{1}".format(sql, err))
            result = 1
        except Exception as err:
            if params:
                try:
                    param_str = "\n".join([str(x) for x in params])
                except TypeError or ValueError:
                    param_str = "Unable to print parameters"
                self.logger.error("Error for SQL {0}\r\n{1}\r\n"
                                  "Parameters:\r\n{2}"
                                  "".format(sql, err, param_str))
            else:
                self.logger.error("Error for SQL {0}\r\n{1}".format(sql, err))
            result = 1
        finally:
            try:
                self.db_connection.commit()
            except Exception as ex:
                self.logger.error("Error committing SQL {0}\r\n{1}".format(
                    sql, ex))
                result = 1
            try:
                cursor.close()
            except Exception as ex:
                self.logger.error("Error closing cursor for SQL {0}\r\n{1}".
                                  format(sql, ex))
                result = 1
        return result

    @contextmanager
    def open_db_connection(self, db_connection_string, commit=False):
        """
        Use contextmanager to manage connections so we cleanup connection
        as we go to avoid database locking issues on exception
        Not in use, connection not closing fast enough in Informix

        """
        connection = pyodbc.connect(db_connection_string)
        cursor = connection.cursor()
        try:
            yield cursor
        except pyodbc.DatabaseError as err:
            raise err
        except Exception as ex:
            self.logger.error(ex)
        finally:
            if commit:
                try:
                    connection.commit()
                except:
                    pass
            try:
                cursor.close()
            except:
                pass
            try:
                connection.close()
            except:
                pass


class AuthorityCrmDTO(object):
    types = {
        "formatted_account": "str",
        "workflow": "str",
        "category1": "str",
        "category2": "str",
        "category3": "str",
        "crm_number": "str",
        "received": "str",
        "prop_st_num": "str",
        "prop_st": "str",
        "prop_sub": "str",
        "road": "str",
        "road_type": "str",
        "road_sub": "str",
        "task_key": "str",
        "task_cde": "str",
        "task_det": "str",
        "det_date": "str",
        "task_seq_num": "str",
        "firstname": "str",
        "familyname": "str",
        "business_phone": "str",
        "home_phone": "str",
        "mobile_phone": "str",
        "address_comment": "str",
        "description": "str",
        "due_date": "str",
        "latitude": "str",
        "longitude": "str",
        "created": "str",
        "precis": "str",
        "assetic_wr_guid": "str",
        "assetic_wr_guid_del": "str",
        "asset_guid": "str",
        "asset_id": "str",
        "mod_opr": "str",
        "crm_assetid": "str",
        "crm_assetdesc": "str",
        "assigned_to": "str",
        "contact_method": "str",
        "lodgement_method": "str",
        "risk_id": "str"
    }

    def __init__(self, formatted_account=None, workflow=None, category1=None
                 , category2=None, category3=None, crm_number=None
                 , received=None, prop_st_num=None, prop_st=None
                 , prop_sub=None, road=None, road_type=None
                 , road_sub=None, task_key=None, task_cde=None, task_det=None
                 , det_date=None, task_seq_num=None, firstname=None
                 , familyname=None, business_phone=None, home_phone=None
                 , mobile_phone=None, description=None, due_date=None
                 , latitude=None, longitude=None, created=None, precis=None
                 , assetic_wr_guid=None, assetic_wr_guid_del=None
                 , asset_guid=None, asset_id=None, mod_opr=None
                 , address_comment=None, crm_assetid=None, crm_assetdesc=None
                 , assigned_to=None, contact_method=None
                 , lodgement_method=None, risk_id=None):

        self._formatted_account = None
        self._workflow = None
        self._category1 = None
        self._category2 = None
        self._category3 = None
        self._crm_number = None
        self._received = None
        self._prop_st_num = None
        self._prop_st = None
        self._prop_sub = None
        self._road = None
        self._road_type = None
        self._road_sub = None
        self._task_key = None
        self._task_cde = None
        self._task_det = None
        self._det_date = None
        self._task_seq_num = None
        self._firstname = None
        self._familyname = None
        self._business_phone = None
        self._home_phone = None
        self._mobile_phone = None
        self._address_comment = None
        self._description = None
        self._due_date = None
        self._latitude = None
        self._longitude = None
        self._created = None
        self._precis = None
        self._assetic_wr_guid = None
        self._assetic_wr_guid_del = None
        self._asset_guid = None
        self._asset_id = None
        self._mod_opr = None
        self._crm_assetid = None
        self._crm_assetdesc = None
        self._assigned_to = None
        self._contact_method = None
        self._lodgement_method = None
        self._risk_id = None

        if formatted_account is not None:
            self._formatted_account = formatted_account
        if workflow is not None:
            self._workflow = workflow
        if category1 is not None:
            self._category1 = category1
        if category2 is not None:
            self._category2 = category2
        if category3 is not None:
            self._category3 = category3
        if crm_number is not None:
            self._crm_number = crm_number
        if received is not None:
            self._received = received
        if prop_st_num is not None:
            self._prop_st_num = prop_st_num
        if prop_st is not None:
            self._prop_st = prop_st
        if prop_sub is not None:
            self._prop_sub = prop_sub
        if road is not None:
            self._road = road
        if road_type is not None:
            self._road_type = road_type
        if road_sub is not None:
            self._road_sub = road_sub
        if task_key is not None:
            self._task_key = task_key
        if task_cde is not None:
            self._task_cde = task_cde
        if task_det is not None:
            self._task_det = task_det
        if det_date is not None:
            self._det_date = det_date
        if task_seq_num is not None:
            self._task_seq_num = task_seq_num
        if firstname is not None:
            self._firstname = firstname
        if familyname is not None:
            self._familyname = familyname
        if business_phone is not None:
            self._business_phone = business_phone
        if home_phone is not None:
            self._home_phone = home_phone
        if address_comment is not None:
            self._address_comment = address_comment
        if mobile_phone is not None:
            self._mobile_phone = mobile_phone
        if description is not None:
            self._description = description
        if due_date is not None:
            self._due_date = due_date
        if latitude is not None:
            self._latitude = latitude
        if longitude is not None:
            self._longitude = longitude
        if created is not None:
            self._created = created
        if precis is not None:
            self._precis = precis
        if assetic_wr_guid is not None:
            self._assetic_wr_guid = assetic_wr_guid
        if assetic_wr_guid_del is not None:
            self._assetic_wr_guid_del = assetic_wr_guid_del
        if asset_guid is not None:
            self._asset_guid = asset_guid
        if asset_id is not None:
            self._asset_id = asset_id
        if mod_opr is not None:
            self._mod_opr = mod_opr
        if crm_assetid is not None:
            self._crm_assetid = crm_assetid
        if crm_assetdesc is not None:
            self._crm_assetdesc = crm_assetdesc
        if assigned_to is not None:
            self._assigned_to = assigned_to
        if contact_method is not None:
            self._contact_method = contact_method
        if lodgement_method is not None:
            self._lodgement_method = lodgement_method
        if risk_id is not None:
            self._risk_id = risk_id

    @property
    def formatted_account(self):
        return self._formatted_account

    @formatted_account.setter
    def formatted_account(self, formatted_account):
        self._formatted_account = formatted_account

    @property
    def workflow(self):
        return self._workflow

    @workflow.setter
    def workflow(self, workflow):
        self._workflow = workflow

    @property
    def category1(self):
        return self._category1

    @category1.setter
    def category1(self, category1):
        self._category1 = category1

    @property
    def category2(self):
        return self._category2

    @category2.setter
    def category2(self, category2):
        self._category2 = category2

    @property
    def category3(self):
        return self._category3

    @category3.setter
    def category3(self, category3):
        self._category3 = category3

    @property
    def crm_number(self):
        return self._crm_number

    @crm_number.setter
    def crm_number(self, crm_number):
        self._crm_number = crm_number

    @property
    def received(self):
        return self._received

    @received.setter
    def received(self, received):
        self._received = received

    @property
    def prop_st_num(self):
        return self._prop_st_num

    @prop_st_num.setter
    def prop_st_num(self, prop_st_num):
        self._prop_st_num = prop_st_num

    @property
    def prop_st(self):
        return self._prop_st

    @prop_st.setter
    def prop_st(self, prop_st):
        self._prop_st = prop_st

    @property
    def prop_sub(self):
        return self._prop_sub

    @prop_sub.setter
    def prop_sub(self, prop_sub):
        self._prop_sub = prop_sub

    @property
    def road(self):
        return self._road

    @road.setter
    def road(self, road):
        self._road = road

    @property
    def road_type(self):
        return self._road_type

    @road_type.setter
    def road_type(self, road_type):
        self._road_type = road_type

    @property
    def road_sub(self):
        return self._road_sub

    @road_sub.setter
    def road_sub(self, road_sub):
        self._road_sub = road_sub

    @property
    def task_key(self):
        return self._task_key

    @task_key.setter
    def task_key(self, task_key):
        self._task_key = task_key

    @property
    def task_cde(self):
        return self._task_cde

    @task_cde.setter
    def task_cde(self, task_cde):
        self._task_cde = task_cde

    @property
    def task_det(self):
        return self._task_det

    @task_det.setter
    def task_det(self, task_det):
        self._task_det = task_det

    @property
    def det_date(self):
        return self._det_date

    @det_date.setter
    def det_date(self, det_date):
        self._det_date = det_date

    @property
    def task_seq_num(self):
        return self._task_seq_num

    @task_seq_num.setter
    def task_seq_num(self, value):
        self._task_seq_num = value

    @property
    def firstname(self):
        return self._firstname

    @firstname.setter
    def firstname(self, firstname):
        self._firstname = firstname

    @property
    def familyname(self):
        return self._familyname

    @familyname.setter
    def familyname(self, familyname):
        self._familyname = familyname

    @property
    def business_phone(self):
        return self._business_phone

    @business_phone.setter
    def business_phone(self, business_phone):
        self._business_phone = business_phone

    @property
    def home_phone(self):
        return self._home_phone

    @home_phone.setter
    def home_phone(self, home_phone):
        self._home_phone = home_phone

    @property
    def mobile_phone(self):
        return self._mobile_phone

    @mobile_phone.setter
    def mobile_phone(self, mobile_phone):
        self._mobile_phone = mobile_phone

    @property
    def address_comment(self):
        return self._address_comment

    @address_comment.setter
    def address_comment(self, address_comment):
        self._address_comment = address_comment

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def due_date(self):
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        self._due_date = due_date

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        self._latitude = latitude

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        self._longitude = longitude

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, created):
        self._created = created

    @property
    def precis(self):
        return self._precis

    @precis.setter
    def precis(self, precis):
        self._precis = precis

    @property
    def assetic_wr_guid(self):
        return self._assetic_wr_guid

    @assetic_wr_guid.setter
    def assetic_wr_guid(self, assetic_wr_guid):
        self._assetic_wr_guid = assetic_wr_guid

    @property
    def assetic_wr_guid_del(self):
        """
        This is a list of Work Request GUIDs that have been cancelled but are
        from the current CRM
        :return: string of guids or None
        """
        return self._assetic_wr_guid_del

    @assetic_wr_guid_del.setter
    def assetic_wr_guid_del(self, assetic_wr_guid_del):
        self._assetic_wr_guid_del = assetic_wr_guid_del

    @property
    def asset_guid(self):
        return self._asset_guid

    @asset_guid.setter
    def asset_guid(self, asset_guid):
        self._asset_guid = asset_guid

    @property
    def asset_id(self):
        return self._asset_id

    @asset_id.setter
    def asset_id(self, asset_id):
        self._asset_id = asset_id

    @property
    def mod_opr(self):
        return self._mod_opr

    @mod_opr.setter
    def mod_opr(self, mod_opr):
        self._mod_opr = mod_opr

    @property
    def crm_assetid(self):
        return self._crm_assetid

    @crm_assetid.setter
    def crm_assetid(self, crm_assetid):
        self._crm_assetid = crm_assetid

    @property
    def crm_assetdesc(self):
        return self._crm_assetdesc

    @crm_assetdesc.setter
    def crm_assetdesc(self, crm_assetdesc):
        self._crm_assetdesc = crm_assetdesc

    @property
    def assigned_to(self):
        return self._assigned_to

    @assigned_to.setter
    def assigned_to(self, assigned_to):
        self._assigned_to = assigned_to

    @property
    def contact_method(self):
        return self._contact_method

    @contact_method.setter
    def contact_method(self, contact_method):
        self._contact_method = contact_method

    @property
    def lodgement_method(self):
        return self._lodgement_method

    @lodgement_method.setter
    def lodgement_method(self, lodgement_method):
        self._lodgement_method = lodgement_method

    @property
    def risk_id(self):
        return self._risk_id

    @risk_id.setter
    def risk_id(self, risk_id):
        self._risk_id = risk_id

    def to_dict(self):
        "Returns the model properties as a dict"
        result = {}

        for attr, _ in iteritems(self.types):
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
        if not isinstance(other, AuthorityCrmDTO):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        "Returns true if both objects are not equal"
        return not self == other


class AuthorityCRMtest(CRMPluginBase):
    def __init__(self, **kwargs):
        """
        initialise object
        :param **kwargs: requires  3 keywords:
        'db_connection_string' with the connection string defined
        'db_type' one of 'informix' or 'sqlserver'
        'db_crm_select_filter' sql to filter the list of CRM requests.  Use full
        table name and column name
        """
        logger = logging.getLogger(__name__)
        self.logger = logger
        self._db_crm_select_filter = ""
        if "db_connection_string" in kwargs:
            self.logger.info("DB Connection: {0}".format(
                kwargs["db_connection_string"]))
        else:
            msg = "'db_connection_string' not defined when initiating " \
                  "Authority CRM plugin"
            self.logger.error(msg)
            raise AttributeError(msg)
        self._db_connection = ""
        if "db_crm_select_filter" in kwargs:
            self._db_crm_select_filter = kwargs["db_crm_select_filter"]

        self._db_type = None
        if "db_type" in kwargs:
            if kwargs["db_type"].lower() == "informix":
                self._db_type = "informix"
            elif kwargs["db_type"].lower() == "sql server":
                self._db_type = "sql server"
        if self._db_type is None:
            self._db_type = "informix"
            self.logger.warning("kwargs 'db_type' undefined or unsupported. "
                                "Supported types are 'Informix' or 'SQL Server"
                                "Assuming database is Informix")
        self.logger.info("Database type is: {0}".format(self.db_type))

        self.authority_common = AuthorityCommon(**kwargs)

        self._resolution_code_representation = \
            AuthorityAsseticStatusResolutionCodes

        self._classification_codes = list()
        self._resolution_codes = list()

        self._wr_crm_code_mappings = list()
        self._wr_crm_code_representation = \
            AuthorityAsseticClassificationCodes

        self._doctype = 2
        self._mduref = "DD"
        self._typind = "T"
        self._audmnote_num_typ = "D"

        self._test_fmt_acc = "002.2018.01431333.001 "
        self._test_wr_guid = "a5a34605-606e-43b7-9c76-51dc290fbb6f"
        self._test_task_id = "5463456"

    @property
    def classification_codes(self):
        return self._classification_codes

    @classification_codes.setter
    def classification_codes(self, classification_codes):
        if isinstance(classification_codes, list):
            self._classification_codes = classification_codes
        else:
            self.logger.error("classification_codes should be a list")

    @property
    def resolution_code_representation(self):
        return self._resolution_code_representation

    @property
    def resolution_codes(self):
        return self._resolution_codes

    @resolution_codes.setter
    def resolution_codes(self, value):
        if isinstance(value, list):
            self._resolution_codes = value
        else:
            self.logger.error("resolution_codes should be a list")

    @property
    def wr_crm_code_representation(self):
        return self._wr_crm_code_representation

    @property
    def wr_crm_code_mappings(self):
        return self._wr_crm_code_mappings

    @wr_crm_code_mappings.setter
    def wr_crm_code_mappings(self, value):
        if isinstance(value, list):
            self._wr_crm_code_mappings = [
                i if isinstance(i, AuthorityAsseticClassificationCodes)
                else
                self.logger.warning("wr_crm_code_mappings list must contain"
                                    "AuthorityAsseticClassificationCodes"
                                    " objects.\nIgnoring invalid list item.")
                for i in value]
        else:
            self.logger.error("wr_crm_code_mappings should be a list")

    @property
    def db_connection(self):
        """
        Get the ODBC database connection to Authority database
        """
        return self._db_connection

    @property
    def db_type(self):
        """
        Get the type of database - e.g. Informix or SQL Server
        """
        return self._db_type

    @property
    def doctype(self):
        """
        Authority document type used when creating a task note
        """
        return self._doctype

    @doctype.setter
    def doctype(self, doctype):
        self._doctype = doctype

    @property
    def mduref(self):
        """
        Authority mduref code used when creating a task note
        """
        return self._mduref

    @mduref.setter
    def mduref(self, mduref):
        self._mduref = mduref

    @property
    def typind(self):
        """
        Authority typind code used when creating a task note
        """
        return self._typind

    @typind.setter
    def typind(self, typind):
        self._typind = typind

    @property
    def audmnote_num_typ(self):
        """
        Authority numtype code used when creating a crm note
        """
        return self._audmnote_num_typ

    @audmnote_num_typ.setter
    def audmnote_num_typ(self, audmnote_num_typ):
        self._audmnote_num_typ = audmnote_num_typ

    @property
    def test_fmt_acc(self):
        """
        Get the dummy Authority fmt_acc used to test integration.
        """
        return self._test_fmt_acc

    @test_fmt_acc.setter
    def test_fmt_acc(self, test_fmt_acc):
        """
        Define the dummy Authority fmt_acc used to test integration.
        """
        self._test_fmt_acc = test_fmt_acc

    @property
    def test_wr_guid(self):
        """
        Get the dummy Assetic guid used to test integration.
        """
        return self._test_wr_guid

    @test_wr_guid.setter
    def test_wr_guid(self, test_wr_guid):
        """
        Define the dummy Assetic guid used to test integration.
        """
        self._test_wr_guid = test_wr_guid

    @property
    def test_task_id(self):
        """
        Get the dummy Authority task number used to test integration.
        """
        return self._test_task_id

    @test_task_id.setter
    def test_task_id(self, test_task_id):
        """
        Define the dummy Authority task number used to test integration.
        """
        self._test_task_id = test_task_id

    def get_crm_requests(self, integrated=False):
        """
        Use a query on the Authority database to get a list of CRMs that satisfy
        the criteria for an Assetic Work Request
        :param integrated: boolean. If true then only get those with an Assetic
        guid that are still active, else only get those without an Assetic guid
        :returns a list of authority_crm_dto objects
        """

        # return a dummy crm
        authority_crms = list()

        # create new dto object to record raw data
        authority_obj = AuthorityCrmDTO()
        authority_obj.formatted_account = self.test_fmt_acc
        authority_obj.workflow = "BUIL"
        authority_obj.category1 = "MAJOR PROJ"
        authority_obj.category2 = "BUILDINGMA"
        authority_obj.category3 = "BUIDL3"
        authority_obj.crm_number = "1431333"
        authority_obj.received = "2018-07-20T14:07:37.845666"
        authority_obj.prop_st_num = None
        authority_obj.prop_st = None
        authority_obj.prop_sub = None
        authority_obj.task_key = self.test_task_id
        authority_obj.task_cde = None
        authority_obj.task_det = None
        authority_obj.det_date = None
        authority_obj.firstname = "Roger"
        authority_obj.familyname = "Federer"
        authority_obj.business_phone = "03 5634 5678"
        authority_obj.home_phone = None
        authority_obj.mobile_phone = "0417 456 670"
        authority_obj.address_comment = None
        authority_obj.due_date = "2018-07-22T14:07:37.845666"
        authority_obj.latitude = None
        authority_obj.longitude = None
        authority_obj.created = "2018-07-20T15:07:37.845666"
        authority_obj.precis = "TEST - Operations depot - External lock on the fire escape door"
        authority_obj.assetic_wr_guid = None
        authority_obj.mod_opr = 4406
        authority_obj.crm_assetid = "126330"
        authority_obj.crm_assetdesc = "Operations Depot"
        authority_obj.assigned_to = "12345"
        authority_obj.contact_method = "T"

        # create object to return wr and crm info
        wr_crm_obj = WrCrmRepresentation()
        wr = WorkRequest()
        # Get the note if new request and then build assetic wr object
        if integrated:
            wr.id = self.test_wr_guid
        else:
            authority_obj.description = self.get_file_note_from_crm(
                authority_obj.formatted_account)
            wr = self.authority_common.prepare_new_wr_object(
                authority_obj, self.wr_crm_code_mappings)
        wr_crm_obj.assetic_wr_representation = wr

        wr_crm_obj.crm_representation = authority_obj
        wr_crm_obj.crm_id = authority_obj.formatted_account
        # append dto to list
        authority_crms.append(wr_crm_obj)
        return authority_crms

    def get_crm_request_for_wr(self, wr_guid):
        """
        Get the CRM for a given Assetic Work Request GUID
        :param wr_guid: The Assetic Work Request GUID
        :returns a wr_crm_dto object or None
        """
        # create object to return wr and crm info
        wr_crm_obj = WrCrmRepresentation()
        # wr representation
        wr = WorkRequest()
        wr.id = wr_guid
        wr_crm_obj.assetic_wr_representation = wr

        # create new dto object to record raw data
        authority_obj = AuthorityCrmDTO()
        authority_obj.formatted_account = self.test_fmt_acc
        authority_obj.task_key = self.test_task_id
        authority_obj.mod_opr = 4406

        wr_crm_obj.crm_representation = authority_obj
        wr_crm_obj.crm_id = authority_obj.formatted_account
        return wr_crm_obj

    def update_crm_for_new_wr(self, wr_crm_obj, note_list):
        """
        For the given Assetic work request update the crm
        :param wr_crm_obj: Work Request / CRM object
        :param note_list: a list of crmtools.WrNote objects
        :return: 0 = success, else error
        """
        wr = wr_crm_obj.assetic_wr_representation
        # Now update authority with Assetic guid
        sql = "UPDATE aualdocs SET ext_ref={0} WHERE fmt_acc={1};".format(
            wr.id, wr_crm_obj.crm_id)
        self.logger.info("Update crm for new wr: {0}".format(sql))

        self.add_task_note_to_crm(note_list, wr_crm_obj.crm_representation)
        self.logger.info("Finished Update crm for new wr")
        return 0

    def add_task_note_to_crm(self, new_note_list, crm_obj):
        """
        Add a comment to the CRM 'task' using crm_id as the reference
        """
        # get some values from wr_crm object
        # the authority request id
        fmt_acc = crm_obj.crm_representation.formatted_account
        # the authority doc number
        doc_num = crm_obj.crm_representation.crm_number
        # mod_opr: the authority operator
        mod_opr = crm_obj.crm_representation.mod_opr

        # some constants
        doctype = self.doctype
        mduref = self.mduref
        typind = self.typind
        doc_prt = 1
        seq_num = 1
        now = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        sub_seq = self._get_last_task_note_sequence(doc_num)

        status_note = None
        info_note = None
        schedule_note = None
        for note_obj in new_note_list:
            if note_obj.context == "Status":
                status_note = "Status {0} {1}".format(
                    note_obj.note_date.strftime("%d-%m-%Y %H:%M")
                    , note_obj.note)
            elif note_obj.context == "Supporting Info":
                new_info = "{0} {1}".format(
                    note_obj.note_date.strftime("%d-%m-%Y %H:%M")
                    , note_obj.note)
                if info_note:
                    info_note += "; " + new_info
                else:
                    info_note = new_info
            elif note_obj.context == "Work_Schedule":
                schedule_note = "{0} {1}".format(
                    note_obj.note_date.strftime("%d-%m-%Y %H:%M")
                    , note_obj.note)
        comment = None
        if status_note:
            comment = status_note
        if info_note and comment:
            comment += "; " + info_note
        elif info_note:
            comment = info_note
        if schedule_note and comment:
            comment += "; " + schedule_note
        elif info_note:
            comment = schedule_note

        # calc some vals
        docyer = datetime.datetime.today().year

        sql = "insert into aualtnot (doc_typ,mdu_fmt,doc_num,com_txt," \
              "mdu_ref,typ_ind,doc_yer,doc_prt,sub_seq,cre_dte_tme,mod_dte_tme" \
              ",mod_opr,seq_num) values (?,?,?,?,?,?,?,?,?,?,?,?,?)"
        self.logger.info(sql)
        # need to break comment into 70 char chunks
        for chunk in self.authority_common.split_comment(comment, 70):
            sub_seq = sub_seq + 1
            params = [doctype, fmt_acc, doc_num, chunk, mduref, typind,
                      docyer, doc_prt, sub_seq, now, now, mod_opr, seq_num]
            self.logger.info(params)
        self.logger.info("Finish add_task_note_to_crm")
        return 0

    def get_task_note_from_crm(self, crm_id):
        """
        Get the comments from the CRM 'task' using crm_id as the reference
        """
        sql = "select com_txt from aualtnot where mdu_fmt={0} " \
              "order by sub_seq asc".format(crm_id)
        self.logger.info("get_task_note_from_crm: {0}".format(sql))
        return "TEST - Task Note: note specific to the task"

    def add_file_note_to_crm(self, note, crm_id):
        """
        Add a comment to the CRM top level using crm_id as the reference
        """
        # some hardcodes
        num_typ = self.audmnote_num_typ
        seq_num = self._get_last_file_note_sequence(crm_id)

        sql = "insert into audmnote (num_typ,fil_num,seq_num,fil_not) values " \
              "(?,?,?,?)"
        self.logger.info("add_file_note_to_crm: {0}".format(sql))
        # need to break comment into 70 char chunks
        for chunk in self.authority_common.split_comment(note, 70):
            seq_num = seq_num + 1
            params = [num_typ, crm_id, seq_num, chunk]
            self.logger.info(params)
        self.logger.info("Finished add_file_note_to_crm")
        return 0

    def get_file_note_from_crm(self, crm_id):
        """
        Get the comments from the CRM top level using crm_id as the reference
        """
        # some hardcodes
        num_typ = self.audmnote_num_typ

        sql = "select fil_not from audmnote where fil_num={0} and num_typ={1}" \
              " order by seq_num asc".format(crm_id, num_typ)
        self.logger.info("get_file_note_from_crm: {0}".format(sql))
        return "TEST - Operations depot - External lock on the fire escape " \
               "door has been broken again"

    def update_crm_task_status(self, crm_obj, code, statusdate):
        """
        For the given CRM task identifier update task status
        using code and datetime (e.g. reject, close)
        :param crm_obj: The crm object
        :param code: determination code
        :param statusdate: the date the status change applies to
        :returns: 0 if success, else error
        """
        fmt_acc = crm_obj.formatted_account # the ID of the Authority Request
        key_num = crm_obj.task_key  # the ID of the task
        date = '{:%Y-%m-%d %H:%M:%S}'.format(statusdate)
        sql = "update aualtask set clo_dte={0},det_cde={1}" \
              ",mod_dte_tme=current " \
              "where key_num={2} and mdu_fmt={3}".format(
                date, code, key_num, fmt_acc)
        self.logger.info("update_crm_task_status: {0}".format(sql))
        return 0

    def update_crm_master_status(self, crm_obj, code, statusdate):
        """
        For the given crm update request status (e.g. close, reject etc)
        using code and datetime.
        :param crm_obj: the crm object
        :param code: the close code
        :param statusdate: the datetime that the request is to be closed
        :returns: 0 if success, else error
        """
        fmt_acc = crm_obj.formatted_account # the ID of the Authority Request
        date = '{:%Y-%m-%d %H:%M:%S}'.format(statusdate)
        sql = "update aualdocs set det_dte={0},det_cde={1}," \
              "mod_dte_tme=current where fmt_acc={2}".format(
                date, code, fmt_acc)
        self.logger.info("update_crm_master_status: {0}".format(sql))
        return 0

    def _get_last_file_note_sequence(self, fmt_acc):
        """
        Get last sequence number for request notes table
        :param fmt_acc: the authority doc number
        :returns: integer sequence number
        """
        # fil_num is the fmt_acc from aualdocs
        sql = "select max(seq_num) from audmnote where fil_num={0}".format(
            fmt_acc)
        self.logger.info("_get_last_file_note_sequence: {0}"
                         "".format(sql))
        return 3

    # def get_resolution_code_for_subtask(self, wr_subtype, crm_obj):
    #     """
    #     Get the resolution codes for task and CRM based on the work request
    #     subtype and Authority workflow
    #     remedy code/maintenance type?
    #     :param wr_subtype: the work request subtype entered by user
    #     :param crm_obj: the crm object
    #     :return resolution code object CRMAsseticResolutionCodes
    #     """
    #     for row in self.resolution_codes:
    #         if row.wr_subtype == wr_subtype and \
    #                 row.crm_workflow == crm_obj.workflow:
    #             self.logger.info("get_resolution_code_for_subtask: {0}".format(
    #                 row))
    #             return row
    #
    #     # no definition found so return default
    #     result = AuthorityAsseticResolutionCodes(crm_resolution_code="COMP"
    #                                            , crm_rejection_code="CRCA"
    #                                            , crm_cancellation_code="CRCA"
    #                                            , close_crm=True)
    #     self.logger.info("get_resolution_code_for_subtask - default: {0}"
    #                      "".format(result))
    #     return result

    def get_resolution_code_for_status(self, wr_status, crm_obj):
        """
        Get the resolution codes for task and CRM based on the work request
        subtype and CRM Object
        remedy code/maintenance type?
        :param wr_status: the Assetic work request status
        :param crm_obj: the crm object
        :return resolution code object
        """
        for row in self.resolution_codes:
            # since the resolution filters are optional set the undefined ones
            # to the current value so simplify the test
            if not row.crm_category1:
                row.crm_category1 = crm_obj.category1
            if not row.crm_category2:
                row.crm_category2 = crm_obj.category2
            if not row.crm_category3:
                row.crm_category3 = crm_obj.category3
            if not row.crm_task:
                row.crm_task = crm_obj.task_cde
            if not row.crm_workflow:
                row.crm_workflow = crm_obj.workflow
            if row.wr_status.lower() == wr_status.lower() \
                    and row.crm_workflow == crm_obj.workflow\
                    and row.crm_category1 == crm_obj.category1 \
                    and row.crm_category2 == crm_obj.category2 \
                    and row.crm_category3 == crm_obj.category3 \
                    and row.crm_task == crm_obj.task_cde:
                return row

        # no definition found so return default - if that desirable? disabled
        # result = AuthorityAsseticStatusResolutionCodes(
        #    crm_resolution_code="COMP", close_crm=True)
        # self.logger.info("get_resolution_code_for_status - default: {0}"
        #                 "".format(result))
        # return result
        self.logger.info("get_resolution_code_for_status - no definition for "
                         "WR GUID {0}".format(crm_obj.assetic_wr_guid))
        return AuthorityAsseticStatusResolutionCodes()

    def _get_last_task_note_sequence(self, doc_num):
        """
        Get last sequence number for task note
        :param doc_num: the authority doc number
        :returns: integer sequence number
        """
        sql = "select max(sub_seq) from aualtnot where doc_num={0}".format(
            doc_num)
        self.logger.info("_get_last_task_note_sequence: {0}".format(sql))
        return 2

    def finalise(self):
        """
        Called at end of integration process to allow plugin to close db connection
        """
        self.logger.info("CRM Plugin Finalise method executed")
        result = 0

    def clear_cancelled_wr_from_crm(self, wr_crm_obj):
        """
        Allow the crm plugin to clear the field used to record the Assetic WR
        GUID. This is for cancelled WR's that may need to be recreated in
        Assetic under a different categorisation against a new CRM task
        :param wr_crm_obj: Work Request / CRM object
        :returns: 0 if success, else error
        """
        sql = "UPDATE aualdocs SET ext_ref=NULL,ext_rf2={0} " \
              "WHERE fmt_acc={1};"\
            .format(wr_crm_obj.assetic_wr_representation.id, wr_crm_obj.crm_id)
        self.logger.info("Update crm for new wr: {0}".format(sql))
        return 0


class AuthorityCommon(object):
    """
    Common tools for Authority integration regardless of db type or 'test'
    """
    def __init__(self, **kwargs):
        """
        initialise object
        In kwargs optional keys are:
        "reference_id_field": a field name from the wr object to put in
        reference number field
        "default_point": a default wkt point to use if spatial location not set
        """
        logger = logging.getLogger(__name__)
        self.logger = logger
        self.assetapi = AssetApi()
        self.maintenance_tools = MaintenanceTools()
        self.asset_tools = AssetTools()
        self._reference_id_field = None
        if "reference_id_field" in kwargs:
            self._reference_id_field = kwargs["reference_id_field"]
        if "default_point" in kwargs:
            self._default_point = kwargs["default_point"]
        else:
            self._default_point = "POINT (144.9653801142365 " \
                                  "-37.816033070641772)"
        self._default_suburb = None
        self._default_state = None
        if "default_suburb" in kwargs:
            self._default_suburb = kwargs["default_suburb"]
        if "default_state" in kwargs:
            self._default_state = kwargs["default_state"]
        if "default_country" in kwargs:
            self._default_country = kwargs["default_country"]
        else:
            self._default_country = "Australia"

        self._customer_in_info = False
        if "customer_in_info" in kwargs:
            self._customer_in_info = kwargs["customer_in_info"]

        self._nearby_asset_in_info = False
        if "nearby_asset_in_info" in kwargs:
            self._nearby_asset_in_info = kwargs["nearby_asset_in_info"]


    def prepare_new_wr_object(self, authority_obj, wr_sub_type_id_mappings):
        """
        Take the raw authority data for a new Assetic WR and format for Assetic
        WR creation
        :param authority_obj: the raw Authority CRM data
        :param wr_sub_type_id_mappings: list of wr subtype ID mappings to
        Authority keys such as workflow, category, task
        :return:
        """
        # create work request object
        wr = WorkRequest()
        # create address object
        wraddr = CustomAddress()
        # create spatial location object
        wrsl = WorkRequestSpatialLocation()

        # get the Assetic asset if there is a crm asset number
        if authority_obj.crm_assetid is not None and \
                authority_obj.crm_assetid.strip() != "":
            assetic_asset = self.get_asset_by_extid(
                authority_obj.crm_assetid)
            if assetic_asset is not None:
                authority_obj.asset_id = assetic_asset["AssetId"]
                authority_obj.asset_guid = assetic_asset["Id"]

        if authority_obj.asset_guid is not None and \
                authority_obj.asset_guid != "":
            wr.asset_id = authority_obj.asset_id
            # we have an asset id, so use it's location and address
            wraddr, wrsl = self.maintenance_tools.get_location_by_assetguid(
                authority_obj.asset_guid)

        asset_comment = None  # may populate this with list of nearby assets
        if authority_obj.latitude is not None and \
                authority_obj.longitude is not None:
            # location provided by authority
            wrsl.point_string = "POINT ({0} {1})".format(
                authority_obj.longitude, authority_obj.latitude)

            # get nearby assets if CRM defined a point
            if self._nearby_asset_in_info:
                radius = 15
                retries = 2
                retry_factor = 1.5
                asset_geojson = self.asset_tools.get_assets_near_point(
                    authority_obj.latitude, authority_obj.longitude, radius
                    , retries, retry_factor)
                if asset_geojson:
                    # add a comment with list of nearby assets
                    include_categories = list()
                    asset_comment = self.build_comment_for_nearby_assets(
                        asset_geojson, include_categories)

        # set address of defect as entered in CRM
        wraddr.street_number = authority_obj.prop_st_num
        wraddr.street_address = authority_obj.prop_st
        wraddr.city_suburb = authority_obj.prop_sub
        if not wraddr.city_suburb or wraddr.city_suburb == "":
            wraddr.city_suburb = self._default_suburb
        wraddr.state = self._default_state
        wraddr.country = self._default_country

        if wrsl.point_string is None:
            # no spatial - use default value
            wrsl.point_string = self._default_point

        # set location string.  Useful way to see location in UI
        wr.location = "{0} {1} {2}".format(wraddr.street_number
                                           , wraddr.street_address
                                           , wraddr.city_suburb).strip()
        if not wr.location or wr.location.strip() == "":
            wr.location = "location"

        # Assign spatial location to work request
        wr.work_request_spatial_location = wrsl

        # create physical location object and assign address and then assign to
        # request object
        wrfl = WorkRequestPhysicalLocation()
        wrfl.address = wraddr
        wr.work_request_physical_location = wrfl

        # create object for person that lodged the request
        wrreq = RequestorRepresentation()
        wrreq.first_name = authority_obj.firstname
        wrreq.surname = authority_obj.familyname
        # display name restricted to 100 chars so build and truncate
        wrreq.display_name = "{0} {1}".format(
            authority_obj.firstname, authority_obj.familyname)[0:100]
        wrreq.mobile = authority_obj.mobile_phone
        wrreq.phone = authority_obj.home_phone
        wrreq.address_comment = authority_obj.address_comment
        reqtype = RequestorTypeRepresentation()
        reqtype.id = 4  # indicates 'customer'
        wrreq.types = [reqtype]
        # assign requestor to work request
        wr.requestor = wrreq

        wr.external_identifier = authority_obj.formatted_account
        if self._reference_id_field is not None:
            try:
                wr.reference_number = str(
                    getattr(authority_obj, self._reference_id_field))
            except AttributeError as ex:
                self.logger.warning("Unable to set WR Reference Number to CRM"
                                    "field {0}: {1}".format(
                                        self._reference_id_field, str(ex)))
        wr.work_request_source_id = 3  # 3='External CRM'
        # contact customer?
        if authority_obj.contact_method == "NR":
            # no need to respond to customer, but may need to contact
            wr.feedback_required = 0
        else:
            wr.feedback_required = 1
        # contact method
        if authority_obj.contact_method:
            if authority_obj.contact_method.upper() == "T":
                # Telephone
                wr.feedback_method_id = 1
            elif authority_obj.contact_method.upper() == "F":
                # Fax - unsupported- use phone
                wr.feedback_method_id = 1
            elif authority_obj.contact_method.upper() == "L":
                # Letter
                wr.feedback_method_id = 5
            elif authority_obj.contact_method.upper() == "M":
                # Mobile - use text
                wr.feedback_method_id = 2
            elif authority_obj.contact_method.upper() == "S":
                # Social - email
                wr.feedback_method_id = 3
            else:
                # default to phone
                wr.feedback_method_id = 1
        if not authority_obj.lodgement_method:
            authority_obj.lodgement_method = ""
        if not authority_obj.precis:
            authority_obj.precis = ""
        if authority_obj.assigned_to:
            # currently WR does not support 'Assigned To' so prefix description
            wr.description = "Attention: {0}. {1} [{2}]".format(
                authority_obj.assigned_to, authority_obj.precis.strip()
                , authority_obj.lodgement_method.strip())[0:250]
        else:
            wr.description = "{0} [{1}]".format(
                authority_obj.precis.strip()
                , authority_obj.lodgement_method.strip())[0:250]
        if self._customer_in_info:
            customer = "Customer: {0} {1}, {2} Mob:{3} Home:{4}".format(
                authority_obj.firstname, authority_obj.familyname
                , authority_obj.address_comment, authority_obj.mobile_phone
                , authority_obj.home_phone).strip()
            wr.supporting_information = "{0}\n{1}".format(
                authority_obj.description, customer)
        else:
            wr.supporting_information = authority_obj.description
        # Add nearby asset list to supporting info comment
        if asset_comment:
            if wr.supporting_information:
                # append asset list to comment
                wr.supporting_information = "{0}\n{1}".format(
                    authority_obj.description, asset_comment)
            else:
                wr.supporting_information = asset_comment

        if authority_obj.due_date is not None:
            wr.resolution_due_date = authority_obj.due_date
            wr.acknowledge_due_date = authority_obj.due_date

        # set WR subtype and priority
        subtype_id, priority_id = self._get_wr_codes_for_crm(
            authority_obj, wr_sub_type_id_mappings)
        if subtype_id and subtype_id > 0:
            # could also use API at start to get list of valid id's - slow?
            wr.work_request_sub_type_id = subtype_id
        if priority_id and priority_id > 0:
            wr.work_request_priority_id = priority_id
        elif authority_obj.risk_id and len(authority_obj.risk_id) > 0:
            try:
                risk_id_int = int(authority_obj.risk_id)
            except ValueError:
                risk_id_int = 1
            wr.work_request_priority_id = risk_id_int
        else:
            wr.work_request_priority_id = 1  # default as 1
        return wr

    def _get_wr_codes_for_crm(self, crm_obj, wr_crm_code_id_mappings):
        """
        For the given workflow and task get the wr sub type ID and risk id
        utilising mapping set when adapter initialised
        :param crm_obj: The Authority CRM object
        :param wr_crm_code_id_mappings: user defined mapping of Assetic
        subtask id and priority(risk) to Authority categorisations
        :return: tuple of subtype id and priority (risk)
        """
        for row in wr_crm_code_id_mappings:
            # since the resolution filters are optional set the undefined ones
            # to the current value so simplify the test
            if not row.crm_category1:
                row.crm_category1 = crm_obj.category1
            if not row.crm_category2:
                row.crm_category2 = crm_obj.category2
            if not row.crm_category3:
                row.crm_category3 = crm_obj.category3
            if not row.crm_task:
                row.crm_task = crm_obj.task_cde
            if not row.crm_workflow:
                row.crm_workflow = crm_obj.workflow
            if row.crm_workflow == crm_obj.workflow\
                    and row.crm_category1 == crm_obj.category1 \
                    and row.crm_category2 == crm_obj.category2 \
                    and row.crm_category3 == crm_obj.category3 \
                    and row.crm_task == crm_obj.task_cde:
                return row.wr_sub_type_id, row.wr_risk

        # No setting found so return default (risk must be >1)
        return 0, 1

    def get_asset_by_extid(self, extid):
        """
        Get the core asset fields for the external ref id
        :params extid: external ref id
        :returns: return the core attributes as a json object or None
        """
        # define page size (no of records) and page number to get
        pagesize = 1
        qfilter = "ExternalIdentifier='{0}'".format(extid)
        pagenum = 1
        kwargs = {"request_params_page": pagenum,
                  "request_params_page_size": pagesize,
                  "request_params_filters": qfilter}
        attributes = list()

        # now execute the request
        try:
            response = self.assetapi.asset_get_0(attributes, **kwargs)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return None

        if len(response["ResourceList"]) == 1:
            return response["ResourceList"][0]
        else:
            return None

    @staticmethod
    def split_comment(comment, size):
        """
        Split a comment into chunks
        :param comment: the comment to split
        :param size: the character size to split by
        :returns: iterable list of split comments
        """
        for start in range(0, len(comment), size):
            yield comment[start:start + size]

    def build_comment_for_nearby_assets(self, asset_geojson
                                        , include_categories = None ):
        """
        For the given geojson build a string ot add to supporting information
        comment.  The geojson is from Assetic asset location search
        Can limit to asset categories if a list is provided
        :param asset_geojson: geojson from Assetic asset spatial search
        :param include_categories: a list of asset categories to include
        :return: a string comment with basic asset details
        """
        comment = ""

        return comment

class AuthorityAsseticStatusResolutionCodes(CrmAsseticStatusResolutionCodes):
    """
    A class used to define an object for configuring the resolution code and
    whether to close the CRM on resolution
    Overrides the base class CrmAsseticStatusResolutionCodes
    """
    types = {
        "wr_status": "str",
        "crm_resolution_code": "str",
        "close_crm": "bool",
        "crm_workflow": "str",
        "crm_category1": "str",
        "crm_category2": "str",
        "crm_category3": "str",
        "crm_task": "str"
    }

    def __init__(self,
                 crm_workflow=None, crm_category1=None, crm_category2=None,
                 crm_category3=None, crm_task=None, **kw):
        super(AuthorityAsseticStatusResolutionCodes, self).__init__(**kw)
        # self._wr_status = None
        # self._crm_resolution_code = None
        # self._close_crm = None
        #
        # if wr_status is not None:
        #     self._wr_status = wr_status
        # if crm_resolution_code is not None:
        #     self._crm_resolution_code = crm_resolution_code
        # if close_crm is not None:
        #     self._close_crm = close_crm

        self._crm_workflow = crm_workflow
        self._crm_category1 = crm_category1
        self._crm_category2 = crm_category2
        self._crm_category3 = crm_category3
        self._crm_task = crm_task

    # @property
    # def wr_status(self):
    #     return self._wr_status
    #
    # @wr_status.setter
    # def wr_status(self, wr_status):
    #     self._wr_status = wr_status
    #
    # @property
    # def crm_resolution_code(self):
    #     return self._crm_resolution_code
    #
    # @crm_resolution_code.setter
    # def crm_resolution_code(self, crm_resolution_code):
    #     self._crm_resolution_code = crm_resolution_code
    #
    # @property
    # def close_crm(self):
    #     return self._close_crm
    #
    # @close_crm.setter
    # def close_crm(self, close_crm):
    #     self._close_crm = close_crm

    @property
    def crm_workflow(self):
        return self._crm_workflow

    @crm_workflow.setter
    def crm_workflow(self, crm_workflow):
        self._crm_workflow = crm_workflow

    @property
    def crm_category1(self):
        return self._crm_category1

    @crm_category1.setter
    def crm_category1(self, crm_category1):
        self._crm_category1 = crm_category1

    @property
    def crm_category2(self):
        return self._crm_category2

    @crm_category2.setter
    def crm_category2(self, crm_category2):
        self._crm_category2 = crm_category2

    @property
    def crm_category3(self):
        return self._crm_category3

    @crm_category3.setter
    def crm_category3(self, crm_category3):
        self._crm_category3 = crm_category3

    @property
    def crm_task(self):
        return self._crm_task

    @crm_task.setter
    def crm_task(self, crm_task):
        self._crm_task = crm_task

    def to_dict(self):
        "Returns the model properties as a dict"
        result = {}

        for attr, _ in iteritems(self.types):
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


class AuthorityAsseticClassificationCodes(object):
    types = {
        "wr_sub_type_id": "int",
        "crm_workflow": "str",
        "crm_category1": "str",
        "crm_category2": "str",
        "crm_category3": "str",
        "crm_task": "str",
        "wr_risk": "int"
    }

    def __init__(self, wr_sub_type_id=None, crm_workflow=None
                 , crm_category1=None, crm_category2=None, crm_category3=None
                 , crm_task=None, wr_risk=None):

        self._wr_sub_type_id = wr_sub_type_id
        self._crm_workflow = crm_workflow
        self._crm_category1 = crm_category1
        self._crm_category2 = crm_category2
        self._crm_category3 = crm_category3
        self._crm_task = crm_task
        self._wr_risk = wr_risk

    @property
    def wr_sub_type_id(self):
        return self._wr_sub_type_id

    @wr_sub_type_id.setter
    def wr_sub_type_id(self, wr_sub_type_id):
        self._wr_sub_type_id = wr_sub_type_id

    @property
    def crm_workflow(self):
        return self._crm_workflow

    @crm_workflow.setter
    def crm_workflow(self, crm_workflow):
        self._crm_workflow = crm_workflow

    @property
    def crm_category1(self):
        return self._crm_category1

    @crm_category1.setter
    def crm_category1(self, crm_category1):
        self._crm_category1 = crm_category1

    @property
    def crm_category2(self):
        return self._crm_category2

    @crm_category2.setter
    def crm_category2(self, crm_category2):
        self._crm_category2 = crm_category2

    @property
    def crm_category3(self):
        return self._crm_category3

    @crm_category3.setter
    def crm_category3(self, crm_category3):
        self._crm_category3 = crm_category3

    @property
    def crm_task(self):
        return self._crm_task

    @crm_task.setter
    def crm_task(self, crm_task):
        self._crm_task = crm_task

    @property
    def wr_risk(self):
        return self._wr_risk

    @wr_risk.setter
    def wr_risk(self, wr_risk):
        self._wr_risk = wr_risk

    def to_dict(self):
        "Returns the model properties as a dict"
        result = {}

        for attr, _ in iteritems(self.types):
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
        if not isinstance(other, AuthorityAsseticClassificationCodes):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        "Returns true if both objects are not equal"
        return not self == other


# class AuthorityAsseticWRSubTypeCode(object):
#     types = {
#         "wr_sub_type_id": "int",
#         "crm_workflow": "str",
#         "crm_category1": "str",
#         "crm_category2": "str",
#         "crm_category3": "str",
#         "crm_task": "str"
#     }
#
#     def __init__(self, wr_sub_type_id=None, crm_workflow=None
#                  , crm_category1=None, crm_category2=None, crm_category3=None
#                  , crm_task=None):
#         self._wr_sub_type_id = None
#         self._crm_workflow = None
#         self._crm_category1 = None
#         self._crm_category2 = None
#         self._crm_category3 = None
#         self._crm_task = None
#
#         if wr_sub_type_id is not None:
#             self._wr_sub_type_id = wr_sub_type_id
#         if crm_workflow is not None:
#             self._crm_workflow = crm_workflow
#         if crm_category1 is not None:
#             self._crm_category1 = crm_category1
#         if crm_category2 is not None:
#             self._crm_category2 = crm_category2
#         if crm_category3 is not None:
#             self._crm_category3 = crm_category3
#         if crm_task is not None:
#             self._crm_task = crm_task
#
#     @property
#     def wr_sub_type_id(self):
#         return self._wr_sub_type_id
#
#     @wr_sub_type_id.setter
#     def wr_sub_type_id(self, wr_sub_type_id):
#         self._wr_sub_type_id = wr_sub_type_id
#
#     @property
#     def crm_workflow(self):
#         return self._crm_workflow
#
#     @crm_workflow.setter
#     def crm_workflow(self, crm_workflow):
#         self._crm_workflow = crm_workflow
#
#     @property
#     def crm_category1(self):
#         return self._crm_category1
#
#     @crm_category1.setter
#     def crm_category1(self, crm_category1):
#         self._crm_category1 = crm_category1
#
#     @property
#     def crm_category2(self):
#         return self._crm_category2
#
#     @crm_category2.setter
#     def crm_category2(self, crm_category2):
#         self._crm_category2 = crm_category2
#
#     @property
#     def crm_category3(self):
#         return self._crm_category3
#
#     @crm_category3.setter
#     def crm_category3(self, crm_category3):
#         self._crm_category3 = crm_category3
#
#     @property
#     def crm_task(self):
#         return self._crm_task
#
#     @crm_task.setter
#     def crm_task(self, crm_task):
#         self._crm_task = crm_task
#
#     def to_dict(self):
#         "Returns the model properties as a dict"
#         result = {}
#
#         for attr, _ in iteritems(self.types):
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
#         if not isinstance(other, AuthorityAsseticWRSubTypeCode):
#             return False
#
#         return self.__dict__ == other.__dict__
#
#     def __ne__(self, other):
#         "Returns true if both objects are not equal"
#         return not self == other


# class AuthorityAsseticResolutionCodes(CrmAsseticResolutionCodes):
#     types = {
#         "wr_subtype": "str",
#         "wo_remedy_id": "str",
#         "crm_workflow": "str",
#         "crm_category1": "str",
#         "crm_category2": "str",
#         "crm_resolution_code": "str",
#         "crm_rejection_code": "str",
#         "close_crm": "bool"
#     }
#
#     def __init__(self, wr_subtype=None, wo_remedy_id=None, crm_workflow=None
#                  , crm_category1=None, crm_category2=None
#                  , crm_resolution_code=None, crm_rejection_code=None
#                  , crm_cancellation_code=None, close_crm=None):
#         self._wr_subtype = None
#         self._wo_remedy_id = None
#         self._crm_workflow = None
#         self._crm_category1 = None
#         self._crm_category2 = None
#         self._crm_resolution_code = None
#         self._crm_rejection_code = None
#         self._crm_cancellation_code = None
#         self._close_crm = None
#
#         if wr_subtype is not None:
#             self._wr_subtype = wr_subtype
#         if wo_remedy_id is not None:
#             self._wo_remedy_id = wo_remedy_id
#         if crm_workflow is not None:
#             self._crm_workflow = crm_workflow
#         if crm_category1 is not None:
#             self._crm_category1 = crm_category1
#         if crm_category2 is not None:
#             self._crm_category2 = crm_category2
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
#     def crm_workflow(self):
#         return self._crm_workflow
#
#     @crm_workflow.setter
#     def crm_workflow(self, crm_workflow):
#         self._crm_workflow = crm_workflow
#
#     @property
#     def crm_category1(self):
#         return self._crm_category1
#
#     @crm_category1.setter
#     def crm_category1(self, crm_category1):
#         self._crm_category1 = crm_category1
#
#     @property
#     def crm_category2(self):
#         return self._crm_category2
#
#     @crm_category2.setter
#     def crm_category2(self, crm_category2):
#         self._crm_category2 = crm_category2
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
#         for attr, _ in iteritems(self.types):
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
#         if not isinstance(other, AuthorityAsseticResolutionCodes):
#             return False
#
#         return self.__dict__ == other.__dict__
#
#     def __ne__(self, other):
#         "Returns true if both objects are not equal"
#         return not self == other

