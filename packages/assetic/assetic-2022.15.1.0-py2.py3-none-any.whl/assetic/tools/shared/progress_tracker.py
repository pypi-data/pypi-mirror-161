import logging
from collections import Counter

from assetic.tools.shared import MessagerBase
from assetic.tools.static_def.enums import Result


class ProgressTracker:
    """
    A simple class that accepts result codes from creating/
    updating assets, keeping track of totals, while centralising
    log messages, simplifying individual integration plugins.
    """

    def __init__(self, messager=None):
        self.cnt_pass = 0
        self.cnt_fail = 0
        self.cnt_skip = 0
        self.cnt_part = 0

        self._results = []

        self.logger = logging.getLogger(__name__)  # todo does this work?

        self.messager = messager  # type: MessagerBase

    def add(self, status_code):

        if isinstance(status_code, bool):
            # some old methods still return True, False so this
            # converts bools to the appropriate status codes
            status_code = int(not status_code)

        self._results.append(status_code)

    def calculate(self):
        col = Counter(self._results)
        self.cnt_pass = col[Result.SUCCESS]
        self.cnt_fail = col[Result.FAILURE]
        self.cnt_skip = col[Result.SKIP]
        self.cnt_part = col[Result.PARTIAL]

    def clear(self):
        self.cnt_pass = 0
        self.cnt_fail = 0
        self.cnt_skip = 0
        self.cnt_part = 0

    def _display_summary(self, action, lyrname):

        msg = self.prepare_summary_string(action, lyrname)
        if self.cnt_fail > 0:
            self.logger.warning(msg)
        else:
            self.logger.info(msg)

        self.messager.new_message(msg)

        return msg

    def display_asset_creation_summary(self, lyrname):
        return self._display_summary("creation", lyrname)

    def display_functional_location_creation_summary(self, lyrname):
        return self._display_summary("functional location creation", lyrname)

    def display_asset_update_summary(self, lyrname):
        return self._display_summary("update", lyrname)

    def display_functional_location_update_summary(self, lyrname):
        return self._display_summary("functional location update", lyrname)

    def display_row_progress(self, lyrname, rownum, total_rows):
        msg = ("Updating Assets for layer {0}. "
               "Processing feature {1} of {2}".format(
            lyrname, rownum + 1, total_rows))

        self.logger.debug(msg)
        self.messager.new_message(msg)

    def prepare_summary_string(self, action, lyrname):
        """
        Prepare a string with the summary of success, fail, skip etc
        param action: The action such as 'create' or 'functional location
        create' which is substituted into the heading
        param lyrname: the name of the layer to include in the header
        returns: a formatted string over multiple lines
        """
        msg = """
            Asset {0} summary for layer {1}:

            Success:            {2}
            Partial Success:    {3}
            Skipped:            {4}
            Failure:            {5}
        """.format(action, lyrname, self.cnt_pass,
                   self.cnt_part, self.cnt_skip, self.cnt_fail)
        return msg
