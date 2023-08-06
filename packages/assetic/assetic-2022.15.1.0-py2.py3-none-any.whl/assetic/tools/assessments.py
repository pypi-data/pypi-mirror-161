# coding: utf-8

"""
    assetic.AssessmentHelper
    assetic.AssessmentFormCreateRepresentation
    assetic.AssessmentTools
    Tools to assist with using Assetic API's for assessments
"""
from __future__ import absolute_import

from ..api_client import ApiClient
from ..rest import ApiException

from ..api import AssessmentFormApi
from ..api import AssessmentTaskApi
from ..api import AssessmentFormResultApi
from ..api import AssessmentProjectApi
from .apihelper import APIHelper

from ..models.assessment_form_page_representation\
    import AssessmentFormPageRepresentation
from ..models.assessment_form_tab_representation\
    import AssessmentFormTabRepresentation
from ..models.form_layout_representation\
    import FormLayoutRepresentation
from ..models.form_layout_pattern_representation\
    import FormLayoutPatternRepresentation
from ..models.form_widget_representation\
    import FormWidgetRepresentation
from ..models.form_control_group_representation\
    import FormControlGroupRepresentation
from ..models.form_control_representation\
    import FormControlRepresentation
from ..models.form_control_combobox_item_representation\
     import FormControlComboboxItemRepresentation

import uuid  #use to generate unqiue ID's for controls
import re   #to replace camelcase with spaced label
import six  #different file open between py2 and py3
import csv  #for helper that reads form structure from csv
from pprint import pformat  #for printing representation
import operator
import os
import sys

class AssessmentHelper(object):
    """
    Class to manage simplified processes for assessment forms
    Uses the AssessmentTools class
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger

        self.assesstool = AssessmentTools()
        self._control_types = self.initiate_control_types()
        self.apihelper = APIHelper()

        # a list of the combbox controls to allow referencing by child items
        self._comboboxes = list()
        self._comboboxrelations = list()

    @property
    def control_types(self):
        """
        dictionary of control type.  The dictionary values can be changed
        to match the source data.  The corresponding keys are tested for when
        determine which control to create
        """
        return self._control_types
    @control_types.setter
    def control_types(self,control_types):
        self._control_types = control_types    
   
    def create_form_from_csv(self,form_repr,csvfile,structure=None):
        """
        create an assessment form from a csv file definition
        :param form_repr: A representation containing the core form
        creation details. AssessmentFormCreateRepresentation
        :param csvfile: The file containing the form definition
        :param structure: an optional mapping of row number in csv file to
        form creation purpose.  e.g row 1 = control header, row 2 = control type
        :returns: >0=error, 0 = Success
        """

        form_name = form_repr.form_name
        if form_repr.form_label == None:
            form_label = form_repr.form_name
        else:
            form_label = form_repr.form_label
        form_level = form_repr.form_level
        version = form_repr.version
        can_add_attachment = form_repr.can_add_attachment
        tab_label = form_repr.tab_label
        layout_pattern = form_repr.layout_pattern
        widget_labels = form_repr.widget_labels
        label_formatter = form_repr.label_formatter
        # first create the form definition
        form = self.assesstool.new_form(form_name,form_level,form_label)
        # create tab and widgets
        tab = self.assesstool.add_tab_with_widgets_to_form(form,tab_label,
                    widget_labels,layout_pattern)
        if tab is None:
            # error encountered
            self.logger.error("Tab could not be created")
            return 1

        # get the structure from csv
        rows = self.read_csv_file_into_dict(csvfile,structure)
        if len(rows) == 0:
            self.logger.warning("No rows returned by csv reader")
            return 1

        # Add the controls to the payload
        count = 0
        for row in rows:
            self.logger.debug("Process row label '{0}'".format(row["Label"]))
            chk = self.process_csv_dict_row(row,tab,widget_labels,count,
                                      label_formatter)
            if chk > 0:
                return 1
            count += 1
        # now create form
        self.logger.debug("Ready to create Form:\n{0}".format(form))
        newformid = self.assesstool.create_form(form)
        if newformid.lower() != form_name.lower():
            return newformid
        if len(self._comboboxrelations) > 0:
            # need to update form with child - get form
            savedform_json = self.assesstool.get_form(newformid)
            try:
                savedform = self.api_client.deserialize(
                    savedform_json, "AssessmentFormPageRepresentation")
            except ValueError as ex:
                self.logger.error("Unable to deserialise new form {0} in "
                                  "preparation for applying parent child "
                                  "lookup relationships".format(form_name))
                return 1

            for relationdef in self._comboboxrelations:
                parent_label = relationdef["parent_control"]
                relationstring = relationdef["relation"]
                child_label = relationdef["child_control"]
                chk = self.set_child_combobox_parent(
                    parent_label=parent_label, relationstring=relationstring
                    , child_label=child_label, form_def=savedform)
                if chk !=0:
                    return chk
            # now update form
            if not savedform.attached_documents:
                savedform.attached_documents = []
            chk = self.assesstool.update_form(savedform)
            return chk


    
    def read_csv_file_into_dict(self,filename,structure=None):
        """
        Read the the contents of a csv file into a representation that can be
        used to build the controls on a form
        :param filename: the file to read
        :param structure: the layout mapping of the rows in the file
        :returns: a list of dictionary objects that match the input structure
        """
        if structure == None:
            structure =  ("Label")

        rows = list()
        if six.PY2:
            self.logger.debug("Reading file")
            with open(filename, 'rt') as csvfile:
                readCSV = csv.DictReader(
                            csvfile,fieldnames=structure,delimiter=',')            
                for row in readCSV:
                    rows.append(row)
        else:
            try:
                self.logger.debug("Reading file with UTF-8 encoding")
                with open(filename, 'rt', encoding='utf-8', newline = '') \
                as csvfile:
                    readCSV = csv.DictReader(csvfile,fieldnames=structure,
                                         delimiter=',')            
                    for row in readCSV:
                        rows.append(row)
            except UnicodeDecodeError:
                self.logger.debug("Try reading file without UTF-8 encoding")
                with open(filename, 'rt', newline = '') as csvfile:
                    readCSV = csv.DictReader(csvfile,fieldnames=structure,
                                         delimiter=',')            
                    for row in readCSV:
                        rows.append(row)
        self.logger.debug("Found {0} rows in csv file".format(len(rows)))
        return rows

    def process_csv_dict_row(self,field_def,tab,widget_labels, order
                             ,label_formatter = None):
        """
        The field definition is from csv.DictReader.
        Look for specific headers to determine
        what kind of control to create and it's attributes.
        :param field_def: the dictionary for a field
        :param tab: the tab to add the control to
        :param widget_labels: the widget to add the control to
        must be in the tab
        :param order: the order of the widget
        :param label_formatter: optional python method to modify the label.
        Useful for converting to tile case or split camel case
        example: str.title or the helper method insert_space_in_camelcase
        :returns: a list of the representation
        FormControlRepresentation()
        """
        label = None
        if "Label" in field_def:
            label = field_def["Label"]
        else:
            # assume first element is the label
            label = field_def[0]
        if label_formatter is not None:
            try:
                label = label_formatter(label)
            except Exception as ex:
                msg = "Label formatter could not be applied: {0}".format(ex)
                self.logger.warning(msg)
        # check if hint for control but otherwise leave null
        hint = None
        if "Hint" in field_def:
            hint = field_def["Hint"]
        # check if name for control but otherwise leave null
        name = None
        if "Name" in field_def:
            name = field_def["Name"]

        # check if 'required' is set
        required = False
        if "Required" in field_def and field_def["Required"] is not None:
            if field_def["Required"] == 1 or \
            field_def["Required"].lower() == "true" or \
            field_def["Required"].lower() == "yes":
                field_def["Required"] = True
            required = field_def["Required"]
        if not isinstance(required, bool):
            required = False
        # check if widget is defined.  If not set as first label
        widget_label = widget_labels[0]
        if "Widget" in field_def and field_def["Widget"] in widget_labels:
            widget_label = field_def["Widget"]

        # now test for type and create control
        control = None
        if "Type" not in field_def:
            # assume text box
            field_def["Type"] = "textbox"
        if "Type" in field_def:
            if field_def["Type"].lower() == \
                   self._control_types["TextBox"].lower():
                # Standard text box
                # get length
                length = 200  # Default field length(will be used if undefined)
                if "Length" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Length"],200)
                elif "Attributes" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Attributes"],200)
                control = self.assesstool.new_text_control(
                    label, name, length, hint=hint,required=required
                    , order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["MultiLineText"].lower():
                # this is a multiline text box
                length = 1000  # Default field length(will be used if undefined)
                if "Length" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Length"],1000)
                elif "Attributes" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Attributes"],1000)
                control = self.assesstool.new_multiline_text_control(
                    label, name, length, hint=hint, required=required
                    , order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["Dropdown"].lower():
                # this is a combobox (drop down list)
                # get items
                itemstring = None
                if "DropdownItems" in field_def:
                    itemstring = field_def["DropdownItems"]
                elif "Attributes" in field_def:
                    itemstring = field_def["Attributes"]
                item_delim=";"  #hardcode delimiter for the moment
                key_value_delim="|"  #hardcode delimiter for the moment
                items = self.get_combobox_items(
                                itemstring,item_delim,key_value_delim)
                control = self.assesstool.new_combobox_control(
                    label, name, items=items, hint=hint, required=required
                    , order=order)

                # is there a parent defined for this combobox
                if "ParentLabel" in field_def and \
                        "ParentRelation" in field_def and \
                        field_def["ParentLabel"] and \
                        field_def["ParentRelation"]:
                    # record the relation to use later in a form update
                    relation = {
                        "child_control": control.label
                        , "parent_control": field_def["ParentLabel"]
                        , "relation": field_def["ParentRelation"]
                    }
                    self._comboboxrelations.append(relation)

                # append the comboxbox to a list in case a child needs to
                # reference
                self._comboboxes.append(control)
            elif field_def["Type"].lower() == \
                    self._control_types["Date"].lower():
                # this is a date picker
                control = self.assesstool.new_date_control(
                    label, name, hint=hint, required=required, order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["DateTime"].lower():
                # this is a date picker
                control = self.assesstool.new_datetime_control(
                    label, name, hint=hint, required=required, order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["NumericStepper"].\
                                         lower():
                # this is a numeric stepper
                # get items
                sdef = self.get_stepper_defs(field_def)
                control = self.assesstool.new_stepper_control(
                    label, name, sdef["minval"], sdef["maxval"]
                    , sdef["increment"], mask=sdef["valueformat"], hint=hint
                    , required=required, order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["CheckBox"].lower():
                # this is a checkbox
                control = self.assesstool.new_checkbox_control(
                    label, name, hint=hint, required=required, order=order)
            elif field_def["Type"].lower() == \
                     self._control_types["Map"].lower():
                # this is a map control
                control = self.assesstool.new_map_control(
                    label, name, hint=hint, required=required, order=order)
            else:
                # Assume text
                # Default field length(will be used if undefined)
                length = 200
                if "Length" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Length"], 200)
                elif "Attributes" in field_def:
                    length = self.get_numeric_or_default(
                                field_def["Attributes"], 200)
                control = self.assesstool.new_text_control(
                    label, name, length, hint=hint, required=required
                    , order=order)
        # Add the control definition to the tab
        if control is not None:
            self.assesstool.add_control_to_tab_widget(
                tab, widget_label, control)
            return 0
        else:
            msg = "Aborting due to invalid field definition for control {0}" \
                  "".format(field_def)
            self.logger.error(msg)
            return 1

    def get_combobox_items(self,itemstring,item_delim=";",key_value_delim="|"):
        """
        given a string decode into a list of key/value pairs and create
        combobox items.
        By default key/value pairs are separated by ";"
        By default "|" for splitting key from value 
        If only value supplied then key = value
        :param itemstring: the string containing key/value pairs
        :param item_delim: delimiter between each set of items (key/value pairs)
        Default = ";"
        :param key_value_delim:delimiter between key and value. default = "|"
        :returns: a list of combobox item representations
        FormControlRepresentation
        """
        items = list()
        if itemstring == None or itemstring.strip() == "":
            # no lookups items defined
            self.logger.debug("No combobox items defined")
            return items

        # split into key/value pairs
        pairs = itemstring.split(item_delim)
        for counter, kvp in enumerate(pairs):
            # split key and value
            if kvp.strip() == "":
                # no data, perhaps a trailing delimiter in itemstring
                pass
            else:
                itemkvp = kvp.split(key_value_delim)
                if len(itemkvp) == 1:
                    # only one definition
                    # itemkvp.append(kvp)
                    itemkvp.append(None)
                    # Label is minimum requirement
                    itemkvp = itemkvp.reverse()
                if itemkvp[0].strip() == "" and itemkvp[1].strip() != "":
                    # make sure key is None rather than empty string
                    itemkvp[0] = None
                if itemkvp[1].strip() == "" and itemkvp[0].strip() != "":
                    # make sure label is set rather than value
                    itemkvp[1] = None
                    itemkvp = itemkvp.reverse()

                # add item representation to items list
                new_item = self.assesstool.new_combobox_item(
                    itemkvp[1], itemkvp[0], order=counter)
                items.append(new_item)

        if len(items) == 0:
            msg = "No combobox items created for itemstring [{0}]".format(
                itemstring)
            self.logger.debug(msg)
        return items

    def set_child_combobox_parent(self, form_def, parent_label, relationstring,
                                  child_label, item_delim="|",
                                  parent_delim=";", config_delim="^^"):
        """
        For the given comobox control definition, associate the items with a
        parent item(s) defined by rhe relationstring that needs to be decoded
        It requires the 'value' of a combobox item to be matched to the
        'value' of the parent combobox item (not the user visible 'labels'
        in the combobox
        :param form_def: the form definition to update
        :param parent_label: the label defined for the parent combobox
        :param relationstring: the string containing relationship between
        the child item id and the parent item ids  e.g. '1|1;2^^2|3;4'
        :param child_label: the label for the child combobox.  This
        is used to get the control to update
        :param item_delim: By default "|" for splitting each child item val
        from parent list
        :param parent_delim: By default parent values are separated by ";"
        :param config_delim: By default "^^" for splitting each item config
        :returns: 0=success, else error.  Updates child_control by reference
        """

        # find the parent and child controls from the form
        parent_control = None
        child_control = None
        for widget in form_def.form_tabs[0].form_layout.widgets:
            for control in widget.form_control_group.form_controls:
                if control.label == parent_label:
                    parent_control = control
                if control.label == child_label:
                    child_control = control
                if parent_control and child_control:
                    break

        if not parent_control:
            self.logger.warning(
                "Unable to find parent comboxbox control {0}".format(
                    parent_label
                ))
            return 0
        if not child_control:
            self.logger.warning(
                "Unable to find child comboxbox control {0}".format(
                    child_label
                ))
            return 0

        configs = relationstring.split(config_delim)
        for config in configs:
            # split the child item value from the parent item values
            item_config = config.split(item_delim)
            if len(item_config) != 2:
                # No parents or poorly defined so skip
                self.logger.warning(
                    "Ignoring invalid combobox parent config: {0}".format(
                        item_config))
                continue

            # get the parent values we will use to find parent control
            parent_ids = item_config[1].split(parent_delim)

            # get the child control
            # get the child item from the control using the value
            for item in child_control.combobox_items:
                tmp_list = list()
                if item.value == item_config[0]:
                    # we have the control so get the parent
                    for parent_id in parent_ids:
                        for p_item in parent_control.combobox_items:
                            if parent_id == p_item.value:
                                tmp_list.append(p_item.id)
                                break
                if len(tmp_list) > 0:
                    #for item_upd in child_control.combobox_items:
                    #    if item_upd.id == item.id:
                    #item.form_control_cb_item_parent_id = tmp_list
                    item.parent_item_ids = tmp_list
                    child_control.form_control_parent_name = \
                        parent_control.name

        for widget in form_def.form_tabs[0].form_layout.widgets:
            for control in widget.form_control_group.form_controls:
                if control.label == parent_label:
                    control = parent_control
                if control.label == child_label:
                    control = child_control
                if parent_control and child_control:
                    break
        return 0

    def get_stepper_defs(self,field_def):
        """
        given a form field configuration definition, test if there are settings
        for a numeric stepper 
        :param field_def: the dictionary of settings to test
        :returns: a dictionary of the parameters and their value
        """
        attributes_delim="|"  #hardcode attributes delimiter for the moment
        default_min = 0
        default_max = 0
        default_inc = 0
        default_format = "n0"
        stepperdict = dict()
        ##apply defaults and then override if there is a setting
        stepperdict["minval"] = default_min
        stepperdict["maxval"] = default_max
        stepperdict["increment"] = default_inc
        stepperdict["valueformat"] = default_format
        
        #First look for separately defined parameters
        useatts = True  #flag to indicate use of generic attributes field
        if "MinValue" in field_def:
            stepperdict["minval"] = field_def["MinValue"]
            useatts = False
        if "MaxValue" in field_def:
            stepperdict["maxval"] = field_def["MaxValue"]
            useatts = False
        if "ValueIncrement" in field_def:
            stepperdict["increment"] = field_def["ValueIncrement"]
            useatts = False
        if "ValueFormat" in field_def:
            stepperdict["valueformat"] = field_def["ValueFormat"]
        #If useatts = True set then look for delimited 'Attributes' and split
        if useatts == True and "Attributes" in field_def and \
        field_def["Attributes"] != None:
            stepperdefs = field_def["Attributes"].split(attributes_delim)
            stepperdict["minval"] = self.get_numeric_or_default(
                                            stepperdefs[0],default_min)
            if len(stepperdefs) > 1:
                stepperdict["maxval"] = self.get_numeric_or_default(
                                            stepperdefs[1],1000)
            if len(stepperdefs) > 2:
                stepperdict["increment"] = self.get_numeric_or_default(
                                            stepperdefs[2],1)
            if len(stepperdefs) > 3:
                stepperdict["valueformat"] = stepperdefs[3]  

        return stepperdict
        
    
    def get_numeric_or_default(self,value,default):
        """
        given a string, test if numeric and if not return default
        :param value: the string to test
        :param default: the default vaue.Must be a numeric (is not validated)
        :returns: the reformatted value as a numeric
        """
        if value == None or value.strip() == "":
            return default
        
        try:
            numeric = int(float(value))
        except Exception as ex:
            msg = "Could not convert {0} to integer. "\
                  "Using default instead".format(str(value))
            self.logger.warning(msg)
            numeric = default
        return numeric
        
    def insert_space_in_camelcase(self,value):
        """
        given a string, insert a space in from of upper case characters
        or numbers.
        Use to make a user presentable label
        :param value: the string to operate on
        :returns: the reformatted string
        """
        result = value
        try:
            result = re.sub('([A-Z]{1})', r' \1',value).strip().strip("_")
        except Exception as ex:
            msg = "Could not convert camelcase: {0}".format(str(ex))
            self.logger.warning(msg)            
        return result

    def initiate_control_types(self):
        """
        initiate a dictionary of control type names with default values.
        :returns: dictionary of supported control types
        """
        control_types = dict()
        control_types["TextBox"] = "TextBox"
        control_types["MultiLineText"] = "MultiLineText"
        control_types["Dropdown"] = "Dropdown"
        control_types["Date"] = "Date"
        control_types["DateTime"] = "DateTime"
        control_types["NumericStepper"] = "NumericStepper"
        control_types["CheckBox"] = "CheckBox"
        control_types["Map"] = "Map"
        return control_types

    def user_input(self,message):
        """
        prompt user for input.
        :returns: user input string
        """
        if six.PY3:
            return str(input(message))
        else:
            return str(raw_input(message))

    def assessment_form_create_prompter(self):
        """
        prompt user for the required information to create a form.
        :returns: success =0 else error number
        """
        self.logger.debug("Initiating Form Create Prompter")
        print("************************************************")
        print("Create Assessment Form")
        print("The tool creates an Assessment Form using the")
        print("configuration information in a csv file plus some")
        print("initial prompts by this tool")
        print("************************************************")

        #get the csv file location
        print(" ")
        print("************************************************")
        msg = "Enter the name and location of the csv file: "
        csvfile = self.user_input(msg)
        if len(csvfile) > 0:
            if os.path.isfile(csvfile) == False:
                print("csv file not found - Exiting form create")
                return None
        else:
            return None
 
        form_repr = AssessmentFormCreateRepresentation()

        #get the form label
        form_repr.form_label = self.user_input("Enter Form Label: ")
        if form_repr.form_label == "":
            print("Label Required - Exiting form create")
            return None

        ##Get a name for the form
        name = form_repr.form_label.replace(" ","")
        msg = "Enter form Name (or 'Enter' to use '{0}'): ".format(name)
        form_repr.form_name = self.user_input(msg)
        if form_repr.form_name == "":
            form_repr.form_name = name

        ##get form level
        form_repr.form_level = self.get_form_level()

        ##get tab name
        print(" ")
        print("************************************************")
        msg = "Enter a label for the tab  (or 'Enter' to use 'Assessment'): "
        form_repr.tab_label = self.user_input(msg)
        if form_repr.tab_label == "":
            form_repr.tab_label = "Assessment"

        #structure (column order) of csv file
        csv_structure = self.get_column_purpose_structure()

        ##get pattern
        form_repr.layout_pattern = self.get_pattern()

        ##get widget labels
        bgot_settings = False
        typelist = list()
        widgets = list()
        if "Widget" in csv_structure:
            ##get list of widgets from csv
            widgetlist,typelist = self.get_settings_in_csv(csvfile,
                                                           csv_structure)
            bgot_settings= True
            if len(widgetlist) > 0:
                widgets = widgetlist
        else:
            ##prompt for widget name
            print(" ")
            print("************************************************")
            msg = "Enter the label for the group control:"
            widget = self.user_input(msg)
            if widget != "":
                widgets.append(widget)
        if len(widgets) == 0:
            widgets.append("Data")
        form_repr.widget_labels = widgets

        ##add attachments?
        form_repr.can_add_attachment == True
        print(" ")
        print("************************************************")
        attach = self.user_input("Allow attachments Y or N (default = Y): ")
        if attach.upper() == "N":
            form_repr.can_add_attachment = False

        ##custom control type names
        if bgot_settings == False and "Type" in csv_structure:
            widgetlist,typelist = self.get_settings_in_csv(csvfile,
                                                           csv_structure)
        if len(typelist) > 0:
            ##check if any non-standard types and prompt user to correct
            self.control_types = self.get_control_types(self.control_types,
                                                        typelist)

        self.logger.debug("Form Representation:\n{0}".format(form_repr))
        self.logger.debug("CSV Structure:\n{0}".format(csv_structure))
        self.logger.debug("Control Types:\n{0}".format(self.control_types))
        ##create the form
        try:
            result = self.create_form_from_csv(form_repr,csvfile,csv_structure)
        except Exception as ex:
            self.user_input(
                "Error encountered. {0} Press enter to close:".format(
                    str(ex)))
            result = 1
            
        if result == 0:
            chk = self.user_input("Created form. Open form in Assetic? (Y/N):")
            if chk.upper() == "Y":
                self.apihelper.launch_assetic_assessment_form_admin(
                    form_repr.form_name)

        return result

    def get_settings_in_csv(self,csvfile,csv_structure):
        """
        given the csv structure, get a list of widgets and control types
        that the user has set (they may not be defined..
        :returns tuple of lists
        """
        widgets = list()
        types = list()
        
        rows = self.read_csv_file_into_dict(csvfile,csv_structure)
        for row in rows:
            if "Widget" in row:
                if row["Widget"] not in widgets and row["Widget"] != "":
                    widgets.append(row["Widget"])
            if "Type" in row:
                if row["Type"] not in types and row["Type"] != "":
                    types.append(row["Type"])

        return widgets,types
        

    def get_column_purpose_structure(self):
        """
        Present a list of column purpose names
        :returns dictionary of column purposes with description
        """
        purpose = dict()
        purpose["Label"] = "The label the user sees for the form field"
        purpose["Name"] = "The reference name to give the form field.\n" \
                          "Use if linking to another system."
        purpose["Hint"] = "A tooltip style hint for the form field"
        purpose["Required"] = "Indicate if the form field is mandatory or not"
        purpose["Widget"] = \
            "The Group Control that the form field is assigned to.\n" \
            "Values in this column match the Group Control Names entered above"
        purpose["Type"] = \
            "The control type. Values in this column match the \n" \
            "control names entered above"
        purpose["Attributes"] = \
            "Attributes of the control such as length,dropdown \n" \
            "items, stepper settings"
        purpose["Length"] = \
            "Field length (if not using 'Attributes' column)"
        purpose["DropdownItems"] = \
            "Dropdown items (if not using 'Attributes' column)"
        purpose["MinValue"] = \
            "Stepper minimum value (if not using 'Attributes' column"
        purpose["MaxValue"] = \
            "Stepper maximum value (if not using 'Attributes' column"
        purpose["ValueIncrement"] = \
            "Stepper increment (if not using 'Attributes' column"
        purpose["ValueFormat"] = \
            "Stepper display format (if not using 'Attributes' column"
        purpose["ParentLabel"] = \
            "The label of a parent combobox if there is one"
        purpose["ParentRelation"] = \
            "The relationship between child comboxbox items and the parent " \
            "combobox items"
        #use purposekeys to check user entry
        purposekeys = set(purpose)

        ##list options and prompt user
        print(" ")
        print("************************************************")
        print("csv column order - column purpose names (Name plus Description).")
        for k,v in six.iteritems(purpose):
            print("{0:16} {1}".format(str(k) + ".",v))
        print(" ")

        cnt = 0
        while True:
            #run as a loop to allow retries
            msg = "Enter the column purpose names from above in the csv file.\n"\
                  "e.g.:Label,Type,Attributes,Widget,Required,Hint\n"\
                    "Separate with commas (case sensitive)):"
            corder = self.user_input(msg)
            if corder == "":
                corder = "Label"
            csv_structure = corder.replace(" ","").split(",")
            chkorder = set(csv_structure)
            if not chkorder.issubset(purposekeys):
                diff = str(chkorder.difference(purposekeys))
                print("{0} are not valid column names.  Please retry".format(diff))
            else:
                break
            ##avoid an endless loop
            if cnt >5:
                print("Using default.  First column is label")
                csv_structure = ("Label",)
                break
            cnt = cnt + 1
        #make sure its a tuple
        csv_structure = tuple(csv_structure)
        return csv_structure
      
    def get_form_level(self):
        """
        Present a list of form levels to use and prompt them to choose one
        Will default to the basic "Asset" pattern if selection not entered
        or out of range
        :returns form level
        """
        default = 1
        form_levels = sorted(self.assesstool.form_levels)
        form_levelslen = len(form_levels)
        print(" ")
        print("************************************************")
        print("Assessment Form Levels")
        for x in range(1,len(form_levels)+1):
            print("{0:5} {1}".format(str(x)+".",form_levels[x-1]))
            if form_levels[x-1] == "Asset":
                default = x
        print(" ")
        msg = "Enter the number (1 to {0}) of the form level (default=Asset): "\
                    "".format(form_levelslen)
        form_levelsnum = self.user_input(msg)
        if form_levelsnum == "":
            form_levelsnum = default
        try:
            form_levelsnum = int(form_levelsnum)
        except:
            form_levelsnum = default
        if form_levelsnum > 0 and form_levelsnum < form_levelslen + 1:
            return form_levels[form_levelsnum-1]
        else:
            return form_levels[default-1]

    def get_pattern(self):
        """
        Present a list of patterns to use and prompt them to choose one
        Will default to the basic "Single" pattern if selection not entered
        or out of range
        :returns pattern name
        """
        ##get the list of patterns (sort list by id) and present to user
        patterns = sorted(six.iteritems(self.assesstool.layout_patterns),
                                            key=operator.itemgetter(1))
        patternlen = len(patterns)
        print(" ")
        print("************************************************")
        print("Form Layout Patterns")
        for row in patterns:
            print("{0:5} {1}".format(str(row[1])+".",row[0]))
        print(" ")
        msg = "Enter the number (1 to {0}) of the form layout (default=1): ".format(
                      patternlen)
        layoutnum = self.user_input(msg)
        if layoutnum == "":
            layoutnum = 1
        try:
            layoutnum = int(layoutnum)
        except:
            layoutnum = 1
        if layoutnum > 0 and layoutnum < patternlen + 1:
            return patterns[layoutnum-1][0]
        else:
            return patterns[0][0]

    def get_control_types(self,control_types,typelist):
        """
        Present a list of standtard control type names.  Prompt user to enter
        variants if they have called it something differen
        :returns dictionary of standard names as key, and user name as value
        """
        printed_defaults = False
        lower_types = set(k.lower() for k in control_types)
        for k in typelist:
            if k.lower() not in lower_types:
                if printed_defaults == False:
                    print("************************************************")
                    print("Standard Form Field Type Names")        
                    for k,v in sorted(six.iteritems(control_types)):
                        print(k)
                    print(" ")
                    printed_defaults = True
                msg = "Enter the standard name from the list above for the "\
                      "field type '{0}': ".format(k)
                custom = self.user_input(msg)
                if custom != "" and custom in control_types:
                    control_types[custom] = k
                else:
                    msg = "{0} is not in the list above. 'TextBox' will be "\
                          "used for {0})".format(custom,k) 
        return control_types

        
class AssessmentFormCreateRepresentation(object):
    """"
    A structure for defining table metadata and relationships between
    search profile names, id's and tables
    Used by AssessmentHelper.
    """
    def __init__(self,form_name=None,form_label=None,form_level=None,version=1,can_add_attachment=True,tab_label="Tab",layout_pattern="Single",widget_labels=["Data"],label_formatter=None):
        """
        AssessmentFormCreateRepresentation - a model defining the core form
        details - form, tab, layoutpattern, control group labels.
        Used by AssessmentHelper.create_form_from_csv
        """
        self.fieldtypes = {
            "form_name": "str",
            "form_label": "str",
            "form_level": "str",
            "version": "int",
            "can_add_attachment": "bool",
            "tab_label":"string",
            "layout_pattern":"string",
            "widget_labels":"list[str]",
            "label_formatter": "string"
        }
        self._form_name = form_name
        self._form_label = form_label
        self._form_level = form_level
        self._version = version
        self._can_add_attachment = can_add_attachment
        self._tab_label = tab_label
        self._layout_pattern = layout_pattern
        if widget_labels == None:
            widget_labels = []
        self._widget_labels = widget_labels
        self._label_formatter = label_formatter
        
    @property
    def form_name(self):
        return self._form_name
    @form_name.setter
    def form_name(self,form_name):
        self._form_name = form_name
    
    @property
    def form_label(self):
        return self._form_label
    @form_label.setter
    def form_label(self,form_label):
        self._form_label = form_label

    @property
    def form_level(self):
        return self._form_level
    @form_level.setter
    def form_level(self,form_level):
        self._form_level = form_level

    @property
    def version(self):
        return self._version
    @version.setter
    def version(self,version):
        self._version = version

    @property
    def can_add_attachment(self):
        return self._can_add_attachment
    @can_add_attachment.setter
    def can_add_attachment(self,can_add_attachment):
        self._can_add_attachment = can_add_attachment

    @property
    def tab_label(self):
        return self._tab_label
    @tab_label.setter
    def tab_label(self,tab_label):
        self._tab_label = tab_label

    @property
    def layout_pattern(self):
        return self._layout_pattern
    @layout_pattern.setter
    def layout_pattern(self,layout_pattern):
        self._layout_pattern = layout_pattern

    @property
    def widget_labels(self):
        return self._widget_labels
    @widget_labels.setter
    def widget_labels(self,widget_labels):
        self._widget_labels = widget_labels

    @property
    def label_formatter(self):
        return self._label_formatter
    @label_formatter.setter
    def label_formatter(self,label_formatter):
        self._label_formatter = label_formatter
                              
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
    
class AssessmentTools(object):
    """
    Class to simplify and manage interface with assessment form APIs
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        
        self.logger = api_client.configuration.packagelogger

        self.formapi = AssessmentFormApi()
        self.taskapi = AssessmentTaskApi()
        self.resultapi = AssessmentFormResultApi()
        self.projectapi = AssessmentProjectApi()
        
        self._layoutpatterns = self.set_layout_pattern_dict()
        self._formlevels = ["Asset", "GroupAsset", "ComplexAsset",
                "Component", "ComponentServiceCriteria","NetworkEntity",
                "SimpleAsset", "WorkOrder", "WorkRequest", "WorkTask",
                "AssesmentsResult", "Documents", "AsmtProject", "AsmtTask",
                "ServiceCriteria"]


    @property
    def layout_patterns(self):
        """
        dictionary of layout patterns where the key is the description
        and the value is the ID.  Need the ID when creating a form.
        """
        return self._layoutpatterns

    @property
    def form_levels(self):
        """
        List of valid form associations to assetic module types.
        """
        return self._formlevels
    
    def create_form(self,form):
        """
        create an assessment form
        :param form: The complete form representation
        AssessmentFormPageRepresentation
        :returns: >0=error (API status code), 0 = Success
        """
        try:
            response = self.formapi.assessment_form_add_form(form)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status,e.reason,e.body))
            return e.status
        return response

    def get_form(self, form_id):
        """
        create an assessment form
        :param form_id: Get the form from API using form id
        :returns: >0=error (API status code), 0 = Success
        """
        try:
            response = self.formapi.assessment_form_get(form_id)
        except ApiException as e:
            self.logger.error("Status {0}, Reason: {1} {2}".format(
                e.status, e.reason, e.body))
            return e.status
        return response

    def update_form(self, form):
        """
        update an assessment form
        :param form: The complete form representation
        AssessmentFormPageRepresentation
        :returns: >0=error (API status code), 0 = Success
        """
        try:
            response = self.formapi.assessment_form_update_form(
                form_representation=form, id=form.name)
        except ApiException as e:
            self.logger.error(
                "Unable to update form, Status {0}, Reason: {1} {2}".format(
                    e.status, e.reason, e.body))
            return e.status
        return response

    def new_form(self,form_name,form_level,label,version=1,can_add_attachment=True,tabs=None,attached_documents=None):
        """
        define an instance of a form page.  This is the highest level of the
        form definition    
        :param form_name: The name of the form.  Mandatory  
        :param form_level: form against an 'Asset' or...  Mandatory
        :param label: short description of form.  Will use 'form_name' if None
        :param version: version number
        :param can_add_attachement: boolean.  Default = True
        :param tabs: list of tab controls to add to form. 
        :param attached_documents: list of document objects to attach to form
        :returns: form pageinstance
        AssessmentFormPageRepresentation()
        """
        #validate some of the mandatory fields 
        if form_level not in self.form_levels:
            self.logger.error("Valid form_level required.  Current value is [{0}]".format(
                form_level))
            return None      
        
        #instance of form page
        form = AssessmentFormPageRepresentation()
        form.name = form_name
        if label == None:
            label = form_name
        form.label = label
        form.applicable_level_name = form_level
        form.version = version
        if tabs == None:
            form.form_tabs = []
        else:
            form.form_tabs = tabs
        form.can_add_attachment = can_add_attachment
        if attached_documents == None:
            form.attached_documents = []
        else:
            form.attached_documents = attached_documents
        return form

    def add_tab_with_widgets_to_form(self,form,tab_label,widgetlabels,pattern_name="Single",visible=True,taborder=None,collapsed=False):
        """
        create an instance of a tab definition including the layout pattern
        within group control and widgets within the tab form layout
        The new tab will be added to the form.
        Widgets are then added to the tab
        :param form: the form representation to add the tab to.  Of type
        AssessmentFormPageRepresentation()
        :param tab_label: The user visible label of the tab.  Mandatory
        :param widgetlabels: List of the user visible widget labels.
        Container order of widgets follows order in list
        :param layoutpattern: The pattern definition for the layout of the
        controls to be placed in the tab.  Default = 'Single'
        :param visible: tab visible True or False.  Default = True
        :param taborder: order number of tab in the form.  Optional.
        :param collapsed: All widgets collapsed or expanded. Default=False
        :returns: tab instance AssessmentFormTabRepresentation()
        """
        #create the tab with it's layout
        tab = self.add_tab_layout_to_form(form,tab_label,pattern_name,visible,
                                          taborder)
        ##loop through the widget label list and add widgets
        containernum = 0
        order = containernum + 1
        for widget_label in widgetlabels:
            widget = self.add_widget_group_control_to_layout(tab,widget_label,
                                    containernum,order,collapsed)
            if widget == None:
                self.logger.debug("Control Group not added to layout")
                return None
            containernum = containernum + 1
            order = containernum + 1            
        return tab
    
    def add_control_to_tab_widget(self,tab,widget_label,control):
        """
        add a control to a widget form_control_group within a tab using the
        widget lable to identify the correct widget
        :param tab: the tab containing the widget.  Of type
        AssessmentFormTabRepresentation()
        :param widget_label: The user visible label of the widget.  Mandatory
        :param control: The control to add to the widget form layout.  Of type
        FormControlRepresentation
        :returns: tab instance AssessmentFormTabRepresentation()
        """
        for widget in tab.form_layout.widgets:
            if widget.label == widget_label:
                if widget.form_control_group != None:
                    if widget.form_control_group.form_controls == None:
                        widget.form_control_group.form_controls = []
                    widget.form_control_group.form_controls.append(control)
                    return True
        self.logger.error("Widget label [{0}] not found in tab [{1}]".format(
                widget_label,tab.label))     
        return False
        
    def add_tab_layout_to_form(self,form,tab_label,pattern_name="Single",visible=True,order=None):
        """
        create an instance of a tab definition including the layout pattern
        The new tab will be added to the form.
        Widgets are then added to the tab
        :param form: the form representation to add the tab to.  Of type
        AssessmentFormPageRepresentation()
        :param tab_label: The user visible label of the tab.  Mandatory
        :param layoutpattern: The pattern definition for the layout of the
        controls to be placed in the tab.  Default = 'Single'
        :param visible: tab visible True or False.  Default = True
        :param order: order number in the form.  Optional.
        :returns: tab instance AssessmentFormTabRepresentation()
        """        
        #create the tab representation
        tab = self.new_tab(tab_label,visible,order)
        #add tab to form
        form.form_tabs.append(tab)
        ##create the layout
        layoutlabel = "layout{0}".format(tab_label)  #label is not user visible 
        layoutname = "L{0}".format(str(uuid.uuid1()))  #generate unique name
        formlayout = self.new_form_layout(layoutname,layoutlabel)
        if formlayout == None:
            return None
        #Add the layout to the form
        tab.form_layout = formlayout

        ##add layout pattern within layout
        pattern = self.new_layout_pattern(self.layout_patterns[pattern_name])
        formlayout.form_layout_pattern = pattern

        return tab

    def add_widget_group_control_to_layout(self,tab,label,containernum,order=None,collapsed=False):
        """
        create an instance of a widget with group control and add to form layout
        a form layout sits within a tab.
        :param tab: the form layout to add the widget to
        :param label: the label the user at the top of the group control
        :param containernum: A layout pattern assigns an incremeting integer
        to each cell in the row/column matrix defined by the pattern.
        The widget will be placed in the cell identified by containernum
        :param collapsed: Is widget collapsed. bool. Default=False
        :param order: order number in the form.  Optional.
        :param form_layout: instance of FormLayoutRepresentation
        :returns: widget control instance AssessmentFormTabRepresentation()
        """
        ##create the widget
        widget = self.new_form_widget(label,containernum,order,collapsed)
        ##add the widget to the tab
        tab.form_layout.widgets.append(widget)
        
        ##now add a control group to the widget
        label = "FCG{0}".format(label)  #label is not user visible
        controlgroup = self.new_form_control_group(label)
        widget.form_control_group = controlgroup
        return widget
        
        
    def new_tab(self,label,visible=True,order=None,form_layout=None):
        """
        create an instance of a tab    
        :param label: control label - the label the user sees next to the text box
        :param visible: tab visible True or False
        :param order: order number in the form.  Optional.
        :param form_layout: instance of FormLayoutRepresentation
        :returns: tab control instance FormTabRepresentation()
        """
        tab = AssessmentFormTabRepresentation()
        tab.label = label
        tab.visible = visible
        tab.sort_order = order
        tab.form_layout = form_layout
        return tab

    def new_form_layout(self,name,label,widgets=None,layoutpattern=None):
        """
        create an instance of a form layout - usually assign to a tab    
        :param label: control label - mandatory
        :param layoutpattern: layout pattern to apply to the form
        :returns: form layout control instance FormLayoutRepresentation()
        """
        try:
            formlayout = FormLayoutRepresentation(label=label)
        except Exception as ex:
            self.logger.error("new_form_layout: {0}".format(str(ex)))
            return None
        if layoutpattern != None:
            formlayout.form_layout_pattern = layoutpattern
        formlayout.name = name
        if widgets == None:
            formlayout.widgets = []
        else:
            formlayout.widgets = widgets
        return formlayout

    def new_layout_pattern(self,patternid):
        """
        create an instance of a form layout pattern - assign to a form layout
        :param patternid: The integer ID of the layout pattern between 1 & 25
        :returns: form layout pattern instance
        FormLayoutPatternRepresentation()
        """
        if patternid < 1 or patternid > 25:
            msg = "Pattern ID [{0}] is invalid. "\
                  "Expecting an integer between 1 and 25".format(patternid)
            self.logger.error(msg)
            return None
        layoutpattern = FormLayoutPatternRepresentation()
        layoutpattern.id = patternid
        return layoutpattern 

    def new_form_widget(self,label,containernum=0,order=0,collapsed=False,form_control_group=None):
        """
        create a instance of the widget control.  Sits in a layout pattern row
        :param label: widget label - the label the user sees
        :param containernum: container number >= 0 Default=0.
          Used to set layout position based on layout pattern used
        :param order: order number in the field. Optional, >= 0 Default=0
        :param collapsed: widget expanded or collapsed.  Default = False (therefore expanded)
        :param form_control_group: optional.
          FormControlGroupRepresentation
        :returns: widget instance
          FormWidgetRepresentation()
        """
        widget = FormWidgetRepresentation()
        widget.name = "W{0}".format(str(uuid.uuid1()))    #generate unique name
        widget.label = label
        widget.view = "Dashboard Partials/_FormControlGroup"
        widget.view_name = "FormControlGroup"
        widget.layout_container = containernum
        widget.type_name = "User"
        widget.form_control_group = form_control_group
        widget.collapsed = collapsed
        widget.sort_order = order
        return widget

    def new_form_control_group(self,label,visible=True,form_controls=None):
        """
        create a instance of the form control group which will contain the lowest level controls
        such as text control, combox box control, date picker control etc..  Sits in a widget
        :param label: control group label - the label the user sees
        :param visible: Control visibility default = True
        :param form_controls: list of controls.  Default is empty list.
        :returns: form control
        FormControlGroupRepresentation()
        """
        controlgroup = FormControlGroupRepresentation()
        controlgroup.name = "FCG{0}".format(str(uuid.uuid1()))  #generate unique name
        controlgroup.label = label
        controlgroup.visible = visible
        controlgroup.area_icon = "fa-check-square-o"
        if form_controls == None:
            controlgroup.form_controls = list()
        else:
            controlgroup.form_controls = form_controls
        return controlgroup
    
    def new_text_control(self,label,name=None,length=200,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the basic text control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param length: field length if string.  Defaults to 200
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).strip("-").replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "Textbox"
        control.data_type = "string"
        if length != None:
            control.text_length = length
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control

    def new_multiline_text_control(self,label,name=None,length=1000,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the multiple line text control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param length: field length if string.  Defaults to 1000
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "TextArea"
        control.data_type = "string"
        if length != None:
            control.text_length = length
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control
    
    def new_combobox_control(self, label, name=None, datatype="string", order=1
                             , items=[], hint=None, visible=True,
                             required=False):
        """
        create a instance of the combobox control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param datatype: datatype of the field, list of options in datatypes property. Defaults to string
        :param order: order number in the field.  Optional.  Must be > 0
        :param items: the combo box items to add i.e the values in the combobox
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "UdfCombobox"
        control.data_type = datatype
        if order != None:
            control.sort_order = order
        control.combobox_items = items
        control.help_string = hint
        return control

    def new_combobox_item(self, label, value, order=1):
        """
        create a instance of the combobox item
        :param label: control label - the label the user sees in the comboxbox
        :param value: The c=value associated with the label
        :param order: order number in the field.  Optional.  Must be > 0
        :returns: form control instance with required settings for a combobox
        control
        assetic.FormControlComboboxItemRepresentation()
        """
        item = FormControlComboboxItemRepresentation()
        item.label = label
        item.value = value
        item.sort_order = order
        return item

    def new_date_control(self,label,name=None,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the date picker control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param datatype: datatype of the field, list of options in datatypes property. Defaults to DateTime
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False        
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "DatePicker"
        control.data_type = "DateTime"
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control
    def new_datetime_control(self,label,name=None,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the date picker control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False        
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "Timespan"
        control.data_type = "DateTime"
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control

    def new_stepper_control(self,label,name=None,minvalue=0,maxvalue=1000,step=1,mask="n0",order=1,hint=None,visible=True,required=False):
        """
        create a instance of the combobox control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param minvalue: minimum value.  Default = 0
        :param maxvalue: maximum value.  Default = 1000
        :param step: the amount ito increment each step by.  Default=1
        :param mask: display mask.  Default = 'n0'.  (Integer)
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "NumericTextBox"
        control.numeric_min = minvalue
        control.numeric_max = maxvalue
        control.numeric_step = step
        control.data_type = "decimal"
        if order != None:
            control.sort_order = order
        control.numeric_mask = mask
        control.help_string = hint
        return control

    def new_checkbox_control(self,label,name=None,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the combobox control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "Checkbox"
        control.data_type = "bool"
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control

    def new_map_control(self,label,name=None,order=1,hint=None,visible=True,required=False):
        """
        create a instance of the map (location) control
        :param label: control label - the label the user sees next to the text box
        :param name: a unique reference name for the control.
        If None then name will be generated
        :param order: order number in the field.  Optional.  Must be > 0
        :param hint: help string
        :param visible: tab visible True or False
        :param required: mandatory field Y/N.  If Y then True.  Default = False
        :returns: form control instance with required settings for a text control
        assetic.FormControlRepresentation()
        """
        control = FormControlRepresentation()
        if name == None:
            #generate unique name
            control.name = "C{0}".format(str(uuid.uuid1()).replace("-",""))
        else:
            control.name = name
        control.label = label
        control.visible = visible
        control.required = required
        control.type_name = "Map"
        control.data_type = "geography"
        if order != None:
            control.sort_order = order
        control.help_string = hint
        return control
    
    def verify_mandatory_fields(self,data_repr,required_repr,mandatory_fields=[]):
        """
        Verify the representation type is correct and mandatory fields not null
        :param data_repr: The representation object with the data
        :param representation_name: The expected representation
        e.g. ComplexAssetRepresentation
        :param mandatory_fields: a list of fields to verify.  Optional
        :return: True (valid), False (invalid)
        """
        # check the type is correct
        if isinstance(data_repr,required_repr) != True:
            msg ="Data object is not the required type: '{0}'".format(
                str(required_repr))
            self.logger.error(msg)
            return False
        # check the mandatory fields are not NULL
        for field in mandatory_fields:
            if getattr(data_repr,field) == None:
                msg ="Required parameter cannot be NULL: '{0}'".format(field)
                self.logger.error(msg)
                return False                    
        return True

    def set_layout_pattern_dict(self):
        """
        Builds a dictionary of where layout pattern description is the key
        and the layout ID is the value.
        :return: dictionary of layout decription and id
        """
        layouts = {}
        layouts["Single"] = 1
        layouts["column: 2 equal columns"] = 2
        layouts["3 equal columns"] = 3
        layouts["column: 8 Left, 4 Right"] = 4
        layouts["column: 4 Left, 8 Right"] = 5
        layouts["column: 4 equal columns"] = 6
        layouts["Row: Row 1 (1 column),Row 2 (2 equal columns)"] = 7
        layouts["Row: Row 1 (1 column),Row 2 (3 equal columns)"] = 8
        layouts["Row: Row 1 (1 column),Row 2 (8 Left, 4 Right)"] = 9
        layouts["Row: Row 1 (1 column),Row 2 (4 Left, 8 Right)"] = 10
        layouts["Row: Row 1 (1 column),Row 2 (4 equal columns)"] = 11
        layouts["Row: Row 1 (2 equal columns),Row 2 (1 column)"] = 12
        layouts["Row: Row 1 (3 equal columns),Row 2 (1 column)"] = 13
        layouts["Row: Row 1 (8 Left, 4 Right),Row 2 (1 column)"] = 14
        layouts["Row: Row 1 (4 Left, 8 Right),Row 2 (1 column)"] = 15
        layouts["Row: Row 1 (4 equal columns),Row 2 (1 column)"] = 16
        layouts["Row: Row 1 (1 column), Row 2 (2 equal columns),Row 3 (1 column)"] = 17
        layouts["Row: Row 1 (1 column), Row 2 (3 equal columns),Row 3 (1 column)"] = 18
        layouts["Row: Row 1 (1 column), Row 2 (8 Left, 4 Right),Row 3 (1 column)"] = 19
        layouts["Row: Row 1 (1 column), Row 2 (4 Left, 8 Right),Row 3 (1 column)"] = 20
        layouts["Row: Row 1 (1 column), Row 2 (4 equal columns),Row 3 (1 column)"] = 21
        layouts["Row: Row 1 (4 equal columns), Row 2 (2 equal columns)"] = 22
        layouts["Row: Row 1 (4 equal columns), Row 2 (4 equal columns)"] = 23
        layouts["Row: Row 1 (3 equal columns), Row 2 (2 equal columns)"] = 24
        layouts["Row: Row 1 (1 equal col), Row 2 (2 equal col),Row 3 (1 equal col), Row 4 (2 equal col)"] = 25
        return layouts


