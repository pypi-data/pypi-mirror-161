# coding: utf-8

"""
    assetic.APIhelper  (apihelper.py)
    Tools to assist with using Assetic API's and typical integration tasks
"""
from __future__ import absolute_import

import six
import webbrowser  # use for launching assetic
import threading  # use for launching assetic
# use following for emailing
import smtplib
import mimetypes
import csv
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# use following for recording integration time
import os
import dateutil
import datetime

from ..api_client import ApiClient
from ..rest import ApiException


class APIHelper(object):
    """
    Class with generic tools to assist integrations
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        self.logger = api_client.configuration.packagelogger
        self.host = api_client.configuration.host

    def launch_url(self, url):
        """
        Launch a URL in a browser window
        Applications such as ArcMap and its python add-ins are
        sensitive to threading. To open a separate process it needs to be opened
        in it's own thread so it does not interfere with ArcMap.
        The code below will open the url in a new tab in a separate thread.
        :param url: The URL to launch
        """
        # open the url in a new tab in a separate thread.
        browser = threading.Thread(target=webbrowser.open, args=(url, 0))
        browser.start()
        browser.join()

    def launch_assetic_dimension(self, assetguid, componentguid):
        """
        Open assetic and display the dimension page for the component
        :param assetguid: asset guid
        :param componentguid: component guid
        """
        url = "{0}/Assets/{1}/Component/Component/{2}/CPDimension/Default/" \
            .format(self.host, assetguid, componentguid)
        self.launch_url(url)

    def launch_assetic_workorder(self, wkoid):
        """
        Open assetic and display the work order
        :param wkoid: work order guid or friendly ID
        """
        url = "{0}/Maintenance/Operational/Plan/EditWO/?Id={1}".format(
            self.host, wkoid)
        self.launch_url(url)

    def launch_assetic_asset(self, assetid):
        """
        Open assetic and display the asset
        :param assetid: asset guid or friendly ID
        """
        url = "{0}/Assets/ComplexAsset/{1}".format(
            self.host, assetid)
        self.launch_url(url)

    def launch_assetic_functional_location(self, fl_id):
        """
        Open assetic and display the Functional Location
        :param fl_id: Functional Location guid or friendly ID
        """
        url = "{0}/Assets/GroupAsset/{1}".format(
            self.host, fl_id)
        self.launch_url(url)

    def launch_assetic_work_request(self, wrid):
        """
        Open assetic and display the asset
        :param wrid: work request guid or friendly ID
        """
        url = "{0}/Maintenance/Operational/Request/EditWR/?Id={1}".format(
            self.host, wrid)
        self.launch_url(url)

    def launch_assetic_assessment_form_admin(self, form_name):
        """
        Open assetic and display the assessment form in the admin module
        :param form_name: assessment form name
        """
        url = "{0}/Admin/Assessment/ASMTForm/Config/{1}".format(
            self.host, form_name)
        self.launch_url(url)

    def smtp_mailer(self, mailhost, port, username, password, fromaddr, toaddrs,
                    msg, isthread=False):
        """
        Send an email via SMTP using TLS (port 587) or SSL (port 465) or
        no auth (port 25)
        Better to use TLS if possible since TLS supercedes SSL
        :param mailhost: the SMTP host
        :param port: SMTP port, expect one of 587 (TLS), 465 (SSL), or 25
        :param username: username.  May be None
        :param password: password. May be None
        :param fromaddr: 'From' email address
        :param toaddrs: 'To' email addresses, comma separated
        :param msg: email message as MIME message object
        :param isthread: True if this is an SMTP logging handle.
        Need to know so that this method won't write exceptions, sending the
        email because the handler picks up the error and it causes an error loop
        """

        smtp = None
        if port == "587":
            try:
                smtp = smtplib.SMTP(mailhost, port)
            except Exception as ex:
                if not isthread:
                    msg = "Unable to initialise TLS smtp variable. " \
                          "Host: {0}; Port {1}; Error {2}".format(
                        mailhost, port, str(ex))
                    self.logger.error(msg)
                return 1
        elif port == "465":
            try:
                smtp = smtplib.SMTP_SSL(mailhost, port)
            except Exception as ex:
                if not isthread:
                    msg = "Unable to initialise SSL smtp variable. " \
                          "Host: {0}; Port {1}; Error {2}".format(
                        mailhost, port, str(ex))
                    self.logger.error(msg)
                return 1
        elif port == "25":
            # try simple email module
            try:
                smtp = smtplib.SMTP(mailhost, port)
            except Exception as ex:
                if not isthread:
                    msg = "Unable to initialise smtp variable. " \
                          "Host: {0}; Port {1}; Error {2}".format(
                        mailhost, port, str(ex))
                    self.logger.error(msg)
                return 1
        if smtp is None:
            if not isthread:
                self.logger.error("email protocol not configured/supported. " \
                                  "Host: {0}; Port {1}".format(mailhost, port))
            return 1
        try:
            if username:
                smtp.ehlo()  # possibly optional for SSL.  Need for TLS
                if port == "587":
                    # for tls need these extra lines
                    smtp.starttls()
                    smtp.ehlo()  # for tls add this line
                smtp.login(username, password)
            # Now send the actual email
            # smtp.sendmail(fromaddr, toaddrs, msg)
            if six.PY2:
                msg = msg.as_string()
                smtp.sendmail(fromaddr, toaddrs, msg)
            else:
                # send_message (>=py3.2) will hide bcc list from
                # 'To' and 'Cc' recipients, unlike sendmail
                smtp.send_message(msg, fromaddr, toaddrs)
            smtp.quit()
        except Exception as ex:
            if not isthread:
                self.logger.error("Error sending email. " \
                                  "Host: {0}; Port {1}; Error: {2}".format(
                    mailhost, port, str(ex)))
            return 1
        return 0

    def create_message(self, fromaddr, toaddr, subject, message
                       , ccaddr=None, bccaddr=None,replytoaddr=None):
        """
        Create an email message
        :param fromaddr: 'From' email address (or 'user friendly name')
        :param toaddr: 'To' email addresses - a list
        :param subject: email subject
        :param message: the message.
        :param ccaddr: 'Cc' email addresses, comma separated (Optional)
        :param bccaddr: 'Bcc' email addresses, comma separated (Optional)
        :param replytoaddr: return email address (Optional)
        :return: email message as MIMEtext
        """
        if not isinstance(toaddr, list):
            return None

        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = fromaddr
        for to in toaddr:
            msg['To'] = to
        # msg['To'] += tuple(toaddr)
        if ccaddr:
            msg["Cc"] = ccaddr
        if bccaddr:
            msg["Bcc"] = bccaddr
        if replytoaddr:
            msg["Reply-To"] = replytoaddr
        return msg

    def create_message_with_attachment(self, fromaddr, toaddr, subject,
                                       htmlbody, plainbody, documents,
                                       ccaddr=None, bccaddr=None,
                                       replytoaddr=None):
        """
        Create an email message
        :param fromaddr: 'From' email address (or 'user friendly name')
        :param subject: email subject
        :param htmlbody: email as html.
        :param plainbody: email as text.  This is the alternate in case the
        mail tool is unable to render the html
        :param documents: A list of tuples - document to attach as byte string
        and document name including file extension.
        :param toaddr: 'To' email addresses, comma separated (Optional)
        :param ccaddr: 'Cc' email addresses, comma separated (Optional)
        :param bccaddr: 'Bcc' email addresses, comma separated (Optional)
        :param replytoaddr: return email address (Optional)
        :return: email message as MIMEMultipart('mixed')
        """

        msg = MIMEMultipart('mixed')
        msg['Subject'] = subject
        msg['From'] = fromaddr
        msg['To'] = toaddr
        if ccaddr:
            msg["Cc"] = ccaddr
        if bccaddr:
            msg["Bcc"] = bccaddr
        if replytoaddr:
            msg["Reply-To"] = replytoaddr

        # Record the MIME types of both parts - text/plain and text/html.
        part_alt_text = MIMEText(plainbody, 'plain')
        part_html = MIMEText(htmlbody, 'html')

        # create a message container that will have the 'alternative' container
        # and attachments
        message_related = MIMEMultipart('related')
        # Create the 'alternative' message container
        # for the html and alternate text
        # the correct MIME type is multipart/alternative.
        message_alternative = MIMEMultipart('alternative')
        message_related.attach(part_html)

        # Attach parts into message alternative container.
        # According to RFC 2046, the last part of a multipart message
        # , in this case the HTML message, is best and preferred.
        message_alternative.attach(part_alt_text)
        message_alternative.attach(message_related)

        # Now attach message options to 'mixed' container
        msg.attach(message_alternative)

        for doc, filename in documents:
            # guess file type based on file extension
            content_type, encoding = mimetypes.guess_type(filename)
            main_type, sub_type = content_type.split('/', 1)
            # based on the main_type part of contenttype, set MIMEtype
            if main_type == 'text':
                mimedoc = MIMEText(doc, _subtype=sub_type)
            elif main_type == 'image':
                mimedoc = MIMEImage(doc, _subtype=sub_type)
            elif main_type == 'audio':
                mimedoc = MIMEAudio(doc, _subtype=sub_type)
            else:
                mimedoc = MIMEBase(main_type, sub_type)
                mimedoc.set_payload(doc)
            mimedoc.add_header('Content-Disposition',
                               'attachment; filename="{0}"'.format(filename))
            msg.attach(mimedoc)
        return msg

    def generic_get(self, url):
        """
        Apply a GET to assetic rest api's for given URL.
        Do not include the assetic environment in the URL
        (e.g configuration.host)
        :param url: The URL to execute against the assetic connection
        Returns: json string
        """
        self.logger.debug("Generic Get raw URL: {0}".format(url))
        header_params = {'Accept': 'application/json',
                         'Content-Type': self.api_client.
                             select_header_content_type([])}
        auth_settings = []
        body_params = None
        form_params = []
        local_var_files = {}
        query_params = {}
        path_params = {}
        resource_path = url
        all_params = ['callback', '_return_http_data_only', '_preload_content',
                      '_request_timeout']
        params = locals()
        collection_formats = {}
        try:
            response = self.api_client.call_api(resource_path, 'GET',
                                                path_params, query_params,
                                                header_params, body=body_params,
                                                post_params=form_params,
                                                files=local_var_files,
                                                response_type='String',
                                                auth_settings=auth_settings,
                                                _return_http_data_only=params.get(
                                                    '_return_http_data_only'),
                                                _preload_content=params.get(
                                                    '_preload_content', True),
                                                _request_timeout=params.get(
                                                    '_request_timeout'),
                                                collection_formats=collection_formats)
        except ApiException as e:
            self.logger.error('Status {0}, Reason: {1} {2}'.format(
                e.status, e.reason, e.body))
            return None
        else:
            # comes back as a tuple
            return response[0]

    def read_csv_file_into_dict(self, filename, structure=None):
        """
        Read the the contents of a csv file into a representation that can be
        used to build the controls on a form
        :param filename: the file to read
        :param structure: the layout mapping of the rows in the file
        :returns: a list of dictionary objects that match the input structure
        """
        if structure is None:
            structure = "Label"

        rows = list()
        if six.PY2:
            self.logger.debug("Reading file")
            with open(filename, 'rt') as csvfile:
                readCSV = csv.DictReader(
                    csvfile, fieldnames=structure, delimiter=',')
                for row in readCSV:
                    rows.append(row)
        else:
            try:
                self.logger.debug("Reading file with UTF-8 encoding")
                with open(filename, 'rt', encoding='utf-8', newline='') \
                        as csvfile:
                    readCSV = csv.DictReader(csvfile, fieldnames=structure,
                                             delimiter=',')
                    for row in readCSV:
                        rows.append(row)
            except UnicodeDecodeError:
                self.logger.debug("Try reading file without UTF-8 encoding")
                with open(filename, 'rt', newline='') as csvfile:
                    readCSV = csv.DictReader(csvfile, fieldnames=structure,
                                             delimiter=',')
                    for row in readCSV:
                        rows.append(row)
        self.logger.debug("Found {0} rows in csv file".format(len(rows)))
        return rows

    def set_last_integration_datetime(self, integration_name, last_date):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Write date in a text file in %APPDATA%/Assetic
        :param integration_name: A name unique to the integration
        :param last_date: the datetime to record
        :return 0=success, else error
        """
        appdata = os.environ.get("APPDATA")
        if not os.path.exists(os.path.join(appdata, "Assetic")):
            try:
                os.makedirs(os.path.join(appdata, "Assetic"))
            except Exception as e:
                msg = "Unable to create folder {0} with error: {1}\n" \
                      "Will use date {2} instead".format(
                    os.path.join(appdata, "Assetic"), str(e), str(last_date))
                self.logger.warning(msg)
                return 1
        file = os.path.join(appdata, "Assetic", "{0}.txt".format(
            integration_name))
        try:
            with open(file, "w+") as f:
                f.write(last_date.isoformat())
        except Exception as e:
            msg = "Unable to write datetime file {0} with error: {1}".format(
                file, str(e))
            self.logger.error(msg)
            return 1
        else:
            return 0

    def get_last_integration_datetime(self, integration_name,
                                      seed_date_if_null=None):
        """
        Record the datetime of the last integration to act as starting point
        for next integration
        Read date from a text file in %APPDATA%/Assetic. If not found then
        use seed date if provided, else current date less 1 week.
        :param integration_name: A name unique to the integration
        :param seed_date_if_null: optional datetime to seed the process if no
        date file is found
        :return: date
        """
        appdata = os.environ.get("APPDATA")
        file = os.path.join(appdata, "Assetic", "{0}.txt".format(
            integration_name))

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
