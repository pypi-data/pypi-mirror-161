"""
https://stackoverflow.com/questions/33646605/how-to-access-variables-from-different-classes-in-tkinter
"""

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from tkinter import messagebox
from tkinter import ttk

#import arcpy

import xml.etree.ElementTree as ET
import struct   # use for unicode symbol packing
import assetic
import xml.dom.minidom
from assetic.api_client import ApiClient
#from assetic.api import AssetConfigurationApi
#from assetic.rest import ApiException
import os


class SampleApp(tk.Tk):

    def __init__(self, layer_dict):
        self.layer_dict = layer_dict

        tk.Tk.__init__(self)

        self.common_tools = CommonTools()
        self.layer_option = sorted(
            self.layer_dict.keys(), key=lambda x: x.lower())

        menu_container = tk.Frame(self,bg="#349cbc")
        menu_container.pack(side="left", fill=tk.BOTH, expand=False)
        menu_container.grid_rowconfigure(0, weight=0)
        menu_container.grid_columnconfigure(0, weight=0)

        container = tk.Frame(self)
        container.pack(side="right", fill=tk.BOTH, expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        self.container = container

        self.frames = {}
        mf = MenuFrame(menu_container, self)
        mf.grid(row=0, column=0, sticky="nsew")
        self.frames[MenuFrame] = mf
        self.show_frame(MenuFrame)

        for F in (StartPage, LayerFrame):
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=1, sticky="nsew")
        self.show_frame(LayerFrame)

    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()

    def refresh_frame(self, c):
        frame = self.frames[c]
        frame.refresh(parent=self.container, controller=self)
        frame.grid(row=0, column=1, sticky="nsew")

    def get_existing_xml(self):
        return self.common_tools.get_existing_xml()

    def save_layer_info(self, curr_layer, layer_name, delete=0):
        self.common_tools.save_layer_info(
            curr_layer=curr_layer, delete=delete, layer_name=layer_name)


class MenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.existing_layer = None
        self.layer_dict = dict()
        self.controller = controller

        # Add buttons to initiate each level of configuration
        tk.Button(self, text="Layer", width='30',
                  height='2',
                  command=lambda: self.load_layer_frame(),
                  bg="#349cbc", borderwidth=0,
                  fg='gray92').grid(row=0, column=0)

        tk.Button(self, text="Asset Core Attributes", width='30', height='2',
               command=lambda: self.asset_window_1_(),
               bg="#349cbc", borderwidth=0,
               fg='gray92').grid(row=1, column=0)
        tk.Button(self, text="Component", width='30', height='2',
               command=lambda: self.component_window_1_(),
               bg="#349cbc", borderwidth=0,
               fg='gray92').grid(row=2, column=0)
        tk.Button(self, text="Dimensions", width='30', height='2',
               command=lambda: self.dimension_window_1_(),
               bg="#349cbc", borderwidth=0,
               fg='gray92').grid(row=3, column=0)

    def load_layer_frame(self):
        self.existing_layer = self.controller.get_existing_xml()
        self.controller.refresh_frame(LayerFrame)
        #prompter = XML_Prompter_for_Layer(
        #    self.master, layer_dict=self.layer_dict,
        #    existing_layer=self.existing_layer)

    def asset_window_1_(self):
        self.existing_layer = self.controller.get_existing_xml()
        #prompter = XMl_Prompter_for_Asset(
        #    self.master, layer_dict=self.layer_dict,
        #    existing_layer=self.existing_layer)

    def component_window_1_(self):
        self.existing_layer = self.controller.get_existing_xml()
        #prompter = XMl_Prompter_for_Component(
        #    self.master, layer_dict=self.layer_dict,
        #    existing_layer=self.existing_layer)


    def dimension_window_1_(self):
        self.existing_layer = self.controller.get_existing_xml()
        #prompter = XMl_Prompter_for_Dimension(
        #    self, layer_dict=self.layer_dict,
        #    existing_layer=self.existing_layer)


class LayerFrame(tk.Frame):

    def __init__(self, parent, controller, use_existing_file=True):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.delete_label = {}
        self.use_existing_file = use_existing_file
        self.l_button = {}
        self.delete_button = {}
        self.existing_layer = controller.get_existing_xml()
        self.extra_fields = 6
        tk.Label(self, text="Layers to configure: ", font=("Arial Bold",
                                                         12)).grid(
            row=0, column=1)

        tk.Label(self, text="Layer: ", font=("Arial Bold", 12)).grid(
            row=1, column=1)

        row_num = 2

        # if user use existing file and it contains a layer
        if use_existing_file == 1:

            #if in existing layer is not None and contain layer
            if self.existing_layer and (len(self.existing_layer)) > 0:

                if (len(self.existing_layer)) > self.extra_fields:
                    num_layer = self.extra_fields
                else:
                    # if contain layer and maximum
                    num_layer = len(self.existing_layer)
                count = 1
                y_start = 130
                for j in range(1, num_layer + 1):
                    k = j
                    self.delete_label[j] = tk.Label(
                        self, text='',
                        font=("Arial", 12), borderwidth=0)
                    self.l_button[j] = tk.Button(self,
                                              text='{1}'.format(j,
                                                                self.existing_layer[
                                                                    j][
                                                                    "layer_name"]),
                                              height=1,
                                              width=30, font='Arial 12',
                                              anchor="w", borderwidth=0,
                                              command=lambda
                                                  curr_layer=j: self.button_new_exec(
                                                  curr_layer, curr_layer,
                                                  self.controller.layer_option))
                    self.delete_button[j] = tk.Button(
                        self
                        , text=struct.pack('i', 10062).decode('utf-32')
                        , height=1, width=2, font='Arial 12 bold', fg="red"
                        , borderwidth=0
                        , command=lambda curr_layer=j:
                        self.delete_layer_button_exec(
                            curr_layer, curr_layer))
                    if k > 7:

                        self.l_button[k].place(x=60 + count * 300,
                                               y=(k - 7 * count) * 60 + 180)
                        self.delete_label[k].place(x=60 + count * 300,
                                                   y=(k - 7 * count) * 60 + 180)
                        self.delete_button[k].place(x=280 + count * 300,
                                                    y=(k - 7 * count) * 60 + 180)
                        if k % 7 == 0:
                            count += 1
                    else:
                        self.l_button[j].grid(row=row_num, column=1)
                        self.delete_button[j].grid(row=row_num, column=2)
                        self.delete_label[j].grid(row=row_num, column=1)

                        row_num += 1

                option = [k for k in
                          range(self.extra_fields - len(self.existing_layer))]
                if option:
                    self.max_num = max(option) + 1
                    self.add_layer_button(curr_layer=j, row_num=row_num)

            else:
                # if user use existing file but no layer is detected then make
                # it add layer
                option = [k for k in range(self.extra_fields)]
                self.max_num = max(option) + 1
                curr_layer = 0
                self.add_layer_button(curr_layer=curr_layer, row_num=row_num)

        else:
            option = [k for k in range(self.extra_fields)]
            self.max_num = max(option) + 1
            curr_layer = 0
            self.add_layer_button(curr_layer=curr_layer, row_num=row_num)
        #tk.Button(self, text="Close", width='15', height='2',
        #       command=lambda: self.window_1.destroy(), bg="#349cbc",
        #       fg='gray92').place(x=self.width - 200, y=self.height - 100)
        # Button(self.window_1, text="Next", width='10', height='2',command=lambda : self.asset_prompter(), bg="#349cbc", fg='gray92').place(x=800, y=700)

    def refresh(self, parent, controller, use_existing_file=True):
        self.destroy()
        self.__init__(parent, controller, use_existing_file)

    def add_layer_button(self, curr_layer, row_num):

        number = self.max_num
        self.l_button_new = {}
        self.label_button = {}
        count = (curr_layer) / 7
        start = 0
        self.m = 1
        for m in range(1, int(number) + 1):
            k = m + curr_layer
            self.label_button[m] = tk.Label(self, text='',
                                           font='Arial 12')
            self.l_button_new[m] = tk.Button(self, text='', height=1,
                                          width=10, font='Arial 12', bd=0,
                                          command=lambda j=m: self.button_new_exec(
                                              curr_layer + j, j,
                                              self.controller.layer_option))

            if k > 7:

                self.label_button[m].place(row=row_num, column=3)
                self.l_button_new[m].place(row=row_num, column=3)
                if start == 0:
                    self.l_button_new[m].configure(bd=1, text="Add layer")
                    start += 1
            else:
                self.label_button[m].grid(row=row_num, column=1)
                self.l_button_new[m].grid(row=row_num, column=1)
                row_num += 1
                if start == 0:
                    self.l_button_new[m].configure(bd=1, text="Add layer")
                    start += 1

            if k % 7 == 0:
                count += 1
                row_num = 2

    def button_new_exec(self,layer,button_index, layer_option):
        self.window_2_(layer, button_index, layer_option)

    def window_2_(self, curr_layer, button_index, layer_option):

        """
        param:
        button_index: to keep track of add layer button.(make it visible)
        """

        """window 2 for Asset form"""
        window_2 = tk.Toplevel(self.master)
        self.window_2 = window_2
        self.layer_option = layer_option
        window_2.title("Assetic XML Prompter")
        window_2.geometry("900x400")
        tk.Label(window_2, text="Layer name").place(x=20, y=70)
        tk.Label(window_2,
              text="Once saved button is clicked, the existing "
                   "configuration will be modified",
              fg="red", font='Arial 12 underline').place(x=20, y=200)

        if self.use_existing_file and self.existing_layer:

            # if user use existing file and existing file is not None
            try:

                one_layer = self.existing_layer[curr_layer]
                self.layer_name = ttk.Combobox(window_2, values=[
                    one_layer["layer_name"]], width=40)
                self.layer_name.current(0)
                self.layer_name.config(value=self.layer_option)
            except KeyError:
                self.layer_name = ttk.Combobox(window_2,
                                               values=self.layer_option,
                                               width=40)
            self.layer_name.place(x=250, y=70)

        else:

            self.layer_name = ttk.Combobox(window_2,
                                           values=self.layer_option,
                                           width=40)
            self.layer_name.current(0)
            self.layer_name.place(x=250, y=70)
        self.button_save = tk.Button(
            window_2, text="Save", width='20',
            height='2',
            command=lambda:
            self.save_layer_button_exec(
                curr_layer, button_index=button_index,
                layer_name=self.layer_name),
            bg="#349cbc", fg='gray92').place(x=150, y=300)

    def save_layer_button_exec(self, curr_layer, button_index, layer_name):
            found = self.controller.save_layer_info(
                curr_layer=curr_layer, layer_name=layer_name)

            layername = self.layer_name.get()
            self.window_2.destroy()
            try:
                if found == 1:
                    # editing existing layer
                    self.l_button[button_index].grid_forget()
                    self.delete_button[button_index].grid_forget()
                    self.delete_label[button_index][
                        "text"] = '{1} edited'.format(
                        curr_layer, layername)

                else:
                    # add a new layer
                    self.label_button[button_index][
                        "text"] = '{1} added'.format(
                        curr_layer, layername)
                    self.l_button_new[button_index].grid_forget()
                    try:
                        # as long as it doesnt pass limit, then show a new
                        # add layer
                        # button
                        self.l_button_new[button_index + 1].configure(
                            bd=1, text="Add layer")
                    except:
                        pass
            except KeyError:
                # wont go here
                pass
            self.existing_layer = self.controller.get_existing_xml()

    def delete_layer_button_exec(self, curr_layer,button_index):
        self.controller.save_layer_info(
            curr_layer=curr_layer, layer_name=curr_layer
            , delete=1)
        try:
            self.l_button[button_index].grid_forget()
            self.delete_button[button_index].grid_forget()
            self.delete_label[button_index]["text"] = "{0} deleted".format(
                self.existing_layer[button_index]["layer_name"])
        except:
            pass

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="PyMail",foreground = "Red", font=("Courier", 30, "bold"))
        label.pack(side="top")
        sublabel = tk.Label(self, text="Bringing you the\n the easiest way of communication",
                            font=("Courier", 15))
        sublabel.pack()

        #wallpaper = tk.PhotoImage(file='Python-logo-notext.gif')
        #img = tk.Label(self, image=wallpaper)
        #img.image = wallpaper
        #img.pack(side="top", expand = True)

        #button1 = tk.Button(self, text="Click Here to Login to your
        # account",fg="red",
        #                    command=lambda: controller.show_frame(PageOne))
        #button2 = tk.Button(self, text="Go to Page Two",
        #                    command=lambda: controller.show_frame(PageTwo))
        #button2.pack(side="bottom")
        #button1.pack(side="bottom")


class CommonTools:
    def __init__(self):
        pass

        self.use_existing_file = True
        self.config_file_path = os.environ['APPDATA'] + \
                      '\\Assetic\\arcmap_edit_config.xml'
        self.assetic_folder = os.environ['APPDATA'] + '\\Assetic'
        if not os.path.exists(self.assetic_folder):
            os.makedirs(self.assetic_folder)
        if not os.path.exists(self.config_file_path):
            self.use_existing_file = False

        # some defaults
        self.bulk_threshold = "200"   # needs to be a strinf for xml parser
        self.loglevelname = "Info"
        self.logfile = self.assetic_folder + "\\gisintegration.log"
        self.upload_feature = "True"
        self.resolve_lookups = "False"
        self.creation_status = "Active"
        self.gis = "ESRI"
        self.existing_layer = dict()

    def get_existing_xml(self):
        """
        Read existing xml file as a dictionary
        :return: dictionary of configuration
        :rtype: dict
        """
        api_client = ApiClient()
        logger = api_client.configuration.packagelogger
        """use existing file and save it in a dictionary called self.existing_layer"""
        asset_found = 0
        save_path = self.config_file_path
        assetic_folder = self.assetic_folder

        if not os.path.exists(assetic_folder):
            logger.error("Folder {0} does not exist")
            return
        if not os.path.exists(save_path):
            logger.error("{0} not found".format(save_path))
            return

        existing_layer = {}
        filesize = os.path.getsize(save_path)
        if filesize == 0:
            logger.error("{0} file is empty. ".format(save_path))

        else:
            # check if xml valid or not
            try:
                ET.parse(save_path)
            except Exception as e:
                messagebox.showerror("Error", e.message)
                return
            data = ET.parse(save_path).getroot()
            # check if the data contain operation tag
            if len(data.findall("operation")) > 0:

                for operation in data.iter("operation"):
                    # check if action exist
                    action = operation.get("action")
                    # if action equal to asset
                    if action in ["Asset", "asset"]:
                        asset_found = 1
                        # parse the data
                    else:
                        message = "No 'Asset' attribute in 'Operation' tag "

                        logger.error(message)
                        return
                    # count the number of the layer
                    if asset_found:

                        count = 0
                        for layer in operation.iter("layer"):
                            layer_info = {}

                            core_defaults_info = {}
                            core_fields_info = {}

                            try:
                                layer_info["layer_name"] = layer.get("name")

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
                                            dimension_core_default_info['network_measure'] = dimensiondefaults.find('network_measure').text
                                        except AttributeError:
                                            dimension_core_default_info[
                                                'network_measure'] = ''
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
                                            dimension_core_fields_info['network_measure'] = dimensionfields.find('network_measure').text
                                        except AttributeError:
                                            dimension_core_fields_info['network_measure'] = ''
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

                            layer_info["coredefaults"] = core_defaults_info
                            layer_info["corefields"] = core_fields_info

                            layer_info["components"] = existing_component
                            count = count + 1
                            existing_layer[count] = layer_info
                    # if functional location operation found

            else:
                message = "'Operation' tag does not exist in the file"
                logger.error(message)
                return
            # go to next window_1
            self.existing_layer = existing_layer
            return existing_layer

    def save_layer_info(self, curr_layer, layer_name=None, delete=0):
        """
        Save the XML file
        :param curr_layer: current XML
        :type curr_layer: dict
        :param layer_name: the name of the layer being processed
        :type layer_name: string
        :param delete: 0=don't delete layer, 1=delete layer
        :type delete: int
        :return: found
        :rtype: int
        """
        found = 0
        if self.use_existing_file:

            if os.path.isfile(self.config_file_path):
                tree = ET.parse(self.config_file_path)
            else:
                messagebox.showerror("Error", "No arcmap_edit_config.xml is found")
                return
            root = tree.getroot()
            bulk_threshold = root.find("bulk_threshold")
            if bulk_threshold is None:
                # create a new one
                bulk_threshold = ET.SubElement(root, "bulk_threshold")
            bulk_threshold.text = self.bulk_threshold
            loglevel = root.find("loglevel")
            if loglevel is None:
                # create a new one
                loglevel = ET.SubElement(root, "loglevel")
            loglevel.text = self.loglevelname
            logfile = root.find("logfile")
            if logfile is None:
                logfile = ET.SubElement(root, "logfile")
            logfile.text = self.logfile
            for operation in root.iter("operation"):
                action = operation.get("action")
                # if action equal to asset
                if action in ["Asset", "asset"]:
                    operation.set("action", "Asset")
                    onelayer = operation.find("layer")

                    if onelayer is None:
                        onelayer = ET.SubElement(operation, "layer")
                    else:
                        num_layer = 1
                        found = 0
                        for onelayer in operation.iter("layer"):

                            try:
                                # find the first layer name. Use try because curr layer may be more which means user want to add layer
                                if onelayer.get("name") == self.existing_layer[curr_layer]["layer_name"]:

                                    if delete:
                                        delete_found = 1
                                        operation.remove(onelayer)
                                        break
                                    if layer_name.get() is None or layer_name.get() in [None, '', ' ']:
                                        messagebox.showerror("Error", "Layer name is missing")
                                        return
                                    found = 1
                                    # if found the layer,check if layer exist/ not
                                    all_layer = operation.findall("layer")
                                    all_layer = [i.attrib["name"] for i in all_layer]
                                    if layer_name.get() in all_layer:
                                        messagebox.showerror("Error", "Layer has already exist")
                                        return
                                    break
                                else:
                                    num_layer += 1
                            except KeyError:

                                # means adding a new layer
                                found = 0
                                # check if the newly added layer has exist in or not, if yes

                                if onelayer.get("name") == layer_name.get():
                                    messagebox.showerror("Error", "Layer name has already exist")
                                    return
                            except TypeError:
                                found = 0
                                # check if the newly added layer has exist in or not, if yes

                                if onelayer.get("name") == layer_name.get():
                                    messagebox.showerror("Error", "Layer name has already exist")
                                    return

                        if delete:
                            break
                        if found == 0:
                            # if it is adding a new layer, and layer name hasnt exist before
                            onelayer = ET.SubElement(operation, "layer")
                    if layer_name.get() is None or layer_name.get() in [None, '', ' ']:
                        messagebox.showerror("Error", "Layer name is missing")
                        return
                    onelayer.set("name", layer_name.get())
                    resolve_lookups = onelayer.find("resolve_lookups")
                    if resolve_lookups is None:
                        resolve_lookups = ET.SubElement(onelayer, "resolve_lookups")
                    resolve_lookups.text = self.resolve_lookups
                    upload_feature = onelayer.find("upload_feature")
                    if upload_feature is None:
                        upload_feature = ET.SubElement(onelayer, "upload_feature")
                    upload_feature.text = self.upload_feature
                    creation_status = onelayer.find("creation_status")
                    if creation_status is None:
                        creation_status = ET.SubElement(onelayer, "creation_status")
                    creation_status.text = self.creation_status
                # else:
                #     # for functional location
                #     pass

            dom = xml.dom.minidom.parseString(ET.tostring(root))
            xml_string = dom.toprettyxml()
            dom_string = '\n'.join([s for s in xml_string.splitlines() if s.strip()])
            # put this one a file called arcmap_edit_config0.xml
            with open(self.config_file_path, "w") as f:
                f.write(dom_string)
                f.close()
        else:
            # if not exist, create a new file

            m_encoding = 'UTF-8'
            # root element
            self.use_existing_file = 1
            root = ET.Element("asseticconfig", {'name': self.gis})

            logfile = ET.SubElement(root, "logfile")
            logfile.text = self.logfile
            loglevel = ET.SubElement(root, "loglevel")
            loglevel.text = self.loglevelname
            bulk_threshold = ET.SubElement(root, "bulk_threshold")
            bulk_threshold.text = self.bulk_threshold
            operation = ET.SubElement(root, "operation", action="Asset")
            layer = ET.SubElement(operation, "layer", name=layer_name.get())
            creation_status = ET.SubElement(layer, "creation_status")
            creation_status.text = self.creation_status
            upload_feature = ET.SubElement(layer, "upload_feature")
            upload_feature.text = self.upload_feature
            resolve_lookups = ET.SubElement(layer, "resolve_lookups")
            resolve_lookups.text = self.resolve_lookups
            dom = xml.dom.minidom.parseString(ET.tostring(root))
            xml_string = dom.toprettyxml()
            part1, part2 = xml_string.split('?>')
            # write to file
            with open(self.config_file_path, 'wb') as f:
                f.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
                f.close()
        messagebox.showinfo('Info', 'Successfully Saved')
        return found

class TestHelper:
    def __init__(self):
        pass

    @staticmethod
    def layer(gdbfile):
        pass
        """
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
        """

if __name__ == "__main__":
    assetic.AsseticSDK(None, None, "info")
    #gdbfile = r"C:\Users\cynthia\Downloads\Town of Walkerville Assets.gdb"
    #gdbfile = r"C:\Projects\TAS\tas_gdb\tasdata.gdb"
    # 1. Get layer
    testhelper = TestHelper()
    #layer = testhelper.layer(gdbfile)

    layer = {u'municipality_boundary': [u'OBJECTID', u'Shape', u'LGA_ID', u'NAME', u'LGA_CODE', u'PLAN_REF', u'GAZ_DATE', u'NOM_REG_NO', u'UFI', u'CREATED_ON', u'LIST_GUID', u'Shape_Length', u'Shape_Area']
        , u'workorders': [u'OBJECTID', u'Shape', u'Id', u'wkoguid', u'wkofriendlyid', u'assetid', u'briefdesc', u'wkostatus']
        , u'list_hydro_areas': [u'OBJECTID', u'Shape', u'HYDAREA_ID', u'HYDARTY1', u'HYDARTY2', u'NAME', u'NOM_REG_NO', u'HYD_CLASS', u'PERENNIAL', u'EXISTING', u'WC_BED_TY', u'RELGRND', u'INUSE', u'ISLANDTYPE', u'ELEVATION', u'COMP_AREA', u'UFI', u'CREATED_ON', u'LIST_GUID', u'Shape_Length', u'Shape_Area', u'LastModifiedDate']
        , u'list_transport_segments': [u'OBJECTID', u'Shape', u'TRANSEG_ID', u'TRANS_TYPE', u'zone', u'STATUS', u'traffic_dir', u'TRAN_CLASS', u'USER_TYPE', u'TOUR_CLASS', u'asset_type', u'assetname', u'PRI_NOMREG', u'SEC_NAME', u'SEC_NOMREG', u'BRIDGE_TUN', u'BRIDGE_T_1', u'AUTHORITY', u'FOREIGN_ID', u'COMP_LEN', u'UFI', u'FMP', u'CREATED_ON', u'LIST_GUID', u'assetid', u'asset_class', u'asset_subclass', u'asset_subtype', u'assetflag', u'assetguid', u'Shape_Length', u'SURFACELIFE', u'SURFACEMATERIAL', u'PAVEBASELIFE', u'PAVEBASEMATERIAL', u'Width', u'base_comp_id', u'suburb', u'base_comp_fid', u'func_loc_fid', u'field', u'func_loc_name', u'func_loc_type', u'base_comp_name', u'LastEditDate']
        , u'list_2d_building_polys': [u'OBJECTID', u'Shape', u'BUILD_ID', u'BUILD_TY', u'BUILD_NAME', u'BLD_PUR', u'MEAN_HGT', u'UFI', u'CREATED_ON', u'LIST_GUID', u'Shape_Length', u'Shape_Area', u'created_user', u'created_date', u'last_edited_user', u'last_edited_date']
        , u'list_hydro_lines': [u'OBJECTID', u'Shape', u'HYDLINE_ID', u'HYDLNTY1', u'HYDLNTY2', u'NAME', u'NOM_REG_NO', u'MHWM_TYPE', u'HYD_CLASS', u'EXISTING', u'RELGRND', u'INUSE', u'HYDCNTR_TY', u'ADJ_FEAT_1', u'ADJ_FEAT_2', u'HEIGHT', u'COMP_LEN', u'UFI', u'CREATED_ON', u'LIST_GUID', u'Shape_Length']
        , u'list_local_govt_reserve': [u'OBJECTID', u'Shape', u'CID', u'CATEGORY', u'FEAT_NAME', u'COMP_AREA', u'MEAS_AREA', u'UFI', u'FMP', u'CREATED_ON', u'LIST_GUID', u'Shape_Length', u'Shape_Area', u'GUID_FLD', u'FL_FID', u'FL_FLTYPE', u'FL_NAME', u'FL_ID']
        , u'list_parcels': [u'OBJECTID', u'Shape', u'CID', u'VOLUME', u'FOLIO', u'PID', u'POT_PID', u'LPI', u'CAD_TYPE1', u'CAD_TYPE2', u'TENURE_TY', u'FEAT_NAME', u'STRATA_LEV', u'COMP_AREA', u'MEAS_AREA', u'UFI', u'FMP', u'CREATED_ON', u'LIST_GUID', u'Shape_Length', u'Shape_Area']}

    app = SampleApp(layer_dict=layer)
    app.title("GIS Configuration Tool")
    app.geometry("600x500")
    app.mainloop()
