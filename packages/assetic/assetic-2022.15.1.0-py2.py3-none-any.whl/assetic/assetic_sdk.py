# coding: utf-8

"""
    Assetic Integration SDK
    Initiates API wrappers and tools to manage integration workflows
"""

from __future__ import absolute_import
import os
import sys
import logging
import logging.handlers
import threading  # use for email error logging
import smtplib  # use for email logging
import six

try:
    import configparser as configparser
except ImportError:
    import ConfigParser as configparser
from .api_client import ApiClient
from .configuration import Configuration
from .tools.apihelper import APIHelper
from .tools.vault_tools import VaultTools
from .__version__ import __version__

# from urllib3 import exceptions

# create a logger to catch unhandled exceptions prior to initialisation of the
# user specified logger
logger = logging.getLogger(__name__)
if len(logger.handlers) == 0:
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.WARNING)
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    If an exception is uncaught it isn't written to the log, so capture the
    exception here and write to the log.  It will also write to stderr
    :param exc_type: exception type
    :param exc_value: exception
    :param exc_traceback: traceback
    """
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    if issubclass(exc_type, KeyboardInterrupt):
        return

    # if exc_type == exceptions.MaxRetryError:
    #    # urllib connection to Assetic failed after retry attempts
    #    logger.error("Connection error: {0}".format(exc_value))
    # else:
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value,
                                                 exc_traceback))


sys.excepthook = handle_uncaught_exception


class AsseticSDK(object):
    """
    class to initialise sdk and api methods
    """

    def __init__(self, inifile=None, logfile=None, loglevelname=None):
        """
        Constructor of the class.
        Param inifile: the file name (including path) of the ini file
        (host, username, api_key).
        If none then will look in local folder for assetic.ini
        ,else look in environment variables for asseticSDKhost, asseticSDKusername
        ,asseticSDKapi_key
        Param logfile: the file name (including path) of the log file.
        If None then no logfile will be created
        Param loglevelname: set as a valid logging level description e.g. INFO
        """
        host = None
        if inifile == None:
            ##look in current folder for 'assetic.ini'
            inifile = os.path.join(os.getcwd(), "assetic.ini")
            if os.path.isfile(inifile) == False:
                appdata = os.environ.get("APPDATA")
                inifile = os.path.join(appdata, "Assetic", "assetic.ini")
        if os.path.isfile(inifile) == True:
            host, username, api_key, proxy = self.get_credentials_via_file(
                inifile)
            self.__inifile = inifile
        else:
            host, username, api_key, proxy = self.get_credentials_via_env()
            self.__inifile = None
        if host == None:
            message = """Configuration file not found.
                Expecting to be set via module init as the first parameter,    
                else assetic.ini in either the current folder (1st preference),
                or assetic.ini in $APPDATA/Assetic (2nd preference)
                else set in the following environment variables:
                ASSETICHOST: the base URL
                ASSETICUSER: the Assetic username
                ASSETICKEY for the token
                ASSETICCLIENTPROXY for the proxy server if required"""
            logger.error(message)
            return

        config = Configuration()
        config.host = host
        config.username = username
        config.password = api_key
        auth = config.get_basic_auth_token()
        config.proxy = proxy
        ##set defaults for any subsequnet instantiation of Configuration
        config._default.host = host
        config._default.username = username
        config._default.password = api_key
        auth = config.get_basic_auth_token()
        config._default.proxy = proxy

        if logfile == None or logfile == "":
            pass
        else:
            config._default.logger_file = logfile
        loglevel = self.verify_log_level(loglevelname)
        config._default.packagelogger.setLevel(loglevel)
        if config._default.packagelogger.level == 10:
            config._default.debug = True

        ##Assetic SDK client instance      
        self.client = ApiClient(config, "Authorization", auth)
        self.client.user_agent = "Assetic_Python_SDK_{0}".format(
            __version__)
        ##Asset SDK client instance for docs
        # self.client_for_docs = ApiClient(config,"Authorization", auth ,
        #                        None,'Content-Disposition')
        # self.client_for_docs.user_agent="Assetic_Python_SDK_{0}".format(
        #    __version__)

        ##Set the default client against config
        config._default.api_client = self.client

        ##reference config in self so we can use it
        self.conf = config

    @property
    def logger(self):
        """
        Gets the logger.  Allows referencing of logger and further customisation
        """
        return self.conf.packagelogger

    @property
    def debug_https_request(self):
        """
        Deprecated - Did get the status of the https debug from self.config,
        but this is no longer created by codegen.
        """
        return None

    @debug_https_request.setter
    def debug_https_request(self, value):
        """
        Deprecated = Did Set the format of the log for https request
        but this is no longer created by codegen.        
        """
        pass

    @property
    def logger_format(self):
        """
        Gets the logger format.
        """
        return self.conf.logger_format

    @logger_format.setter
    def logger_format(self, value):
        """
        Set the format of the log
        """
        for handler in self.conf.packagelogger.handlers:
            formatter = logging.Formatter(value)
            handler.setFormatter(formatter)

    @property
    def client_for_docs(self):
        """
        This is no longer supported, so raise exception with instructions
        """
        msg = "asseticSDK.client_for_docs is obsolete, \nuse API " \
              "document_get_document_file_with_http_info \nwhich returns " \
              "a tuple, the 3rd value being the headers \nwhich contain " \
              "Content-Dispostion which is what \nclient_for_docs previously " \
              "returned"
        raise Exception(msg)

    def get_credentials_via_file(self, inifile):
        """
        get credentials from ini file
        param inifile: ini file with host, username, api_key 
        Returns: tuple containing:
        host: assetic host
        username: username
        api_key: authentication token
        """
        settings = configparser.ConfigParser()
        settings.read(inifile)

        try:
            host = settings.get('environment', 'url')
            username = settings.get('auth', 'username')
            password = settings.get('auth', 'api_key')

        except configparser.NoSectionError as ex:
            msg = "Error reading Assetic configuration from {0}. \r\n\{1}".format(
                inifile, str(ex))
            logger.error(msg)
            return None, None, None, None
        except configparser.NoOptionError as ex:
            try:
                host = settings.get('environment', 'url')
                username = settings.get('auth', 'username')
                # get password from windows credentials
                a = VaultTools(host, encode=0)
                password = a.get_pwd(username)
                if password is None:
                    # get password from windows credentials that is encoded
                    a = VaultTools(host, encode=1)
                    password = a.get_pwd(username)

                if password is None:
                    try:
                        host = settings.get('environment', 'url')
                        username = settings.get('auth', 'username')
                        password = settings.get('auth', 'api_key')
                    except configparser.NoOptionError as ex:
                        msg = "Error reading Assetic configuration from {0}. \r\n\{1}".format(
                            inifile, str(ex))
                        logger.error(msg)
                        return None, None, None, None

            except configparser.NoOptionError as ex:
                msg = "Error reading Assetic configuration from {0}. \r\n\{1}".format(
                    inifile, str(ex))
                logger.error(msg)
                return None, None, None, None
        except Exception as ex:
            msg = "Error reading Assetic configuration from {0}. {1}".format(
                inifile, str(ex))
            logger.error(msg)
            return None, None, None, None

        try:
            proxy = settings.get('proxy', 'server')
        except:
            ##proxy is optional so not raise error
            proxy = None
        return host, username, password, proxy

    def get_credentials_via_env(self):
        """
        get credentials from environment variables. Looks for ASSETICHOST for
        the base URL, ASSETICUSER for the username, ASSETICKEY for the token
        Returns: tuple containing:
        host: assetic host
        username: username
        api_key: authentication token
        """
        host = None
        username = None
        password = None
        proxy = None
        if 'ASSETICHOST' in os.environ:
            host = os.environ['ASSETICHOST']
        if 'ASSETICUSER' in os.environ:
            username = os.environ['ASSETICUSER']
        if 'ASSETICKEY' in os.environ:
            password = os.environ['ASSETICKEY']
        if 'ASSETICCLIENTPROXY' in os.environ:
            proxy = os.environ['ASSETICCLIENTPROXY']
        return host, username, password, proxy

    def get_smtp_settings(self, inifile=None):
        """
        From the ini file get the settings for the SMTP mail
        param inifile: optional ini file, else ini self.__inifile used
        Returns: tuple of host,port,from_login,from_pass or None,None,None,None
        if error
        """
        ##set error return tuple
        err = None, None, None, None

        # use inifile that was passed in, unless it is None
        if inifile == None or inifile == "":
            inifile = self.__inifile

        ##get SMTP settings
        settings = configparser.ConfigParser()
        if inifile == None or os.path.isfile(inifile) == False:
            msg = "assetic.ini file is missing or undefined. " \
                  "Mail logging will not be setup"
            self.logger.warning(msg)
            return err

        settings.read(inifile)
        # Apply assetic config settings
        try:
            host = settings.get('smtpserver', 'host')
            port = settings.get('smtpserver', 'port')
        except configparser.NoSectionError as ex:
            msg = "Error reading smtp configuration from {0}. \r\n\{1}".format(
                inifile, str(ex))
            self.logger.error(msg)
            return err
        except configparser.NoOptionError as ex:
            msg = "Error reading smtp configuration from {0}. \r\n\{1}".format(
                inifile, str(ex))
            self.logger.error(msg)
            return err
        except Exception as ex:
            msg = "Error reading smtp configuration from {0}. \r\n\{1}".format(
                inifile, str(ex))
            self.logger.error(msg)
            return err

        if six.PY2 and type(port) == unicode:
            try:
                port = str(port).encode('utf-8')
            except:
                pass

        from_login = None
        from_pass = None
        try:
            from_login = settings.get('smtpauth', 'username')
            from_pass = settings.get('smtpauth', 'password')
        except configparser.NoSectionError as ex:
            if port != "25":
                msg = "Error reading smtp configuration from {0}. \r\n\{1}" \
                      "".format(inifile, str(ex))
                self.logger.error(msg)
                return err
        except configparser.NoOptionError as ex:
            if port != "25":
                msg = "Error reading smtp configuration from {0}. \r\n\{1}" \
                      "".format(inifile, str(ex))
                self.logger.error(msg)
                return err
        except Exception as ex:
            if port != "25":
                msg = "Error reading smtp configuration from {0}. \r\n\{1}" \
                      "".format(inifile, str(ex))
                self.logger.error(msg)
                return err

        return host, port, from_login, from_pass

    def verify_log_level(self, loglevelname):
        """
        verify loglevel is valid for given text description
        needs to be a valid logging name, else set to zero (no logging)
        param loglevelname: the name of the logging level to test & set
        Returns: loglevel (int)
        """
        # make sure a string is being tested.
        # If an int assume user is setting the level directly
        if isinstance(loglevelname, six.integer_types):
            return loglevelname
        elif isinstance(loglevelname, six.string_types):
            try:
                getattr(logging, loglevelname.upper())
            except AttributeError as ex:
                raise ValueError(str(ex))
            return loglevelname.upper()
        else:
            return 0

    def setup_log_to_email(self, from_email, dest_emails, subject=None, capacity=1, loglevelname="Error",
                           logformat=None):
        """
        Setup logging to email.  Settings to smtp server in assetic.ini file
        Direct logging of log events to email so best to set log level to
        'error'.  Has it's own handler so can use different log level to file
        or console.
        The flush event
        param from_email: the email address of the 'sender'
        param dest_emails: A list of email address (type = list)
        param subject: Email subject
        param capacity: The number of errors that will be grouped together
        before an email is sent.  Integer. Default=1 which means each error will
        result in a separate email
        param loglevelname: the name of the logging level to set
        param logformat:format string for logging output
        Returns: 0=success, >0 error
        """

        # ensure destination emails defined and in correct format
        if type(dest_emails) != list or len(dest_emails) == 0:
            msg = "destination email list is missing or undefined. " \
                  "Mail logging will not be setup.  It must be of type 'list'"
            self.logger.warning(msg)
            return msg
        # get SMTP settings
        host, port, from_login, from_pass = self.get_smtp_settings()
        if host == None:
            return 1

        mailer = BufferingSMTPHandler(host, port, from_email, dest_emails,
                                      subject, from_login, from_pass, capacity, self.logger)
        if logformat != None:
            formatter = logging.Formatter(logformat)
            mailer.setFormatter(formatter)
        loglevel = self.verify_log_level(loglevelname)
        mailer.setLevel(loglevel)
        mailer.set_name("mailhandler")
        self.logger.addHandler(mailer)
        return 0

    def flush_email_logger(self):
        """
        The email logger handler needs flushing at the end of a script in case
        there are logging events still in the buffer awaiting email
        This method is therefore called at the end of running a script
        """
        for loghandle in self.logger.handlers:
            if loghandle.name == "mailhandler":
                loghandle.flush()


class ThreadedSMTPHandler(logging.handlers.SMTPHandler):
    """
    SMTP handler for logging
    Send logging message as an email.
    Uses a separate thread.
    Currently not implemented in this SDK, using the Buffering handler instead
    """

    def emit(self, record):
        """
        Initiates the thread to email in response to a logging event
        :param record: The logger object for the logging event
        """

        port = self.mailport
        if not port:
            port = smtplib.SMTP_PORT

        # initialise api helper
        apihelper = APIHelper()

        msg = apihelper.create_message(
            self.fromaddr, self.toaddrs, self.getSubject(record)
            , self.format(record))
        try:
            # msg = self.format(record)   #get error message
            # msg = "From:{0}\r\nTo:{1}\r\nSubject:{2}\r\nDate:{3}\r\n\r\n{4}".format(
            #    self.fromaddr, ",".join(self.toaddrs),self.getSubject(record),
            #    formatdate(), msg)
            thread = threading.Thread(
                target=apihelper.smtp_mailer
                , args=(self.mailhost, port, self.username
                        , self.password, self.fromaddr, self.toaddrs, msg, True)
            )
            thread.daemon = True
            thread.start()
        except(KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            raise


class BufferingSMTPHandler(logging.handlers.BufferingHandler):
    """
    Buffered SMTP handler for logging
    Send logging message as an email.
    Buffers the log messages and sends as email when user defined number of
    log messages is reached.
    """

    def __init__(self, mailhost, mailport, fromaddr, toaddrs, subject, username, password, capacity, logger):
        """
        Initiates the BufferingSMTP handler
        """
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = mailport
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.username = username
        self.password = password
        self.__mailerror = False
        self.logger = logger
        # self.setFormatter(logging.Formatter("%(asctime)s %(levelname)-5s %(message)s"))

    def flush(self):
        """
        Flush the message buffer.  This sends all outstanding messages in buffer
        Use at end of script to ensure all messages have been mailed - if number
        of messages is currently less than buffer they may not otherwise be sent
        on completion of the script
        """
        if len(self.buffer) > 0 and not self.__mailerror:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT

            # initialise api helper
            apihelper = APIHelper()

            # msg = "From:{0}\r\nTo:{1}\r\nSubject:{2}\r\nDate:{3}\r\n\r\n".format(
            #    self.fromaddr, ",".join(self.toaddrs),self.subject,
            #    formatdate())
            msg = ""
            for record in self.buffer:
                s = self.format(record)
                msg = msg + s + "\r\n"
            mime_msg = apihelper.create_message(self.fromaddr, self.toaddrs
                                                , self.subject, msg)
            chk = apihelper.smtp_mailer(self.mailhost, port, self.username,
                                        self.password, self.fromaddr, self.toaddrs, mime_msg, True)
            if chk > 0:
                self.__mailerror = True
                for handle in self.logger.handlers:
                    # remove the mail handler as it didn't initiate
                    if handle.name == "mailhandler":
                        self.logger.handlers.remove(handle)
                        break
                logger.error("Email not correctly configured.")
            self.buffer = []
