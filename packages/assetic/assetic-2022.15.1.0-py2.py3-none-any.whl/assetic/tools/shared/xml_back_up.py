import arcpy
import os
import xml.etree.ElementTree as ET
import assetic
from arcpy import env
import xml.dom.minidom
import tkinter as tk
import logging
from tkinter import ttk
from tkinter import *
from assetic import AsseticSDK
from assetic.api_client import ApiClient
from assetic.api import WorkOrderApi, AssetApi, AssetConfigurationApi
from assetic.rest import ApiException
from tkinter import messagebox
from tkinter.messagebox import showinfo


class XMl_Prompter:
    extra_fields = 6
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)
    asset_temp_path = {}
    empty_value = ['']

    for i in range(extra_fields):
        asset_temp_path[i] = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config{0}.xml'.format(i)
        a_file = open(asset_temp_path[i], "w")
        a_file.truncate()
        a_file.close()
    component_temp_path = os.environ['APPDATA'] + '\\Assetic\\component.xml'
    merged_temp_path = os.environ['APPDATA'] + '\\Assetic\\merged_arcmap_edit_config.xml'

    def __init__(self, master, logfile=r"C:\temp\logfile.log", loglevelname="Debug", layer_dict=None,
                 bulk_threshold="100", upload_feature="True", resolve_lookups="True", creation_status="active"):
        self.master = master
        self.logfile = logfile
        self.loglevelname = loglevelname
        self.bulk_threshold = bulk_threshold
        self.resolve_lookups = resolve_lookups
        self.upload_feature = upload_feature
        self.creation_status = creation_status

        self.layer_dict = layer_dict
        api_client = ApiClient()
        self.api_client = api_client
        self.logger = api_client.configuration.packagelogger
        self.asset_category_api = AssetConfigurationApi(self.api_client)
        self.asset_type_api = AssetConfigurationApi(self.api_client)
        self.asset_subtype_api = AssetConfigurationApi(self.api_client)
        self.asset_class_api = AssetConfigurationApi(self.api_client)
        self.asset_subclass_api = AssetConfigurationApi(self.api_client)
        self.asset_criticality_api = AssetConfigurationApi(self.api_client)
        self.host = self.api_client.configuration.host
        self.layer_labels = []
        self.layer_buttons = []
        self.component_labels = []
        self.component_buttons = []
        self.dimension_labels = [[]]
        self.dimension_buttons = [[]]
        for m in range(self.extra_fields):
            self.dimension_labels.append([])
            self.dimension_buttons.append([])
        self.d_number = {}
        self.lst_d_number = []

        self.existing_layer = {}
        self.error = 0
        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())
        try:
            category = self.asset_category_api.asset_configuration_get_asset_category()
        except ApiException as e:
            message = "Error getting Asset Category.\n Status: {0}, Reason: {1} \n {2}".format(e.status, e.reason,
                                                                                               e.body)
            self.logger.error(message)
            return
        if "ResourceList" not in category:
            msg = "No ResourceList found "
            self.logger.error(msg)
            return
        self.category_dict = {}
        for i in category["ResourceList"]:
            self.category_dict[i["Label"]] = i["Id"]
        self.category_option = sorted(self.category_dict.keys(), key=lambda x: x.lower())

        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter")
        master.geometry("1500x800")
        master.header = Label(master, text="XML Prompter", font=("Arial", 40, "bold")).place(x=600, y=80)
        if os.path.exists(self.save_path):
            message = "arcmap_edit_config.xml file already exists in \n" \
                      "{0} ".format(self.save_path)
            Button(master, text="Continue with existing file", width='20', height='2',
                   command=lambda: self.continue_file(), bg="#349cbc", fg='gray92').place(
                x=700,
                y=500)
        else:
            message = "arcmap_edit_config.xml file will be created in\n {0}".format(self.save_path)

        Button(master, text="create new file", width='20', height='2',
               command=lambda: self.window_1_(), bg="#349cbc", fg='gray92').place(
            x=700,
            y=600)
        Label(master, text=message).place(x=550, y=300)

    def window_1_(self):

        self.master.withdraw()
        window_1 = Toplevel(self.master)
        self.window_1 = window_1
        self.window_1.geometry("1500x800")
        Label(window_1, text="Layer number: ").place(x=650, y=115)
        option = [i for i in range(self.extra_fields)]
        self.select_number = StringVar()
        self.select_number.set(option[0])
        # Create Dropdown menu
        drop = OptionMenu(window_1, self.select_number, *option)
        # if there are layers in the existing file, show the number of the layer directly for the user to edit it
        if (self.existing_layer):

            Label(window_1,
                  text="To Edit existing layer, click info\n To add layer, go back to previous window and choose add layer to existing file",
                  font='Helvetica 12 bold').place(
                x=550, y=25)
            self.ok()
            # if existing layer is more than the maximum , set it to the maximum fields
            if (len(self.existing_layer)) > self.extra_fields:
                num_layers = 5
            else:
                num_layers = len(self.existing_layer)

            self.select_number.set(num_layers)
            self.ok()
            # todo can they edit exisitng layer and add a new layer to that ? or should they run the prompter again.
            #  better check if there is more than the self.exisiting layer then, a new one is empty and ready to be added
        else:
            # else if there wasnt any file detected, choose the number of layer

            Button(self.window_1, text="OK", command=lambda: self.ok()).place(x=850, y=115)
            drop.place(x=790, y=115)
        Button(self.window_1, text="Previous", width='10', height='2',
               command=lambda: [self.window_1.destroy(), self.master.deiconify(), self.set_existing_layer(0)],
               font=("Arial", 10, "bold")).place(x=100, y=700)

    def set_existing_layer(self, value):
        self.existing_layer = value

    def ok(self):
        """
        when 'ok' button, info button will appear
        """
        number = self.select_number.get()
        l_label = {}
        l_button = {}
        # delete the button and label if the number change
        if len(self.layer_labels) != 0:
            for label in self.layer_labels:
                label.destroy()
            for but in self.layer_buttons:
                but.destroy()
        for i in range(int(number)):
            self.current_layer = i

            l_label[i] = Label(self.window_1, text="Layer {0}".format(i + 1))
            l_label[i].place(x=650, y=(i + 1) * 40 + 120)
            l_button[i] = Button(self.window_1, text='Info',
                                 command=lambda j=i: self.window_2_(j + 1))
            l_button[i].place(x=800, y=(i + 1) * 40 + 120)
            self.layer_labels.append(l_label[i])
            self.layer_buttons.append(l_button[i])

    def window_2_(self, num_layer):
        """
        Asset details in Window
        """
        self.num_layer = num_layer
        self.window_1.withdraw()
        window_2 = Toplevel(self.master)  # child window
        self.window_2 = window_2
        window_2.title("Assetic XML Prompter")
        window_2.geometry("1500x800")

        Label(window_2, text="Layer Name*").place(x=15, y=30)
        Label(window_2, text="Category*").place(x=15, y=80)
        self.window_2_left_frame(window_2, num_layer)
        self.window_2_right_frame(window_2, num_layer)
        self.button_previous = Button(self.window_2, text="Previous", width='10', height='2',
                                      command=lambda: [self.window_2.destroy(), self.window_1.deiconify()],
                                      font=("Arial", 10, "bold")).place(x=100, y=700)
        if self.existing_layer:
            Label(window_2,
                  text="if existing arcmap_edit_config.xml is used,\n it will automatically be edited once saved button is clicked",
                  fg="red", font='Helvetica 11 underline').place(x=800, y=10)
            if self.existing_layer[num_layer]['layer_name'] in [None or '']:
                messagebox.showerror('Error', "Layer name is missing ArcMap_edit_config.xml file")
                self.logger.error("Layer name is missing in ArcMap_edit_config.xml file")
                layer_name = self.existing_layer[num_layer]['layer_name']
                self.layer_drop = ttk.Combobox(window_2, values=[layer_name], width=40)
                self.layer_drop.current(0)
                self.layer_drop.config(value=self.layer_option)
                self.layer_drop.bind("<<ComboboxSelected>>", self.Pick_GIS_Field)
            elif self.existing_layer[num_layer]['layer_name'] not in self.layer_option:
                messagebox.showerror('Error', "Layer does not exist")
                self.logger.error("Layer does not exist")
                layer_name = self.existing_layer[num_layer]['layer_name']
                self.layer_drop = ttk.Combobox(window_2, values=[layer_name], width=40)
                self.layer_drop.current(0)
                self.layer_drop.config(value=self.layer_option)
                self.layer_drop.bind("<<ComboboxSelected>>", self.Pick_GIS_Field)
            else:

                layer_name = self.existing_layer[num_layer]['layer_name']
                self.layer_drop = ttk.Combobox(window_2, values=[layer_name], width=40)
                self.layer_drop.current(0)
                self.layer_drop.config(value=self.layer_option)
                self.Pick_GIS_Field()
            if self.existing_layer[num_layer]['category'] in [None or '']:
                messagebox.showerror('Error', "category name is missing ArcMap_edit_config.xml file")
                self.logger.error("category name is missing in ArcMap_edit_config.xml file")
                category = self.existing_layer[num_layer]['category']
                self.category_drop = ttk.Combobox(window_2, values=[category], width=40)
                self.category_drop.current(0)
                self.category_drop.config(value=self.category_option)
                self.category_drop.bind("<<ComboboxSelected>>", self.Pick_Assetic_Field)
            elif self.existing_layer[num_layer]['category'] not in self.category_option:
                messagebox.showerror('Error', "category name does not exist")
                self.logger.error("category name does not exist")
                category = self.existing_layer[num_layer]['category']
                self.category_drop = ttk.Combobox(window_2, values=[category], width=40)
                self.category_drop.current(0)
                self.category_drop.config(value=self.category_option)
                self.category_drop.bind("<<ComboboxSelected>>", self.Pick_Assetic_Field)

            else:
                category = self.existing_layer[num_layer]['category']
                self.category_drop = ttk.Combobox(window_2, values=[category], width=40)
                self.category_drop.current(0)
                self.category_drop.config(value=self.category_option)
                self.Pick_Assetic_Field()

        else:
            self.layer_drop = ttk.Combobox(window_2, values=self.layer_option, width=40)
            self.layer_drop.bind("<<ComboboxSelected>>", self.Pick_GIS_Field)
            self.category_drop = ttk.Combobox(window_2, values=self.category_option, width=40)
            self.category_drop.bind("<<ComboboxSelected>>", self.Pick_Assetic_Field)
        self.layer_drop.place(x=250, y=30)
        self.category_drop.place(x=250, y=80)

        # if not self.error:
        # check the error from the gis field or the asset fieds si cnnot click next
        self.button_save = Button(window_2, text="Save", width='20', height='2',
                                  command=lambda: self.save_asset_info(num_layer),
                                  bg="#349cbc", fg='gray92').place(x=350, y=700)

    def window_2_left_frame(self, window_2, num_layer):
        """core fields of asset form """

        ttk.Separator(window_2).place(x=0, y=120, relwidth=4)
        Label(window_2, text="Core Fields \n"
                             "(GIS Field Name)", font=("Arial Bold", 12)).place(x=15, y=130)
        Label(window_2, text="Asset ID*").place(x=15, y=200)
        Label(window_2, text="Asset Name*").place(x=15, y=250)
        Label(window_2, text="Asset GUID").place(x=15, y=300)
        Label(window_2, text="Asset Class").place(x=15, y=350)
        Label(window_2, text="Asset SubClass").place(x=15, y=400)
        Label(window_2, text="Asset Type").place(x=15, y=450)
        Label(window_2, text="Asset SubType").place(x=15, y=500)

        if self.existing_layer and self.existing_layer[num_layer] and len(
                self.existing_layer[num_layer]['corefields'].items()) != 0:
            print("here")
            existing_layer = self.existing_layer[num_layer]
            print("existing_layer", existing_layer['corefields']['asset_id'])

            self.asset_ID_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_id']], width=40)
            self.asset_ID_field.current(0)
            self.asset_GUID_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['id']], width=40)
            self.asset_GUID_field.current(0)
            self.asset_name_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_name']],
                                                 width=40)
            self.asset_name_field.current(0)
            self.asset_class_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_class']],
                                                  width=40)
            self.asset_class_field.current(0)
            self.asset_subclass_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_sub_class']],
                                                     width=40)
            self.asset_subclass_field.current(0)
            self.asset_type_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_type']],
                                                 width=40)
            self.asset_type_field.current(0)
            self.asset_subtype_field = ttk.Combobox(window_2, values=[existing_layer['corefields']['asset_sub_type']],
                                                    width=40)
            self.asset_subtype_field.current(0)
            # todo havent done for the guid when writing it back to xml file , only appearing in the UI
        else:

            self.asset_ID_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_ID_field.current(0)
            self.asset_GUID_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_GUID_field.current(0)
            self.asset_name_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_name_field.current(0)
            self.asset_class_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_class_field.current(0)
            self.asset_subclass_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_subclass_field.current(0)
            self.asset_type_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_type_field.current(0)
            self.asset_subtype_field = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_subtype_field.current(0)
            # self.asset_criticality_field = ttk.Combobox(LFrame, values=self.empty_value, width=40)
            # self.asset_criticality_field.current(0)

        self.asset_ID_field.place(x=250, y=200)
        self.asset_name_field.place(x=250, y=250)
        self.asset_GUID_field.place(x=250, y=300)
        self.asset_class_field.place(x=250, y=350)
        self.asset_subclass_field.place(x=250, y=400)
        self.asset_type_field.place(x=250, y=450)
        self.asset_subtype_field.place(x=250, y=500)
        # self.asset_criticality_field.place(x=250, y=550)

    def Pick_GIS_Field(self, e=1):
        """once layer name is populated, drop down in the core defaults will be created"""
        one_layer = self.layer_drop.get()
        ## if button not clicked make it empty
        if one_layer in self.layer_option:
            self.fields = sorted(self.layer_dict[one_layer], key=lambda x: x.lower())
            self.fields.insert(0, " ")
            self.asset_ID_field.config(value=self.fields)
            self.asset_name_field.config(value=self.fields)
            self.asset_GUID_field.config(value=self.fields)
            self.asset_class_field.config(value=self.fields)
            self.asset_subclass_field.config(value=self.fields)
            self.asset_type_field.config(value=self.fields)
            self.asset_subtype_field.config(value=self.fields)
            # self.asset_criticality_field.config(value=self.fields)

        else:
            msg = "Layer {0} not found".format(one_layer)
            self.logger.error(msg)
            messagebox.showerror("Error", msg)
            self.error = 1

    def window_2_right_frame(self, window_2, num_layer):
        """core defaults of the asset form"""
        Label(window_2, text="Core Defaults\n (Hardcoded default value from the Assetic Core Field Name)",
              font=("Arial Bold", 12)).place(x=850, y=130)
        Label(window_2, text="Asset ID*").place(x=850, y=200)
        Label(window_2, text="Asset Name*").place(x=850, y=250)
        Label(window_2, text="Asset GUID").place(x=850, y=300)
        Label(window_2, text="Asset Class").place(x=850, y=350)
        Label(window_2, text="Asset SubClass").place(x=850, y=400)
        Label(window_2, text="Asset Type").place(x=850, y=450)
        Label(window_2, text="Asset SubType").place(x=850, y=500)

        if self.existing_layer and self.existing_layer[num_layer] and len(
                self.existing_layer[num_layer]['coredefaults'].items()) != 0:
            existing_layer = self.existing_layer[num_layer]

            self.asset_name_field_default = Entry(window_2, textvariable=StringVar(window_2,
                                                                                   value=existing_layer['coredefaults'][
                                                                                       'asset_name']), width=40)
            self.asset_class_field_default = ttk.Combobox(window_2,
                                                          values=[existing_layer['coredefaults']['asset_class']],
                                                          width=40)
            self.asset_class_field_default.current(0)
            self.asset_subclass_field_default = ttk.Combobox(window_2,
                                                             values=[existing_layer['coredefaults']['asset_sub_class']],
                                                             width=40)

            self.asset_subclass_field_default.current(0)
            self.asset_subclass_fields__(num_layer)
            self.asset_type_field_default = ttk.Combobox(window_2,
                                                         values=[existing_layer['coredefaults']['asset_type']],
                                                         width=40)
            self.asset_type_field_default.current(0)
            self.asset_subtype_field_default = ttk.Combobox(window_2,
                                                            values=[existing_layer['coredefaults']['asset_sub_type']],
                                                            width=40)
            self.asset_subtype_field_default.current(0)
            self.asset_subtype_fields__(num_layer)
        else:
            self.asset_class_field_default = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_name_field_default = Entry(window_2, textvariable=StringVar(), width=40)
            self.asset_subclass_field_default = ttk.Combobox(window_2, values=self.empty_value, width=40)
            self.asset_type_field_default = ttk.Combobox(window_2, values=self.empty_value, width=40)
            # self.asset_type_field_default.bind("<<ComboboxSelected>>", self.asset_subtype_fields)
            # self.asset_class_field_default.bind("<<ComboboxSelected>>", self.asset_subclass_fields)
            self.asset_subtype_field_default = ttk.Combobox(window_2, values=self.empty_value, width=40)

        # self.asset_ID_field_default.place(x=1100, y=200)
        self.asset_name_field_default.place(x=1100, y=250)
        # self.asset_GUID_field_default.place(x=1100, y=300)
        self.asset_class_field_default.place(x=1100, y=350)
        self.asset_subclass_field_default.place(x=1100, y=400)
        self.asset_type_field_default.place(x=1100, y=450)
        self.asset_subtype_field_default.place(x=1100, y=500)

    def Pick_Assetic_Field(self, e=1):
        """
        right frame contain information from assetic
        """

        one_category = self.category_drop.get()

        if one_category in self.category_option:
            # get asset type, subtype based on the given cateogy
            self.Asset_Field()
            print("one category", one_category)

            self.asset_type_field_default.bind("<<ComboboxSelected>>", self.asset_subtype_fields__)
            self.asset_class_field_default.bind("<<ComboboxSelected>>", self.asset_subclass_fields__)
            # self.asset_name_field_default = Entry(RFrame, textvariable=StringVar(), width=40)
            # self.asset_class_field_default = ttk.Combobox(RFrame, values=self.asset_class_list, width=40)
        else:
            msg = "'{0}' category not found".format(one_category)
            self.logger.error(msg)
            messagebox.showerror("Error", msg)
            self.error = 1

    def Asset_Field(self):
        """Get asset class, subclass , type and subtype """

        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500
        }
        try:
            asset_types = self.asset_type_api.asset_configuration_get_asset_types(**kwargs)
        except ApiException as e:
            self.logger.error(
                "Error getting Asset Category.\n"
                "Status: {0}, Reason: {1} \n "
                "{2}".format(e.status, e.reason, e.body))
            self.error = 1
            return
        if "ResourceList" not in asset_types:
            self.error = 1
            return
        self.asset_types_list = [i["Name"] for i in asset_types["ResourceList"]]
        self.asset_types_list.insert(0, " ")
        self.asset_type_field_default.config(value=self.asset_types_list)
        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500
        }
        try:
            asset_class = self.asset_class_api.asset_configuration_get_asset_classes(**kwargs)
        except ApiException as e:
            self.logger.error(
                "Error getting Asset Category.\n"
                "Status: {0}, Reason: {1} \n "
                "{2}".format(e.status, e.reason, e.body))
            self.error = 1

            return
        if "ResourceList" not in asset_class:
            self.error = 1
            return
        self.asset_class_list = [i["Name"] for i in asset_class["ResourceList"]]
        self.asset_class_list.insert(0, " ")
        self.asset_class_field_default.config(value=self.asset_class_list)

    def asset_subtype_fields__(self, e):
        self.asset_subtype_not_found = 0
        asset_type = self.asset_type_field_default.get()
        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500
        }
        x = self.asset_type_api.asset_configuration_get_asset_types(**kwargs)
        self.asset_subtype_list = [' ']
        for one_type in x["ResourceList"]:
            # if the type exist
            if one_type['Name'] == asset_type:
                # check if type contain subtype
                if len(one_type["SubTypes"]) != 0:
                    self.asset_subtype_list = [j["Name"] for j in one_type["SubTypes"]]
                    self.asset_subtype_list.insert(0, " ")
                else:
                    self.asset_subtype_list = [' ']
                    messagebox.showerror('Error', 'No Asset SubType found')
                    self.asset_subtype_not_found = 1
                break;
        self.asset_subtype_field_default.config(value=self.asset_subtype_list)

    def asset_subclass_fields__(self, e):
        self.asset_subclass_not_found = 0
        asset_class = self.asset_class_field_default.get()
        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500
        }
        x = self.asset_class_api.asset_configuration_get_asset_classes(**kwargs)
        self.asset_subclass_list = [' ']
        for one_class in x["ResourceList"]:
            # if the type exist

            if one_class['Name'] == asset_class:
                # check if type contain subtype
                if len(one_class["SubTypes"]) != 0:
                    self.asset_subclass_list = [j["Name"] for j in one_class["SubTypes"]]
                    self.asset_subclass_list.insert(0, " ")
                else:

                    error = 1
                    self.asset_subclass_not_found = 1
                    messagebox.showerror('Error', 'No Asset SubClass found')

                break;

        self.asset_subclass_field_default.config(value=self.asset_subclass_list)

    def continue_file(self):
        """use existing file and save it in a dictionary called self.existing_layer"""
        asset_found = 0
        self.existing_layer = {}
        filesize = os.path.getsize(self.save_path)

        if filesize == 0:
            messagebox.showerror("Error", "File is empty")
        else:
            # check if xml valid or not
            try:
                ET.parse(self.save_path)
            except Exception as e:
                messagebox.showerror("Error", e.message)
                return
            data = ET.parse(self.save_path).getroot()
            # check if the data contain operation tag
            if len(data.findall("operation")) > 0:
                print("len(data.findall('operation'))", len(data.findall('operation')))
                for operation in data.iter("operation"):
                    # check if action exist
                    action = operation.get("action")
                    # if action equal to asset
                    if action in ["Asset", "asset"]:
                        asset_found = 1
                        # parse the data
                    else:
                        message = "No 'Asset' attribute in 'Operation' tag "
                        messagebox.showerror("Error", message)
                        self.logger.error(message)
                        return
                    # count the number of the layer
                    if asset_found:

                        count = 0
                        for layer in operation.iter("layer"):
                            layer_info = {}
                            print("yoooo", self.existing_layer)
                            core_defaults_info = {}
                            core_fields_info = {}

                            try:
                                layer_info["layer_name"] = layer.get("name")
                                print("dcvbnjhbgvfcdxs", layer_info["layer_name"])
                            except AttributeError:
                                layer_info["layer_name"] = ''
                            try:
                                layer_info["category"] = layer.find('category').text
                            except AttributeError:
                                layer_info["category"] = ''
                            try:
                                layer_info["creation_status"] = layer.find('creation_status').text
                            except AttributeError:
                                layer_info["creation_status"] = ''
                            try:
                                layer_info['upload_feature'] = layer.find('upload_feature').text
                            except AttributeError:
                                layer_info['upload_feature'] = ''

                            if layer.find('corefields') is not None and len(layer.find('corefields')) > 0:
                                corefields = layer.find('corefields')
                                try:
                                    core_fields_info['asset_id'] = corefields.find('asset_id').text
                                except AttributeError:
                                    core_fields_info['asset_id'] = ''
                                try:
                                    core_fields_info['id'] = corefields.find('id').text
                                except AttributeError:
                                    core_fields_info['id'] = ''

                                try:
                                    core_fields_info['asset_name'] = corefields.find('asset_name').text
                                except AttributeError:
                                    core_fields_info['asset_name'] = ''
                                try:
                                    core_fields_info['asset_class'] = corefields.find('asset_class').text
                                except AttributeError:
                                    core_fields_info['asset_class'] = ''
                                try:
                                    core_fields_info['asset_sub_class'] = corefields.find('asset_sub_class').text
                                except AttributeError:
                                    core_fields_info['asset_sub_class'] = ''
                                try:
                                    core_fields_info['asset_type'] = corefields.find('asset_type').text
                                except AttributeError:
                                    core_fields_info['asset_type'] = ''
                                try:
                                    core_fields_info['asset_sub_type'] = corefields.find('asset_sub_type').text
                                except AttributeError:
                                    core_fields_info['asset_sub_type'] = ''

                            if (layer.find('coredefaults')) is not None and len(layer.find('coredefaults')) > 0:
                                coredefaults = layer.find('coredefaults')
                                try:
                                    core_defaults_info['asset_id'] = coredefaults.find('asset_id').text
                                except AttributeError:
                                    core_defaults_info['asset_id'] = ''
                                try:
                                    core_defaults_info['id'] = coredefaults.find('id').text
                                except AttributeError:
                                    core_defaults_info['id'] = ''

                                try:
                                    core_defaults_info['asset_name'] = coredefaults.find('asset_name').text
                                except AttributeError:
                                    core_defaults_info['asset_name'] = ''
                                try:
                                    core_defaults_info['asset_class'] = coredefaults.find('asset_class').text
                                except AttributeError:
                                    core_defaults_info['asset_class'] = ''
                                try:
                                    core_defaults_info['asset_sub_class'] = coredefaults.find(
                                        'asset_sub_class').text
                                except AttributeError:
                                    core_defaults_info['asset_sub_class'] = ''
                                try:
                                    core_defaults_info['asset_type'] = coredefaults.find('asset_type').text
                                except AttributeError:
                                    core_defaults_info['asset_type'] = ''
                                try:
                                    core_defaults_info['asset_sub_type'] = coredefaults.find(
                                        'asset_sub_type').text
                                except AttributeError:
                                    core_defaults_info['asset_sub_type'] = ''
                            count_component = 0
                            existing_component = {}
                            for component in layer.iter("components"):
                                component_core_default_info = {}
                                component_core_fields_info = {}

                                count_component += 1
                                if component.find('componentdefaults') is not None and len(
                                        component.find('componentdefaults')) > 0:
                                    componentdefaults = component.find('componentdefaults')
                                    print("findallc componentdefaults", len(component.find('componentdefaults')))
                                    try:
                                        component_core_default_info['label'] = componentdefaults.find('label').text
                                    except AttributeError:
                                        component_core_default_info['label'] = ''
                                    try:
                                        component_core_default_info[
                                            'component_type'] = componentdefaults.find('component_type').text
                                    except AttributeError:
                                        component_core_default_info['component_type'] = ''
                                    try:
                                        component_core_default_info[
                                            'dimension_unit'] = componentdefaults.find('dimension_unit').text
                                    except AttributeError:
                                        component_core_default_info['dimension_unit'] = ''
                                    try:
                                        component_core_default_info[
                                            'network_measure_type'] = componentdefaults.find(
                                            'network_measure_type').text
                                    except AttributeError:
                                        component_core_default_info['network_measure_type'] = ''
                                    try:
                                        component_core_default_info['design_life'] = componentdefaults.find(
                                            'design_life').text
                                    except AttributeError:
                                        component_core_default_info['design_life'] = ''
                                    try:
                                        component_core_default_info['material_type'] = componentdefaults.find(
                                            'material_type').text
                                    except AttributeError:
                                        component_core_default_info['material_type'] = ''

                                if component.find('componentfields') is not None and len(
                                        component.find('componentfields')) > 0:
                                    componentfields = component.find('componentfields')
                                    try:
                                        component_core_fields_info['label'] = componentfields.find('label').text
                                    except AttributeError:
                                        component_core_fields_info['label'] = ''
                                    try:
                                        component_core_fields_info[
                                            'component_type'] = componentfields.find('component_type').text
                                    except AttributeError:
                                        component_core_fields_info['component_type'] = ''
                                    try:
                                        component_core_fields_info[
                                            'dimension_unit'] = componentfields.find('dimension_unit').text
                                    except AttributeError:
                                        component_core_fields_info['dimension_unit'] = ''
                                    try:
                                        component_core_fields_info[
                                            'network_measure_type'] = componentfields.find(
                                            'network_measure_type').text
                                    except AttributeError:
                                        component_core_fields_info['network_measure_type'] = ''
                                    try:
                                        component_core_fields_info['design_life'] = componentfields.find(
                                            'design_life').text
                                    except AttributeError:
                                        component_core_fields_info['design_life'] = ''
                                    try:
                                        component_core_fields_info['material_type'] = componentfields.find(
                                            'material_type').text
                                    except AttributeError:
                                        component_core_fields_info['material_type'] = ''

                                count_dimension = 0
                                existing_dimension = {}
                                for dimension in component.iter("dimension"):
                                    dimension_core_default_info = {}
                                    dimension_core_fields_info = {}
                                    count_dimension += 1
                                    if dimension.find('dimensiondefaults') is not None and len(
                                            dimension.find('dimensiondefaults')) > 0:
                                        dimensiondefaults = dimension.find('dimensiondefaults')
                                        try:
                                            dimension_core_default_info['unit'] = dimensiondefaults.find('unit').text
                                        except AttributeError:
                                            dimension_core_default_info['unit'] = ''
                                        try:
                                            dimension_core_default_info['shape_name'] = dimensiondefaults.find(
                                                'shape_name').text
                                        except AttributeError:
                                            dimension_core_default_info['shape_name'] = ''
                                        try:
                                            dimension_core_default_info[
                                                'length_unit'] = dimensiondefaults.find(
                                                'length_unit').text
                                        except AttributeError:
                                            dimension_core_default_info['length_unit'] = ''
                                        try:
                                            dimension_core_default_info['width_unit'] = dimensiondefaults.find(
                                                'width_unit').text
                                        except AttributeError:
                                            dimension_core_default_info['width_unit'] = ''
                                        try:
                                            dimension_core_default_info['record_type'] = dimensiondefaults.find(
                                                'record_type').text
                                        except AttributeError:
                                            dimension_core_default_info['record_type'] = ''
                                        try:
                                            dimension_core_default_info[
                                                'network_measure_type'] = dimensiondefaults.find(
                                                'network_measure_type').text
                                        except AttributeError:
                                            dimension_core_default_info['network_measure_type'] = ''
                                    if dimension.find('dimensionfields') is not None and len(
                                            dimension.find('dimensionfields')) > 0:
                                        dimensionfields = dimension.find('dimensionfields')

                                        try:
                                            dimension_core_fields_info['unit'] = dimensionfields.find('unit').text
                                        except AttributeError:
                                            dimension_core_fields_info['unit'] = ''
                                        try:
                                            dimension_core_fields_info[
                                                'length_unit'] = dimensionfields.find(
                                                'length_unit').text
                                        except AttributeError:
                                            dimension_core_fields_info['length_unit'] = ''
                                        try:
                                            dimension_core_fields_info['width_unit'] = dimensionfields.find(
                                                'width_unit').text
                                        except AttributeError:
                                            dimension_core_fields_info['width_unit'] = ''
                                        try:
                                            dimension_core_fields_info['record_type'] = dimensionfields.find(
                                                'record_type').text
                                        except AttributeError:
                                            dimension_core_fields_info['record_type'] = ''
                                        try:
                                            dimension_core_fields_info['shape_name'] = dimensionfields.find(
                                                'shape_name').text
                                        except AttributeError:
                                            dimension_core_fields_info['shape_name'] = ''
                                        try:
                                            dimension_core_fields_info[
                                                'network_measure_type'] = dimensionfields.find(
                                                'network_measure_type').text
                                        except AttributeError:
                                            dimension_core_fields_info['network_measure_type'] = ''
                                    existing_dimension[count_dimension] = {
                                        "dimensionfields": dimension_core_fields_info,
                                        "dimensiondefaults": dimension_core_default_info}
                                existing_component[count_component] = {"componentfields": component_core_fields_info,
                                                                       "componentdefaults": component_core_default_info,
                                                                       "dimension": existing_dimension}

                            # print("findallc componentfields", len(component.find('componentfields')))
                            #     print("findallc omponent",len(layer.findall('components')))

                            # check if action exist
                            # component=layer.find('components')
                            # if component.find("componentdefaults") is not None and len(component.find("componentdefaults"))>0:
                            #     try :
                            layer_info["coredefaults"] = core_defaults_info
                            layer_info["corefields"] = core_fields_info

                            layer_info["components"] = existing_component
                            count = count + 1
                            self.existing_layer[count] = layer_info
                    # if functional location operation found
                    # pass
            else:
                message = "'Operation' tag does not exist in the file"
                messagebox.showerror("Error", message)
                self.logger.error(message)
                return

            # go to next window_1
            self.window_1_()

            # if success:
            #
            #     pass

    def save_asset_info(self, i):
        """
        save the information from the form
        params i: The nth of the layer
        """

        error = 0
        # check layer
        if self.layer_drop.get() not in self.layer_option:
            messagebox.showerror('Error', 'Layer does not  exist')
            return
        self.xml_layer = self.layer_drop.get()
        # check_category
        if self.category_drop.get() not in self.category_option:
            messagebox.showerror('Error', 'Asset Category does not  exist')
            return
        self.xml_category = self.category_drop.get()
        # check asset id
        if self.asset_ID_field.get() in ["", ' ']:
            messagebox.showerror('Error', 'Asset ID cannot be empty')
            error = 1
            return
        elif self.asset_ID_field.get() not in self.fields:
            messagebox.showerror('Error', 'Asset ID fields in Core Fields does not exist ')
            error = 1
            return
        self.xml_asset_ID = self.asset_ID_field.get()
        if self.asset_ID_field.get() in ["", ' ']:
            self.xml_asset_ID = None
        if self.asset_GUID_field.get() in ["", ' ']:
            self.xml_asset_GUID_core_field = None
        elif self.asset_GUID_field.get() in self.fields:
            self.xml_asset_GUID_core_field = self.asset_GUID_field.get()
        else:
            messagebox.showerror("Error", "Asset GUID fields in Core Fields does not exist ")
            return

        if self.asset_name_field_default.get() in ["", ' '] and self.asset_name_field.get() in ["", ' ']:

            messagebox.showerror('Error', 'Asset Name cannot be empty')
            return
        elif self.asset_name_field_default.get():
            # if asset name in core default is not empty
            self.xml_asset_name_core_default = self.asset_name_field_default.get()
            # if asset name in core field not empty
            if self.asset_name_field.get() not in [" ", ''] and self.asset_name_field.get() not in self.fields:
                messagebox.showerror('Error', 'Asset Name Fields in Core Fields does not exist')
                return
            elif self.asset_name_field.get() in [" ", ""]:
                self.xml_asset_name_core_field = None
            elif self.asset_name_field.get() in self.fields:
                self.xml_asset_name_core_field = self.asset_name_field.get()
        else:
            self.xml_asset_name_core_field = self.asset_name_field.get()
            self.xml_asset_name_core_default = None
            if self.xml_asset_name_core_field not in self.fields:
                messagebox.showerror('Error', 'Asset Name Fields in Core Fields does not exist')
                return
        # check asset class and subclass
        error = self.check_asset_class_subclass()
        if error:
            return

        # check asset type and subtype
        error = self.check_asset_type_subtype()
        if error:
            return

        if not error:

            messagebox.showinfo('Info', 'Successfully Saved')
        else:
            messagebox.showerror("Error", 'check again')

        if self.existing_layer:
            # edit an exisitng xml file
            self.edit_existing_xml_file(i)
        else:
            # create a new xml file
            self.create_xml_file(i)

        Button(self.window_2, text="Next", width='20', height='2',
               command=lambda: self.window_3_(i), bg="#349cbc", fg='gray92').place(x=900, y=700)

    def window_3_(self, num_layer):
        """"Component and Dimension details in Window"""
        self.window_2.withdraw()
        window_3 = Toplevel(self.master)
        self.window_3 = window_3
        window_3.geometry("1500x800")
        Label(window_3, text="Layer Name:").place(x=15, y=10)
        Label(window_3, text=self.xml_layer).place(x=15, y=40)
        Label(window_3, text="Component number: ").place(x=400, y=65)
        option = [i for i in range(self.extra_fields)]
        self.select_c_number = StringVar()
        self.select_c_number.set(option[0])
        drop = OptionMenu(window_3, self.select_c_number, *option)
        if (self.existing_layer[num_layer]['components']):
            print("component lengtyh", len(self.existing_layer[num_layer]['components']))
            self.ok_component()
            if (len(self.existing_layer[num_layer]['components'])) > self.extra_fields:
                num_component = 5
            else:
                num_component = len(self.existing_layer[num_layer]['components'])
            self.select_c_number.set(num_component)
        else:
            # create a new component

            Button(self.window_3, text="OK", command=lambda: self.ok_component()).place(x=850, y=65)
            drop.place(x=790, y=65)
        # Button(self.window_3, text="Previous", width='10', height='2',
        #        command=lambda: [self.window_3.destroy(), self.master.deiconify(), self.set_existing_layer(0)],
        #        font=("Arial", 10, "bold")).place(x=100, y=700)

    def ok_component(self):
        self.lst_dimen_label = []

        window_3 = self.window_3
        number = self.select_c_number.get()
        if os.path.isfile(self.component_temp_path):
            os.remove(self.component_temp_path)
        if len(self.component_labels) != 0:
            for label in self.component_labels:
                label.destroy()
            for but in self.component_buttons:
                but.destroy()
        # if len(self.dimension_labels) != 0:
        #     for lst_label in self.dimension_labels:
        #         for label in lst_label:
        #             label.destroy()
        #     for lst_button in self.dimension_buttons:
        #         for button in lst_button:
        #             button.destroy()
        #     # todo
        #     # chekidot
        #     for dimen_num in self.lst_d_number:
        #         dimen_num.destroy()
        #     for d_label in self.lst_dimen_label:
        #         d_label.destroy()
        if self.select_c_number.get() in ["", " "]:
            number = 0
        # delete all the label and text that is above that
        c_label = {}
        c_button = {}
        dimension_label = {}

        Label(window_3,
              text="*Components and Dimension should be filled \n"
                   "in sequence (ie: First, Second, Third, and so on)",
              font=("Arial Bold", 8)).place(
            x=900, y=10)
        for i in range(int(number)):
            c_label[i] = Label(window_3, text="Component {0}: ".format(i + 1))
            c_label[i].place(x=15, y=(i + 1) * 70 + 60)
            c_button[i] = Button(window_3, text='Info',
                                 command=lambda j=i: self.open_component_window(j))

            c_button[i].place(x=200, y=(i + 1) * 70 + 60)
            self.component_labels.append(c_label[i])
            self.component_buttons.append(c_button[i])
            # dimension_label[i]= Label(self.window_3 , text="Dimension Number: ")
            # dimension_label[i].place(x=400, y=(i + 1) * 70 + 65)
            # self.d_number[i] = StringVar()
            # option=[num for num in range(self.extra_fields)]
            # self.d_number[i].set(option[0])
            # drop_dimension=OptionMenu(window_3, self.d_number[i], *option)
            # if self.existing_layer[self.num_layer]["components"] and self.existing_layer[self.num_layer]["components"]["dimension"] :
            #     print("here  dscs",self.existing_layer[self.num_layer]["components"])
            #     print("dsdsd",self.existing_layer[self.num_layer]["components"]["dimension"])
            #     #do something
            #     pass
            # else :
            #     drop_dimension.place(x=550, y=(i + 1) * 70 + 65)
            #     print("here  dscs", self.existing_layer[self.num_layer]["components"])
            #     self.d_number[i]=Button(self.window_3, text="OK", command=lambda j=i:self.create_dimension(j)).place(x=600, y=(i + 1) * 70 + 65)
            #
            #     #print("dsdsd", self.existing_layer[self.num_layer]["components"]["dimension"])
            #     self.lst_d_number.append(self.d_number[i])
            #     self.lst_dimen_label.append(dimension_label[i])
            #     # if there is component but no dimension or no component no dimension

    def open_component_window(self, num_layer):

        component_window = Toplevel(self.window_3)  # Child window
        self.component_window = component_window
        component_window.geometry("1500x500")
        component_window.title("Component Details")
        self.component_left_frame()
        # self.component_right_frame()
        Button(self.window_3, text="Previous", width='10', height='2',
               command=lambda: [self.window_3.destroy(), self.window_2.deiconify()],
               font=("Arial", 10, "bold")).place(x=100, y=700)
        pass

    def component_left_frame(self):
        """
        Component core fields text
        """
        LFrame = self.component_window
        Label(LFrame, text="1. Component Fields (Not Mandatory)\n"
                           "(GIS Field Name)", font=("Arial Bold", 9)).place(x=15, y=10)

        Label(LFrame, text="Component Label*").place(x=15, y=50)
        Label(LFrame, text="Component Type*").place(x=15, y=80)
        Label(LFrame, text="Dimension Unit").place(x=15, y=110)
        Label(LFrame, text="Network Measure").place(x=15, y=140)
        Label(LFrame, text="Design Life").place(x=15, y=170)
        Label(LFrame, text="Material Type").place(x=15, y=200)

        if self.existing_layer[self.num_layer]["components"] and len(
                self.existing_layer[self.num_layer]["components"]["corefields"].items() != 0):
            print("here i see u have compoent corefieds")
            existing_component = self.existing_layer[self.num_layer]["components"]["corefields"]
            self.c_label_field = ttk.Combobox(LFrame, values=[existing_component["label"]], width=40)
            self.c_type_field = ttk.Combobox(LFrame, values=[existing_component["component_type"]], width=40)
            self.c_dimension_unit_field = ttk.Combobox(LFrame, values=[existing_component["dimension_unit"]], width=40)
            self.c_network_measure_type_field = ttk.Combobox(LFrame,
                                                             values=[existing_component["network_measure_type"]],
                                                             width=40)
            self.c_material_type_field = ttk.Combobox(LFrame, values=[existing_component["material_type"]], width=40)
            self.c_design_life_field = ttk.Combobox(LFrame, values=[existing_component["design_life"]], width=40)
            self.c_label_field.current(0)
            self.c_type_field.current(0)
            self.c_dimension_unit_field.current(0)
            self.c_network_measure_type_field.current(0)
            self.c_material_type_field.current(0)
            self.c_design_life_field.current(0)
        else:
            self.c_label_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_dimension_unit_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_network_measure_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_material_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_design_life_field = ttk.Combobox(LFrame, values=self.fields, width=40)
        self.c_label_field.place(x=250, y=50)
        self.c_type_field.place(x=250, y=80)
        self.c_dimension_unit_field.place(x=250, y=110)
        self.c_network_measure_type_field.place(x=250, y=140)
        self.c_design_life_field.place(x=250, y=170)
        self.c_material_type_field.place(x=250, y=200)

    def component_right_frame(self):
        RFrame = self.component_window
        Label(RFrame, text="1. Component Defaults (Not Mandatory)\n"
                           "(Hardcoded value)",
              font=("Arial Bold", 9)).place(x=850, y=10)
        Label(RFrame, text="Component Label*").place(x=850, y=50)
        Label(RFrame, text="Component Type*").place(x=850, y=80)
        Label(RFrame, text="Dimension Unit").place(x=850, y=110)
        Label(RFrame, text="Network Measure").place(x=850, y=140)
        Label(RFrame, text="Design Life").place(x=850, y=170)
        Label(RFrame, text="Material Type").place(x=850, y=200)
        if self.existing_layer[self.num_layer]["components"] and self.existing_layer[self.num_layer]["components"][
            "coredefaults"] and len(
                self.existing_layer[self.num_layer]["components"]['coredefaults'].items()) != 0:
            existing_component = self.existing_layer[self.num_layer]["components"]["coredefaults"]

        self.c_label_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_label_default.place(x=1100, y=50)
        self.c_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_type_default.place(x=1100, y=80)
        self.c_dimension_unit_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_dimension_unit_default.place(x=1100, y=110)
        self.c_network_measure_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_network_measure_type_default.place(x=1100, y=140)
        self.c_design_life_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_design_life_default.place(x=1100, y=170)
        self.c_material_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.c_material_type_default.place(x=1100, y=200)

    def create_dimension(self, i):

        pass

    def check_asset_class_subclass(self):
        self.xml_asset_class_field_default = None
        self.xml_asset_class_field = None
        self.xml_asset_subclass_field = None
        self.xml_asset_subclass_field_default = None
        error = 0

        if self.asset_class_field.get() in ["", ' '] and self.asset_class_field_default.get() in ["", ' ']:
            xml_asset_class = None
        # AssetClass in  Core Default is not Null, it should exist in (assetic UI)
        elif self.asset_class_field_default.get() and self.asset_class_field_default.get() not in [" ", '']:
            xml_asset_class = self.asset_class_field_default.get()
            self.xml_asset_class_field_default = xml_asset_class

            if xml_asset_class not in self.asset_class_list:
                error = 1
                messagebox.showerror('Error', 'Asset Class in Core Default does not exist')
                return error
            elif self.asset_subclass_not_found:
                error = 1
                messagebox.showerror('Error', 'Asset SubClass in Core Default not found')
                return error
            # if asset class is in core fields is not null , it should exist in GIS table
            if self.asset_class_field.get() and self.asset_class_field.get() not in [" ", '']:
                xml_asset_class = self.asset_class_field.get()
                self.xml_asset_class_field = xml_asset_class
                if xml_asset_class and xml_asset_class not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset Class Fields in Core Fields does not exist')
                    return error

        # Asset Class in core fields is not Null but asset class in core defaults is null, then Asset Class in core fields  should exist in GIS table
        elif self.asset_class_field.get():
            self.xml_asset_class_field_default = None
            xml_asset_class = self.asset_class_field.get()
            self.xml_asset_class_field = xml_asset_class
            if xml_asset_class and xml_asset_class not in self.fields:
                error = 1
                messagebox.showerror('Error', 'Asset Class Fields in Core Fields does not exist')
                return error
        # Asset Subclass equals to Null in both fields
        if self.asset_subclass_field.get() in ["", ' '] and self.asset_subclass_field_default.get() in ["",
                                                                                                        ' ']:
            xml_asset_subclass = None
        # Asset Subclass in Core Defaults is not Null, it should exist in assetic UI
        elif self.asset_subclass_field_default.get() and self.asset_subclass_field_default.get() not in [" ", ""]:
            xml_asset_subclass = self.asset_subclass_field_default.get()
            self.xml_asset_subclass_field_default = self.asset_subclass_field_default.get()
            if xml_asset_subclass not in self.asset_subclass_list:
                error = 1
                messagebox.showerror('Error', 'Asset SubClass in Core Default does not exist')
                return error
            # Asset Subclass in Core Defaults and Core Fields are not Null, Asset Subclass in Core Fields should exist in GIS Table
            if self.asset_subclass_field.get() and self.asset_subclass_field.get() not in [" ", ""]:
                xml_asset_subclass = self.asset_subclass_field.get()
                self.xml_asset_subclass_field = self.asset_subclass_field.get()
                if xml_asset_subclass not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset SubClass Fields in Core Fields does not exist')
                    return error
            else:
                self.xml_asset_subclass_field = None


        # Asset Subclass in Core Fields is not Null and Asset Subclass in core defaults is null,Asset Subclass in Core Fields should exist in GIS Table
        else:
            self.xml_asset_subclass_field_default = None
            xml_asset_subclass = self.asset_subclass_field.get()
            self.xml_asset_subclass_field = self.asset_subclass_field.get()
            if xml_asset_subclass not in self.fields:
                error = 1
                messagebox.showerror('Error', 'Asset SubClass Fields in Core Fields does not exist')
                return error

        # Asset class and Asset Subclass should either be None or not None together
        if xml_asset_class is None and xml_asset_subclass is not None:
            error = 1
            messagebox.showerror('Error', 'Asset Class need to select to save Asset SubClass')
            return error
        if xml_asset_class is not None and xml_asset_subclass is None:
            error = 1
            messagebox.showerror('Error', 'Asset SubClass need to select to save Asset Class')
            return error
        if not error:
            error = 0
            return error

    def check_asset_type_subtype(self):
        error = 0
        self.xml_asset_subtype_field_default = None
        self.xml_asset_type_field_default = None
        self.xml_asset_type_field = None
        self.xml_asset_subtype_field = None
        print("lf.asset_type_field.gef", self.asset_type_field)
        if self.asset_type_field.get() in ["", ' '] and self.asset_type_field_default.get() in ["", ' ']:
            xml_asset_type = None

        # Asset Type is not Null in Core Default, it should exist in core defaults (assetic UI)
        elif self.asset_type_field_default.get() and self.asset_type_field_default.get() not in ["", ' ']:
            xml_asset_type = self.asset_type_field_default.get()
            self.xml_asset_type_field_default = xml_asset_type
            if xml_asset_type not in self.asset_types_list:
                error = 1
                messagebox.showerror('Error', 'Asset Type in Core Default does not exist')
                return error
            elif self.asset_subtype_not_found:
                error = 1
                messagebox.showerror('Error', 'Asset SubType in Core Default not found')
                return error
            # if Asset Type is in core fields is not null and  Asset Type in Core Default is not Null, Asset Type in Core Default should exist in GIS table
            if self.asset_type_field.get() and self.asset_type_field.get() not in ["", ' ']:
                xml_asset_type = self.asset_type_field.get()
                self.xml_asset_type_field = xml_asset_type
                if xml_asset_type and xml_asset_type not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset Type Fields in Core Fields does not exist')
                    return error
        # Asset Type in core fields is not Null, it should exist in GIS table
        elif self.asset_type_field.get():
            xml_asset_type = self.asset_type_field.get()
            self.xml_asset_type_field = xml_asset_type
            if xml_asset_type and xml_asset_type not in self.fields:
                error = 1
                messagebox.showerror('Error', 'Asset Type Fields in Core Fields does not exist')
                return error

        # Asset SubType equals to Null in both fields
        if self.asset_subtype_field.get() in ["", ' '] and self.asset_subtype_field_default.get() in ["",
                                                                                                      ' ']:
            xml_asset_subtype = None
        # Asset SubType in Core Defaults is not Null, it should exist in assetic UI
        elif self.asset_subtype_field_default.get() and self.asset_subtype_field_default.get() not in [" ", ""]:
            xml_asset_subtype = self.asset_subtype_field_default.get()
            self.xml_asset_subtype_field_default = self.asset_subtype_field_default.get()
            if xml_asset_subtype not in self.asset_subtype_list:
                error = 1
                messagebox.showerror('Error', 'Asset SubType in Core Default does not exist')
                return error
                # Asset Subtype in Core Defaults and Core Fields are not Null, Asset Subclass in Core Fields should exist in GIS Table
            if self.asset_subtype_field.get() and self.asset_subtype_field.get() not in [" ", ""]:
                xml_asset_subtype = self.asset_subtype_field.get()
                self.xml_asset_subtype_field = self.asset_subtype_field.get()
                if xml_asset_subtype not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset SubType Fields in Core Fields does not exist')
                    return error
            else:
                self.xml_asset_subtype_field = None

        # Asset SubType in Core Fields is not Null, it should exist in GIS Table
        else:
            self.xml_asset_subtype_field_default = None
            xml_asset_subtype = self.asset_subtype_field.get()
            self.xml_asset_subtype_field = self.asset_subtype_field.get()
            if xml_asset_subtype not in self.fields:
                error = 1
                messagebox.showerror('Error', 'Asset SubType Fields in Core Fields does not exist')
                return error

        # Asset Type and Asset SubType should either be None or not None together
        if xml_asset_type is None and xml_asset_subtype is not None:
            error = 1
            messagebox.showerror('Error', 'Asset Type need to select to save Asset SubType')
            return error
        if xml_asset_type is not None and xml_asset_subtype is None:
            error = 1
            messagebox.showerror('Error', 'Asset SubType need to select to save Asset Type')
            return error
        if not error:
            error = 0
            return error
        return 0

    def edit_existing_xml_file(self, num_layer):
        cur_layer = 1

        if self.existing_layer:
            filesize = os.path.getsize(self.asset_temp_path[0])
            if filesize == 0:
                # if there is no temporary file to look at , then use the saved file
                tree = ET.parse(self.save_path)
                print("no temporary")
            else:
                # if temporary data exist(layer that has been editted and place to a new file), then use the editted data
                tree = ET.parse(self.asset_temp_path[0])
                print("yes there is something")

            root = tree.getroot()
            # check if there is a layer name
            for operation in root.iter('operation'):
                action = operation.get("action")
                if action == "Asset":

                    for onelayer in operation.iter("layer"):
                        if cur_layer == num_layer:
                            layer_name = onelayer.get("name")
                            onelayer.set('name', self.xml_layer)
                            category = onelayer.find('category')
                            if onelayer.find('category') is None:
                                category = ET.SubElement(onelayer, "category")
                            category.text = self.xml_category
                            corefields = onelayer.find('corefields')
                            if corefields is None:
                                corefields = ET.SubElement(onelayer, "corefields")
                            if self.xml_asset_ID:
                                asset_id_core_fields = corefields.find("asset_id")
                                if asset_id_core_fields is None:
                                    asset_id_core_fields = ET.SubElement(corefields, "asset_id")
                                asset_id_core_fields.text = self.xml_asset_ID
                            if self.xml_asset_name_core_field:
                                asset_name_core_fields = corefields.find("asset_name")
                                if asset_name_core_fields is None:
                                    asset_name_core_fields = ET.SubElement(corefields, "asset_name")
                                asset_name_core_fields.text = self.xml_asset_name_core_field

                            if self.xml_asset_GUID_core_field:
                                asset_GUID_core_fields = corefields.find("id")
                                if asset_GUID_core_fields is None:
                                    asset_GUID_core_fields = ET.SubElement(corefields, "id")
                                asset_GUID_core_fields.text = self.xml_asset_GUID_core_field

                            if self.xml_asset_class_field:
                                asset_class_core_fields = corefields.find("asset_class")
                                if asset_class_core_fields is None:
                                    asset_class_core_fields = ET.SubElement(corefields, "asset_class")
                                asset_class_core_fields.text = self.xml_asset_class_field
                            if self.xml_asset_subclass_field:
                                asset_subclass_core_fields = corefields.find("asset_sub_class")
                                if asset_subclass_core_fields is None:
                                    asset_subclass_core_fields = ET.SubElement(corefields, "asset_sub_class")
                                asset_subclass_core_fields.text = self.xml_asset_subclass_field
                            if self.xml_asset_type_field:

                                asset_type_core_fields = corefields.find("asset_type")
                                if asset_type_core_fields is None:
                                    asset_type_core_fields = ET.SubElement(corefields, "asset_type")
                                asset_type_core_fields.text = self.xml_asset_type_field
                            if self.xml_asset_subtype_field:
                                asset_subtype_core_fields = corefields.find("asset_sub_type")
                                if asset_subtype_core_fields is None:
                                    asset_subtype_core_fields = ET.SubElement(corefields, "asset_sub_type")
                                asset_subtype_core_fields.text = self.xml_asset_subtype_field
                            coredefaults = onelayer.find('coredefaults')
                            if coredefaults is None:
                                coredefaults = ET.SubElement(onelayer, "coredefaults")
                            if self.xml_asset_name_core_default:
                                asset_name_core_default = coredefaults.find("asset_name")
                                if asset_name_core_default is None:
                                    asset_name_core_default = ET.SubElement(coredefaults, "asset_name")
                                asset_name_core_default.text = self.xml_asset_name_core_default
                            if self.xml_asset_class_field_default:
                                asset_class_core_default = coredefaults.find("asset_class")
                                if asset_class_core_default is None:
                                    asset_class_core_default = ET.SubElement(coredefaults, "asset_class")
                                asset_class_core_default.text = self.xml_asset_class_field_default
                            if self.xml_asset_subclass_field_default:
                                asset_subclass_core_default = coredefaults.find("asset_sub_class")
                                if asset_subclass_core_default is None:
                                    asset_subclass_core_default = ET.SubElement(coredefaults, "asset_sub_class")
                                asset_subclass_core_default.text = self.xml_asset_subclass_field_default
                            if self.xml_asset_type_field_default:
                                asset_type_core_default = coredefaults.find("asset_type")
                                if asset_type_core_default is None:
                                    asset_type_core_default = ET.SubElement(coredefaults, "asset_type")
                                asset_type_core_default.text = self.xml_asset_type_field_default
                            if self.xml_asset_subtype_field_default:
                                asset_subtype_core_default = coredefaults.find("asset_sub_type")
                                if asset_subtype_core_default is None:
                                    asset_subtype_core_default = ET.SubElement(coredefaults, "asset_sub_type")
                                asset_subtype_core_default.text = self.xml_asset_subtype_field_default

                                # create a new tag for core fields

                            # print("category", category.text)

                        cur_layer += 1
            dom = xml.dom.minidom.parseString(ET.tostring(root))
            xml_string = dom.toprettyxml()
            dom_string = b'\n'.join([s for s in xml_string.splitlines() if s.strip()])
            # put this one a file called arcmap_edit_config0.xml
            with open(self.asset_temp_path[0], "wb") as f:
                f.write(dom_string)
                f.close()

            # finding the state tag and their child attributes.
            # for state in root.findall('state'):
            #     rank = state.find('rank').text
            #     name = state.get('name')
            #     print(name, rank)

    def create_xml_file(self, i):
        """create a new xml file if the user choose create a new xml file
        param i: the nth layer"""
        m_encoding = 'UTF-8'
        # root element
        root = ET.Element("asseticconfig", {'name': 'ESRI'})
        logfile = ET.SubElement(root, "logfile")
        logfile.text = self.logfile
        loglevelname = ET.SubElement(root, "loglevel")
        loglevelname.text = self.loglevelname
        bulk_threshold = ET.SubElement(root, "bulk_threshold")
        bulk_threshold.text = self.bulk_threshold
        operation = ET.SubElement(root, "operation", action="Asset")
        layer = ET.SubElement(operation, "layer", name=self.xml_layer)
        category = ET.SubElement(layer, "category")
        category.text = self.xml_category
        creation_status = ET.SubElement(layer, "creation_status")
        creation_status.text = self.creation_status
        upload_feature = ET.SubElement(layer, "upload_feature")
        upload_feature.text = self.upload_feature
        resolve_lookups = ET.SubElement(layer, "resolve_lookups")
        resolve_lookups.text = self.resolve_lookups
        # Core Defaults
        coredefaults = ET.SubElement(layer, 'coredefaults')
        # Core Fields
        corefields = ET.SubElement(layer, 'corefields')
        asset_id = ET.SubElement(corefields, "asset_id")
        asset_id.text = self.xml_asset_ID
        # only GUID in core fields one that will be written
        asset_guid = ET.SubElement(corefields, 'id')
        asset_guid.text = self.xml_asset_GUID_core_field

        if self.xml_asset_name_core_default is not None:
            asset_name = ET.SubElement(coredefaults, "asset_name")
            asset_name.text = self.xml_asset_name_core_default
        if self.xml_asset_name_core_field is not None:
            asset_name = ET.SubElement(corefields, "asset_name")
            asset_name.text = self.xml_asset_name_core_field
        # if asset class in core default
        if self.xml_asset_class_field_default is not None:
            asset_class = ET.SubElement(coredefaults, "asset_class")
            asset_class.text = self.xml_asset_class_field_default

        # if asset class in core fields
        if self.xml_asset_class_field is not None:
            asset_class = ET.SubElement(corefields, "asset_class")
            asset_class.text = self.xml_asset_class_field
        # if asset subclass in core defaults
        if self.xml_asset_subclass_field_default is not None:
            asset_subclass = ET.SubElement(coredefaults, "asset_sub_class")
            asset_subclass.text = self.xml_asset_subclass_field_default
        # if asset subclass in coredefaults
        if self.xml_asset_subclass_field is not None:
            asset_subclass = ET.SubElement(corefields, "asset_sub_class")
            asset_subclass.text = self.xml_asset_subclass_field

        # if asset type in core defaults
        if self.xml_asset_type_field_default is not None:
            asset_type = ET.SubElement(coredefaults, "asset_type")
            asset_type.text = self.xml_asset_type_field_default

        # if asset type in core fields
        if self.xml_asset_type_field is not None:
            asset_type = ET.SubElement(corefields, "asset_type")
            asset_type.text = self.xml_asset_type_field
        # if asset subtype in core defaults
        if self.xml_asset_subtype_field_default is not None:
            asset_subtype = ET.SubElement(coredefaults, "asset_sub_type")
            asset_subtype.text = self.xml_asset_subtype_field_default
        # if asset subtype in core fields
        elif self.xml_asset_subtype_field is not None:
            asset_subtype = ET.SubElement(corefields, "asset_sub_type")
            asset_subtype.text = self.xml_asset_subtype_field

        dom = xml.dom.minidom.parseString(ET.tostring(root))
        xml_string = dom.toprettyxml()

        with open(self.asset_temp_path[int(i - 1)], "w") as f:
            f.write(xml_string)
            f.close()

    @staticmethod
    def layer(gdbfile):
        arcpy.env.workspace = gdbfile
        tables = arcpy.ListFeatureClasses()
        if not tables:
            msg = ("Either the file is empty or no feature of classes found for {0} file").format(gdbfile)
            print(msg)
            return
        layer_option = [layer for layer in tables]
        # empty layer
        if not layer_option:
            msg = ("No Feature of Classes found for {0}").format(gdbfile)
            print(msg)
            return
        layer_dict = {}
        # count to be deleted
        count = 0
        for one_layer in layer_option:
            count += 1
            featureclass = os.path.join(gdbfile, one_layer)
            layer_dict[one_layer] = [f.name for f in arcpy.ListFields(featureclass)]
            if count == 10:
                break;
        return layer_dict


class XMl_Prompter_for_component:
    extra_fields = 6
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)
    component_temp_path = os.environ['APPDATA'] + '\\Assetic\\component.xml'
    merged_temp_path = os.environ['APPDATA'] + '\\Assetic\\merged_arcmap_edit_config.xml'

    def __init__(self, master, layer_dict=None):
        self.master = master
        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter for Component")
        master.geometry("1500x800")
        master.header = Label(master, text="XML Prompter for Component", font=("Arial", 40, "bold")).place(x=600, y=80)
        if os.path.exists(self.save_path):
            message = "arcmap_edit_config.xml file already exists in \n" \
                      "{0} ".format(self.save_path)
            Button(master, text="Continue with existing file", width='20', height='2',
                   command=lambda: self.continue_file(), bg="#349cbc", fg='gray92').place(
                x=700,
                y=500)
            Button(master, text="Start", width='20', height='2',
                   command=lambda: self.window_1_(), bg="#349cbc", fg='gray92').place(
                x=700,
                y=600)
        else:
            message = "XML Prompter for asset should be run first"
            # print("message")
            # messagebox.showerror("Error", message)

        Label(master, text=message).place(x=550, y=300)




if __name__ == '__main__':
    assetic.AsseticSDK(None, None, "info")

    gdbfile = r"C:\Users\cynthia\Downloads\Town of Walkerville Assets.gdb"
    layer = XMl_Prompter.layer(gdbfile)
    root = tk.Tk()
    prompter = XMl_Prompter(root, layer_dict=layer)
    # prompter.layer = gdbfile
    root.mainloop()
