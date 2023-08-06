"""
field_calculations.py
custom methods that apply calculations for the given inputs
Usually this will be overloaded with static functions
"""
import logging


class CalculationTools(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._error = None

    @property
    def error(self):
        return self._error

    @error.setter
    def error(self, value):
        self._error = value

    def run_calc(self, calc_method, input_fields, row, layer_name):
        """
        Runs the given static method within this class having first created
        a dictionary of values from the source row and calculation field list
        :param calc_method: The static method to execute
        :param input_fields: The fields the static method needs
        :param row: The data row from the GIS dictionary
        :param layer_name: The name of the layer being processed
        :return: The method response or None if method raised exception
        """
        # execute the method name passed in
        try:
            return eval("self.{0}(row, input_fields, layer_name)".format(
                calc_method))
        except ValueError as ex:
            self.logger.error(ex)
            return None
        except Exception as ex:
            self.logger.error("Error executing custom method: {0}".format(ex))
            return None
