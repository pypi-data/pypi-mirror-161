try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import os
import xml.etree.ElementTree as ET
import assetic
import xml.dom.minidom
from arcpy import env
import struct
import logging
from tkinter import ttk
from tkinter import *
from assetic import AsseticSDK
from assetic.api_client import ApiClient
from assetic.api import WorkOrderApi, AssetApi, AssetConfigurationApi
from assetic.rest import ApiException
from tkinter import messagebox
from tkinter.messagebox import showinfo


class XML_Prompter_for_Layer:
    extra_fields = 30
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)
    empty_value = ['']

    def __init__(self, master, logfile=r"C:\temp\logfile.log", loglevelname="Debug", layer_dict=None,
                 bulk_threshold="100", upload_feature="True", resolve_lookups="True", creation_status="active",
                 existing_layer=None):

        self.master = master
        self.logfile = logfile
        self.loglevelname = loglevelname
        self.bulk_threshold = bulk_threshold
        self.resolve_lookups = resolve_lookups
        self.upload_feature = upload_feature
        self.creation_status = creation_status
        self.existing_layer = existing_layer
        self.layer_dict = layer_dict
        self.start_file = 0
        api_client = ApiClient()
        self.api_client = api_client
        self.logger = api_client.configuration.packagelogger
        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter")
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()
        # setting tkinter window size
        master.geometry("%dx%d" % (self.width, self.height))
        # master.minsize(root.winfo_width(), root.winfo_height())
        master.header = Label(master, text="XML Prompter", font=("Arial", 40, "bold")).place(x=600, y=80)
        if os.path.exists(self.save_path) and self.existing_layer:
            message = "arcmap_edit_config.xml file already exists in \n" \
                      "{0} ".format(self.save_path)
            filesize = os.path.getsize(self.save_path)
            if filesize == 0:
                Button(master, text="create new file", width='20', height='2',
                       command=lambda: self.window_1_(use_exisiting_file=0), bg="#349cbc", fg='gray92').place(
                    x=700,
                    y=600)
            else:
                Button(master, text="Use existing file", width='20', height='2',
                       command=lambda: self.window_1_(use_exisiting_file=1), bg="#349cbc", fg='gray92').place(
                    x=700,
                    y=500)
        else:
            message = "arcmap_edit_config.xml file will be created in\n {0}".format(self.save_path)
        Button(master, text="create new file", width='20', height='2',
               command=lambda: self.window_1_(use_exisiting_file=0), bg="#349cbc", fg='gray92').place(
            x=700,
            y=600)
        Label(master, text=message).place(x=550, y=300)

    def delete_layer(self, curr_layer, button_index):
        self.save_layer_info(curr_layer, delete=1, button_index=button_index)

    def window_1_(self, use_exisiting_file):
        self.delete_label = {}
        self.use_exisiting_file = use_exisiting_file
        self.l_button = {}
        self.delete_button = {}
        self.master.withdraw()
        window_1 = Toplevel(self.master)
        self.window_1 = window_1
        self.window_1.geometry("%dx%d" % (self.width, self.height))
        Label(window_1, text="Layer: ").place(x=60, y=185)
        Label(self.window_1, text="Note: ", font=("Arial Bold", 8)).place(x=20, y=20)
        Label(self.window_1, text="'-' : Delete ", font=("Arial Bold", 8)).place(x=20, y=40)
        Label(self.window_1, text="Order", font=("Arial Bold", 8)).place(x=20, y=70)
        Label(self.window_1, text="1. Delete Layer if needed",
              font=("Arial Bold", 8)).place(x=20, y=90)
        Label(self.window_1, text="2. Add/edit Layer Component",
              font=("Arial Bold", 8)).place(x=20, y=110)
        # if user use existing file and it contains a layer
        if use_exisiting_file == 1:

            #     #if in existiing layer is not None and contain layer
            if self.existing_layer and (len(self.existing_layer)) > 0:

                if (len(self.existing_layer)) > self.extra_fields:
                    num_layer = self.extra_fields
                else:
                    # if contain layer and maximum
                    num_layer = len(self.existing_layer)
                count = 1
                for j in range(1, num_layer + 1):
                    k = j
                    self.delete_label[j] = Label(self.window_1, text='', font='Helvetica 9')
                    self.l_button[j] = Button(self.window_1,
                                              text='{0}. {1} '.format(j, self.existing_layer[j]["layer_name"]),
                                              height=1,
                                              width=28, font='Helvetica 8', anchor="w",
                                              command=lambda curr_layer=j: self.window_2_(curr_layer, curr_layer))
                    self.delete_button[j] = Button(self.window_1, text='-', height=1,
                                                   width=2, font='Helvetica 8 bold', fg="red",
                                                   command=lambda curr_layer=j: self.delete_layer(curr_layer,
                                                                                                  curr_layer))
                    if k > 7:

                        self.l_button[k].place(x=60 + count * 300, y=(k - 7 * count) * 60 + 180)
                        self.delete_label[k].place(x=60 + count * 300, y=(k - 7 * count) * 60 + 180)
                        self.delete_button[k].place(x=250 + count * 300, y=(k - 7 * count) * 60 + 180)
                        if k % 7 == 0:
                            count += 1
                    else:
                        self.l_button[j].place(x=60, y=j * 60 + 180)
                        self.delete_button[j].place(x=250, y=j * 60 + 180)
                        self.delete_label[j].place(x=60, y=j * 60 + 180)
                option = [k for k in range(self.extra_fields - len(self.existing_layer))]
                if option:
                    self.max_num = max(option) + 1
                    self.add_layer_button(curr_layer=j)

            else:
                # if user use existing file but no layer is detected than makeit add layer
                option = [k for k in range(self.extra_fields)]
                self.max_num = max(option) + 1
                curr_layer = 0
                self.add_layer_button(curr_layer=curr_layer)

        else:
            option = [k for k in range(self.extra_fields)]
            self.max_num = max(option) + 1
            curr_layer = 0
            self.add_layer_button(curr_layer=curr_layer)
        Button(self.window_1, text="Save & Close", width='15', height='2',
               command=lambda: self.master.destroy(), bg="#349cbc", fg='gray92').place(x=200, y=700)
        # Button(self.window_1, text="Next", width='10', height='2',command=lambda : self.asset_prompter(), bg="#349cbc", fg='gray92').place(x=800, y=700)

    def asset_prompter(self):
        layer_window = self.window_1.deiconify()
        root = tk.Tk()
        existing_layer = XML_Prompter_for_Layer.get_existing_xml()
        prompter = XMl_Prompter_for_Asset(root, layer_dict=layer, existing_layer=existing_layer)
        root.mainloop()
        layer_window.destroy()

    def add_layer_button(self, curr_layer):

        number = self.max_num
        self.l_button_new = {}
        self.label_button = {}
        count = (curr_layer) / 7
        start = 0
        self.m = 1
        for m in range(1, int(number) + 1):
            k = m + curr_layer
            self.label_button[m] = Label(self.window_1, text='', font='Helvetica 9')
            self.l_button_new[m] = Button(self.window_1, text='', height=1,
                                          width=10, font='Helvetica 10', bd=0,
                                          command=lambda j=m: self.window_2_(curr_layer + j, j))

            if k > 7:

                self.label_button[m].place(x=60 + count * 300, y=(k - 7 * count) * 60 + 180)
                self.l_button_new[m].place(x=60 + count * 300, y=(k - 7 * count) * 60 + 180)
                if start == 0:
                    self.l_button_new[m].configure(bd=1, text="Add layer")
                    start += 1
            else:
                self.label_button[m].place(x=60, y=k * 60 + 180)
                self.l_button_new[m].place(x=60, y=k * 60 + 180)
                if start == 0:
                    self.l_button_new[m].configure(bd=1, text="Add layer")
                    start += 1

            if k % 7 == 0:
                count += 1

    def window_2_(self, curr_layer, button_index=None):

        """
        param:
        button_index: to keep track of add layer button.(make it visible)
        """

        """window 2 for Asset form"""
        window_2 = Toplevel(self.master)
        self.window_2 = window_2
        window_2.title("Assetic XML Prompter")
        window_2.geometry("900x400")
        Label(window_2, text="Layer name").place(x=20, y=70)
        Label(window_2,
              text="once saved button is clicked, the existing arcmap_edit_config.xml will be modififed",
              fg="red", font='Helvetica 11 underline').place(x=20, y=200)

        if self.use_exisiting_file and self.existing_layer:

            # if user use existing file and existing file is not None
            try:

                one_layer = self.existing_layer[curr_layer]
                self.layer_name = ttk.Combobox(window_2, values=[one_layer["layer_name"]], width=40)
                self.layer_name.current(0)
                self.layer_name.config(value=self.layer_option)
            except KeyError:
                self.layer_name = ttk.Combobox(window_2, values=self.layer_option, width=40)
            self.layer_name.place(x=250, y=70)

        else:

            self.layer_name = ttk.Combobox(window_2, values=self.layer_option, width=40)
            self.layer_name.current(0)
            self.layer_name.place(x=250, y=70)
        self.button_save = Button(window_2, text="Save", width='20', height='2',
                                  command=lambda: self.save_layer_info(curr_layer, button_index=button_index),
                                  bg="#349cbc", fg='gray92').place(x=150, y=300)

    def save_layer_info(self, curr_layer, delete=0, button_index=None):
        found = 0
        delete_found = 0
        if self.use_exisiting_file:

            if os.path.isfile(self.save_path):
                tree = ET.parse(self.save_path)
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
                                        break;
                                    if self.layer_name.get() is None or self.layer_name.get() in [None, '', ' ']:
                                        messagebox.showerror("Error", "Layer name is missing")
                                        return
                                    found = 1
                                    # if found the layer,check if layer exist/ not
                                    all_layer = operation.findall("layer")
                                    all_layer = [i.attrib["name"] for i in all_layer]
                                    if self.layer_name.get() in all_layer:
                                        messagebox.showerror("Error", "Layer has already exist")
                                        return
                                    break;
                                else:
                                    num_layer += 1
                            except KeyError:

                                # means adding a new layer
                                found = 0
                                # check if the newly added layer has exist in or not, if yes

                                if onelayer.get("name") == self.layer_name.get():
                                    messagebox.showerror("Error", "Layer name has already exist")
                                    return
                            except TypeError:
                                found = 0
                                # check if the newly added layer has exist in or not, if yes

                                if onelayer.get("name") == self.layer_name.get():
                                    messagebox.showerror("Error", "Layer name has already exist")
                                    return

                        if delete:
                            break;
                        if found == 0:
                            # if it is adding a new layer, and layer name hasnt exist before
                            onelayer = ET.SubElement(operation, "layer")
                    if self.layer_name.get() is None or self.layer_name.get() in [None, '', ' ']:
                        messagebox.showerror("Error", "Layer name is missing")
                        return
                    onelayer.set("name", self.layer_name.get())
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
            with open(self.save_path, "w") as f:
                f.write(dom_string)
                f.close()
        else:
            # if not exist, create a new file

            m_encoding = 'UTF-8'
            # root element
            self.use_exisiting_file = 1
            root = ET.Element("asseticconfig", {'name': 'ESRI'})

            logfile = ET.SubElement(root, "logfile")
            logfile.text = self.logfile
            loglevel = ET.SubElement(root, "loglevel")
            loglevel.text = self.loglevelname
            bulk_threshold = ET.SubElement(root, "bulk_threshold")
            bulk_threshold.text = self.bulk_threshold
            operation = ET.SubElement(root, "operation", action="Asset")
            layer = ET.SubElement(operation, "layer", name=self.layer_name.get())
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
            with open(self.save_path, 'wb') as f:
                f.write(part1 + 'encoding=\"{}\"?>\n'.format(m_encoding) + part2)
                f.close()
        messagebox.showinfo('Info', 'Successfully Saved')
        if not delete:
            layername = self.layer_name.get()
            self.window_2.destroy()
            try:
                if found == 1:
                    # editing existing layer
                    self.l_button[button_index].place_forget()
                    self.delete_button[button_index].place_forget()
                    self.delete_label[button_index]["text"] = '{0}. {1} edited'.format(curr_layer, layername)

                else:
                    # add a new layer
                    self.label_button[button_index]["text"] = '{0}. {1} added'.format(curr_layer, layername)
                    self.l_button_new[button_index].place_forget()
                    try:

                        # as long as it doesnt pass limit, then show a new add layer button
                        self.l_button_new[button_index + 1].configure(bd=1, text="Add layer")
                    except:
                        pass
            except KeyError:
                # wont go here
                pass

        if delete:
            try:
                self.l_button[button_index].place_forget()
                self.delete_button[button_index].place_forget()
                self.delete_label[button_index]["text"] = "{0}. {1} deleted".format(button_index,
                                                                                    self.existing_layer[button_index][
                                                                                        "layer_name"])
            except:
                pass
        self.window_1.deiconify()

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

    @staticmethod
    def get_existing_xml():
        api_client = ApiClient()
        api_client = api_client
        logger = api_client.configuration.packagelogger
        """use existing file and save it in a dictionary called self.existing_layer"""
        asset_found = 0
        save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
        assetic_folder = os.environ['APPDATA'] + '\\Assetic'

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
            return existing_layer


class XMl_Prompter_for_Asset:
    extra_fields = 7
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)

    def __init__(self, master, layer_dict=None, existing_layer=None):
        self.existing_layer = existing_layer
        self.master = master
        self.max_num = {}
        self.layer_dict = layer_dict
        api_client = ApiClient()
        self.api_client = api_client
        self.asset_buttons = {}
        self.logger = api_client.configuration.packagelogger
        self.asset_category_api = AssetConfigurationApi(self.api_client)
        self.asset_type_api = AssetConfigurationApi(self.api_client)
        self.asset_subtype_api = AssetConfigurationApi(self.api_client)
        self.asset_class_api = AssetConfigurationApi(self.api_client)
        self.asset_subclass_api = AssetConfigurationApi(self.api_client)
        self.asset_criticality_api = AssetConfigurationApi(self.api_client)
        self.host = self.api_client.configuration.host

        try:
            category = self.asset_category_api.asset_configuration_get_asset_category()
        except ApiException as e:
            self.logger.error(
                "Error getting Asset Category.\n"
                "Status: {0}, Reason: {1} \n "
                "{2}".format(e.status, e.reason, e.body))
            return
        if "ResourceList" not in category:
            msg = ("No ResourceList found ")
            self.logger.error(msg)
            return
        self.asset_category = {}
        for i in category["ResourceList"]:
            self.asset_category[i["Label"]] = i["Id"]
        self.category_label = sorted(self.asset_category.keys(), key=lambda x: x.lower())
        for i in range(self.extra_fields):
            self.asset_buttons[i] = []
        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())

        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()

        """
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter for Asset")
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()
        master.geometry("%dx%d" % (self.width, self.height))
        master.header = Label(master, text="XML Prompter for Asset", font=("Arial", 40, "bold")).place(x=430, y=80)
        if os.path.exists(self.save_path):
            message = ""
            Button(master, text="Start", width='20', height='2',
                   command=lambda: self.window_1_(), bg="#349cbc", fg='gray92').place(
                x=650,
                y=600)
        else:
            message = "XML Prompter for Layer should be run first"
        Label(master, text=message).place(x=550, y=300)
        """

    def window_1_(self):
        self.master.withdraw()
        window_1 = Toplevel(self.master)
        self.window_1 = window_1
        self.window_1.geometry("%dx%d" % (self.width, self.height))
        self.window_1.header = Label(
            self.window_1, text="Asset Attribute Configuration",
            font=("Arial", 20, "bold")
        ).place(x=self.width/2, y=40, anchor=CENTER)
        option = [i for i in range(self.extra_fields)]
        self.select_number = StringVar()
        self.select_number.set(option[0])

        if self.existing_layer:
            # if existing layer is more than the maximum , set it to the maximum fields
            if (len(self.existing_layer)) > self.extra_fields:
                num_layers = self.extra_fields
            else:
                num_layers = len(self.existing_layer)
            self.select_number.set(num_layers)
            self.ok()
        else:
            # else if there wasnt any file detected, choose the number of layer, it is wrong
            messagebox.showerror("Error", "XML Prompter for asset should be run first")
            return

    def ok(self):
        number = self.select_number.get()
        self.l_label = {}
        self.a_button = {}
        self.cat_label = {}
        self.delete_button = {}
        self.select_a_number = {}
        self.a_label_new = {}
        self.a_button_new = {}
        for i in range(1, int(number) + 1):
            self.cat_label[i] = {}
            self.a_button[i] = {}
            self.delete_button[i] = {}
            self.curr_layer = i
            # layer start from1
            self.l_label[i] = Label(self.window_1, font='Arial 12',
                                    text="{0}. Layer: {1}:".format(i, self.existing_layer[i]["layer_name"]))
            self.l_label[i].place(x=20, y=i * 40 + 120)

            if self.existing_layer[i]["corefields"] or self.existing_layer[i]["coredefaults"]:
                # Label(self.window_1, text="Note: ", font=("Arial Bold", 8)).place(x=20, y=20)
                # Label(self.window_1, text="'-' : Delete ", font=("Arial Bold", 8)).place(x=20, y=40)
                # Label(self.window_1, text="Order", font=("Arial Bold", 8)).place(x=20, y=70)
                # Label(self.window_1, text="1. Delete Asset if needed",
                #       font=("Arial Bold", 8)).place(x=20, y=90)
                # Label(self.window_1, text="2. Add/edit new Asset",
                #       font=("Arial Bold", 8)).place(x=20, y=110)

                num_asset = 1
                for j in range(1, num_asset + 1):
                    self.cat_label[i][j] = Label(self.window_1, text='', font='Helvetica 9')
                    self.cat_label[i][j].place(x=200 + 150, y=(i) * 40 + 120)

                    self.a_button[i][j] = Button(
                        self.window_1, text='{0}. Edit Configuration'.format(j), height=1,
                                                 width=13, font='Helvetica 10',
                                                 command=lambda k=i, l=j: self.window_2_(k, l, l))
                    self.a_button[i][j].place(x=200 + j * 150, y=(i) * 40 + 120)
                    self.delete_button[i][j] = Button(self.window_1, text=struct.pack('i', 10062).decode(
                            'utf-32'), height=1,
                                                      width=2, font='Helvetica 8 bold', fg="red",
                                                      command=lambda k=i, l=j: self.delete_asset(k, l, l))
                    self.delete_button[i][j].place(x=500,
                                                   y=(i) * 40 + 120)
                option = [1]
                if option:
                    self.max_num[i] = 0
                    self.select_a_number[i] = ttk.Combobox(self.window_1, values=option,
                                                           width=5)
                    self.add_asset_button(i, curr_asset=j)


            else:
                # only 1 asset is allowed
                option = [1]
                self.max_num[i] = max(option)
                curr_asset = 0
                self.add_asset_button(i, curr_asset=curr_asset)
            #Button(self.window_1, text="Finish", width='10', height='2',
            #       command=lambda: self.master.destroy(), bg="#349cbc", fg='gray92').place(x=700, y=700)
            Button(self.window_1, text="Finish", width='10', height='2',
                   command=lambda: self.window_1.destroy(), bg="#349cbc",
                   fg='gray92').place(x=self.width - 50, y=self.height - 50)
    def asset_left_frame(self, curr_layer, curr_asset):

        i = 40
        LFrame = self.window_2

        Label(LFrame, text="1. Asset Core Fields (GIS Field Name)", font=("Arial Bold", 9)).place(x=15, y=25 + i)
        Label(LFrame, text="Category*").place(x=15, y=85)
        Label(LFrame, text="Asset ID*").place(x=15, y=100 + i)
        Label(LFrame, text="Asset Name*").place(x=15, y=130 + i)
        Label(LFrame, text="Asset GUID").place(x=15, y=160 + i)
        Label(LFrame, text="Asset Class").place(x=15, y=190 + i)
        Label(LFrame, text="Asset SubClass").place(x=15, y=220 + i)
        Label(LFrame, text="Asset Type").place(x=15, y=250 + i)
        Label(LFrame, text="Asset SubType").place(x=15, y=280 + i)

        one_layer = self.existing_layer[curr_layer]["layer_name"]
        self.fields = []
        if one_layer in self.layer_option:
            self.fields = sorted(self.layer_dict[one_layer], key=lambda x: x.lower())
            self.fields.insert(0, " ")

        try:

            Label(LFrame, text="Edit Asset in layer: {0}".format(one_layer)).place(x=550, y=10)

            existing_asset = self.existing_layer[curr_layer]["corefields"]
            self.category_field = ttk.Combobox(LFrame, values=[self.existing_layer[curr_layer]["category"]], width=40)
            self.asset_id_field = ttk.Combobox(LFrame, values=[existing_asset["asset_id"]], width=40)
            self.asset_name_field = ttk.Combobox(LFrame, values=[existing_asset["asset_name"]], width=40)
            self.asset_guid_field = ttk.Combobox(LFrame,
                                                 values=[existing_asset["id"]],
                                                 width=40)
            self.asset_class_field = ttk.Combobox(LFrame, values=[existing_asset["asset_class"]], width=40)
            self.asset_sub_class_field = ttk.Combobox(LFrame, values=[existing_asset["asset_sub_class"]], width=40)
            self.asset_type_field = ttk.Combobox(LFrame, values=[existing_asset["asset_type"]], width=40)
            self.asset_sub_type_field = ttk.Combobox(LFrame, values=[existing_asset["asset_sub_type"]], width=40)
            self.category_field.current(0)
            self.asset_id_field.current(0)
            self.asset_name_field.current(0)
            self.asset_guid_field.current(0)
            self.asset_class_field.current(0)
            self.asset_sub_class_field.current(0)
            self.asset_type_field.current(0)
            self.asset_sub_type_field.current(0)
            self.asset_id_field.config(value=self.fields)
            self.asset_name_field.config(value=self.fields)
            self.asset_guid_field.config(value=self.fields)
            self.asset_class_field.config(value=self.fields)
            self.asset_sub_class_field.config(value=self.fields)
            self.asset_type_field.config(value=self.fields)
            self.asset_sub_type_field.config(value=self.fields)
            self.category_field.config(value=self.category_label)
        except KeyError:
            # if the current component is  more than the exising component or it is aa new component
            Label(LFrame, text="Add Asset to layer: {0}".format(one_layer)).place(x=550, y=10)
            self.category_field = ttk.Combobox(LFrame, values=self.category_label, width=40)
            self.asset_id_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_name_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_guid_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_class_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_sub_class_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.asset_sub_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
        self.category_field.place(x=250, y=85)
        self.asset_id_field.place(x=250, y=100 + i)
        self.asset_name_field.place(x=250, y=130 + i)
        self.asset_guid_field.place(x=250, y=160 + i)
        self.asset_class_field.place(x=250, y=190 + i)
        self.asset_sub_class_field.place(x=250, y=220 + i)
        self.asset_type_field.place(x=250, y=250 + i)
        self.asset_sub_type_field.place(x=250, y=280 + i)
        Button(self.window_2, text="Previous", width='10', height='2',
               command=lambda: [self.window_2.destroy(), self.window_1.deiconify()],
               font=("Arial", 10, "bold")).place(x=100, y=700)

    def asset_right_frame(self, curr_layer, curr_asset):
        i = 40
        RFrame = self.window_2
        self.Asset_Field()
        Label(RFrame, text="1. Asset Defaults (Hardcoded value)", font=("Arial Bold", 9)).place(x=850, y=25 + i)
        Label(RFrame, text="Asset ID*").place(x=850, y=100 + i)
        Label(RFrame, text="Asset Name*").place(x=850, y=130 + i)
        Label(RFrame, text="Asset GUID").place(x=850, y=160 + i)
        Label(RFrame, text="Asset Class").place(x=850, y=190 + i)
        Label(RFrame, text="Asset SubClass").place(x=850, y=220 + i)
        Label(RFrame, text="Asset Type").place(x=850, y=250 + i)
        Label(RFrame, text="Asset SubType").place(x=850, y=280 + i)
        try:
            existing_asset = self.existing_layer[curr_layer]["coredefaults"]

            self.asset_id_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_asset["asset_id"]),
                                          width=40)
            self.asset_name_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_asset["asset_name"]),
                                            width=40)

            self.asset_class_default = ttk.Combobox(RFrame, values=[existing_asset["asset_class"]], width=38)
            self.asset_class_default.current(0)
            self.asset_sub_class_default = ttk.Combobox(RFrame, values=[existing_asset["asset_sub_class"]], width=38)
            self.asset_sub_class_default.current(0)
            self.asset_subclass_fields__(curr_layer)
            self.asset_type_default = ttk.Combobox(RFrame, values=[existing_asset["asset_type"]], width=38)
            self.asset_type_default.current(0)
            self.asset_sub_type_default = ttk.Combobox(RFrame, values=[existing_asset["asset_sub_type"]], width=38)
            self.asset_sub_type_default.current(0)
            self.asset_subtype_fields__(curr_layer)
            # self.asset_class_default.config(value=self.asset_class_list)

        except KeyError:
            self.asset_id_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.asset_name_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.asset_class_default = ttk.Combobox(RFrame, values=self.asset_class_list, width=38)
            self.asset_sub_class_default = ttk.Combobox(RFrame, values=[""], width=38)
            self.asset_type_default = ttk.Combobox(RFrame, values=self.asset_types_list, width=38)
            self.asset_sub_type_default = ttk.Combobox(RFrame, values=[""], width=38)
        self.asset_class_default.config(value=self.asset_class_list)
        self.asset_class_default.bind("<<ComboboxSelected>>", self.asset_subclass_fields__)
        self.asset_type_default.config(value=self.asset_types_list)
        self.asset_type_default.bind("<<ComboboxSelected>>", self.asset_subtype_fields__)
        # self.asset_id_default.place(x=1015, y=100 + i)
        self.asset_name_default.place(x=1015, y=130 + i)
        # self.asset_guid_default.place(x=1015, y=160 + i)
        self.asset_class_default.place(x=1015, y=190 + i)
        self.asset_sub_class_default.place(x=1015, y=220 + i)
        self.asset_type_default.place(x=1015, y=250 + i)
        self.asset_sub_type_default.place(x=1015, y=280 + i)

    def window_2_(self, curr_layer, curr_asset, button_index=None):
        """window 2 for Asset form"""
        self.window_1.withdraw()
        window_2 = Toplevel(self.master)  # child window
        self.window_2 = window_2
        window_2.title("Assetic XML Prompter")
        window_2.geometry("1500x800")
        Label(window_2,
              text="Once saved button is clicked, the existing "
                   "configuration file will be modififed",
              fg="red", font='Helvetica 11 underline').place(x=500, y=600)
        self.asset_left_frame(curr_layer, curr_asset)
        self.asset_right_frame(curr_layer, curr_asset)

        self.button_save = Button(window_2, text="Save", width='20', height='2',
                                  command=lambda: self.save_asset_info(curr_layer, curr_asset, button_index),
                                  bg="#349cbc", fg='gray92').place(x=750, y=700)

    def add_asset_button(self, i, curr_asset):
        """place 'Add Asset Button'"""
        number = self.max_num[i]

        self.a_label_new[i] = {}

        self.a_button_new[i] = {}

        for m in range(1, int(number) + 1):
            self.a_label_new[i][m] = Label(self.window_1, text="", font='Helvetica 9')
            self.a_label_new[i][m].place(x=200 + 150,
                                         y=(i) * 40 + 120)
            self.a_button_new[i][m] = Button(self.window_1, text='{0}. Add Asset'.format(curr_asset + m), height=1,
                                             width=10, font='Helvetica 10',
                                             command=lambda j=i, k=m: self.window_2_(i, curr_asset + m, button_index=k))

            self.a_button_new[i][m].place(x=200 + (curr_asset + m) * 150, y=(i) * 40 + 120)

    def delete_asset(self, curr_layer, curr_asset, button_index):
        self.add_asset_to_xml_file(curr_layer, curr_asset, delete=1, button_index=button_index)

    def save_asset_info(self, curr_layer, curr_asset, button_index=None):

        if not self.category_field.get():
            messagebox.showerror('Error', 'Asset Category does not  exist')
            return
        self.xml_category = self.category_field.get()
        # check asset id

        if self.asset_id_field.get() in ["", ' ']:
            messagebox.showerror('Error', 'Asset ID cannot be empty')
            error = 1
            return
        elif self.asset_id_field.get() not in self.fields:
            messagebox.showerror('Error', 'Asset ID fields in Core Fields does not exist ')

            return
        self.xml_asset_ID = self.asset_id_field.get()
        if self.asset_id_field.get() in ["", ' ']:
            self.xml_asset_ID = None

        if self.asset_guid_field.get() in ["", ' ']:
            self.xml_asset_GUID_core_field = None
        elif self.asset_guid_field.get() in self.fields:
            self.xml_asset_GUID_core_field = self.asset_guid_field.get()
        else:
            messagebox.showerror("Error", "Asset GUID fields in Core Fields does not exist ")
            return
        if self.asset_name_default.get() in ["", ' '] and self.asset_name_field.get() in ["", ' ']:
            messagebox.showerror('Error', 'Asset Name cannot be empty')
            return
        elif self.asset_name_default.get():
            # if asset name in core default is not empty
            self.xml_asset_name_core_default = self.asset_name_default.get()
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
            self.add_asset_to_xml_file(curr_layer, curr_asset, delete=0, button_index=button_index)

        else:
            messagebox.showerror("Error", 'check again')

    def check_asset_type_subtype(self):
        error = 0
        self.xml_asset_subtype_field_default = None
        self.xml_asset_type_field_default = None
        self.xml_asset_type_field = None
        self.xml_asset_subtype_field = None
        if self.asset_type_field.get() in ["", ' '] and self.asset_type_default.get() in ["", ' ']:
            xml_asset_type = None

        # Asset Type is not Null in Core Default, it should exist in core defaults (assetic UI)
        elif self.asset_type_default.get() and self.asset_type_default.get() not in ["", ' ']:
            xml_asset_type = self.asset_type_default.get()
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
        if self.asset_sub_type_field.get() in ["", ' '] and self.asset_sub_type_default.get() in ["",
                                                                                                  ' ']:
            xml_asset_subtype = None
        # Asset SubType in Core Defaults is not Null, it should exist in assetic UI
        elif self.asset_sub_type_default.get() and self.asset_sub_type_default.get() not in [" ", ""]:
            xml_asset_subtype = self.asset_sub_type_default.get()
            self.xml_asset_subtype_field_default = self.asset_sub_type_default.get()
            if xml_asset_subtype not in self.asset_subtype_list:
                error = 1
                messagebox.showerror('Error', 'Asset SubType in Core Default does not exist')
                return error
                # Asset Subtype in Core Defaults and Core Fields are not Null, Asset Subclass in Core Fields should exist in GIS Table
            if self.asset_sub_type_field.get() and self.asset_sub_type_field.get() not in [" ", ""]:
                xml_asset_subtype = self.asset_sub_type_field.get()
                self.xml_asset_subtype_field = self.asset_sub_type_field.get()
                if xml_asset_subtype not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset SubType Fields in Core Fields does not exist')
                    return error
            else:
                self.xml_asset_subtype_field = None

        # Asset SubType in Core Fields is not Null, it should exist in GIS Table
        else:
            self.xml_asset_subtype_field_default = None
            xml_asset_subtype = self.asset_sub_type_field.get()
            self.xml_asset_subtype_field = self.asset_sub_type_field.get()
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

    def add_asset_to_xml_file(self, curr_layer, curr_asset, delete=0, button_index=None):
        layer = 1
        asset_num = 1
        found = 0

        if os.path.isfile(self.save_path):
            tree = ET.parse(self.save_path)

        else:
            messagebox.showerror("Error", "No arcmap_edit_config.xml is found")
            return
        root = tree.getroot()
        for operation in root.iter('operation'):
            action = operation.get("action")
            if action == "Asset":
                for onelayer in operation.iter("layer"):

                    if onelayer.get("name") == self.existing_layer[curr_layer]["layer_name"]:

                        coredefaults = onelayer.find("coredefaults")

                        corefields = onelayer.find("corefields")

                        category = onelayer.find('category')
                        if onelayer.find('category') is None:
                            found = 0
                            category = ET.SubElement(onelayer, "category")
                        else:
                            asset_num = 1

                            for category in onelayer.iter("category"):
                                # if asset_num > 1:
                                #     messagebox.showerror("Error", "Only one asset per layer is allowed")
                                # if asset_num == curr_asset:
                                if delete:
                                    onelayer.remove(category)
                                    break
                                found = 1
                            # if delete:
                            #     break

                        if coredefaults is None and not delete:
                            # create a new one
                            coredefaults = ET.SubElement(onelayer, "coredefaults")
                        else:
                            asset_num = 1
                            for coredefaults in onelayer.iter("coredefaults"):
                                # if asset_num > 1:
                                #     messagebox.showerror("Error", "Only one asset per layer is allowed")
                                # if asset_num == curr_asset:
                                if delete:
                                    onelayer.remove(coredefaults)
                                    break

                                # asset_num += 1
                            # if delete:
                            #     break

                        if corefields is None and not delete:

                            corefields = ET.SubElement(onelayer, "corefields")

                        else:
                            # check if there are more than 2 coredefaults means it is wrong

                            for corefields in onelayer.iter("corefields"):

                                # messagebox.showerror("Error", "Only one asset per layer is allowed")

                                if delete:
                                    onelayer.remove(corefields)
                                    break

                            if delete:
                                break
                            # if found == 0:
                            #     messagebox.showerror("Error", "Only one asset per layer is allowed")
                        if self.xml_category:
                            category.text = self.xml_category
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
                    layer += 1
        messagebox.showinfo('Info', 'Successfully Saved')
        dom = xml.dom.minidom.parseString(ET.tostring(root))
        xmlstring = dom.toprettyxml(encoding='UTF-8')
        dom_string = b'\n'.join([s for s in xmlstring.splitlines() if s.strip()])
        with open(self.save_path, 'wb') as file:
            file.write(dom_string)
            file.close()

        if not delete:
            self.window_2.destroy()

            if found == 0:

                self.a_button_new[curr_layer][button_index].place_forget()
                self.a_label_new[curr_layer][button_index]["text"] = "{0}. {1} Category".format(curr_asset,
                                                                                                category.text)
            elif found == 1:
                self.a_button[curr_layer][button_index].place_forget()
                self.delete_button[curr_layer][button_index].place_forget()
                self.cat_label[curr_layer][button_index]["text"] = "{0}. {1} Category".format(curr_asset, category.text)
        if delete:
            self.a_button[curr_layer][button_index].place_forget()
            self.delete_button[curr_layer][button_index].place_forget()

            self.cat_label[curr_layer][button_index]["text"] = "{0}. {1} Category deleted ".format(curr_asset,
                                                                                                   category.text)

        self.window_1.deiconify()

    def Asset_Field(self):
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
            return
        if "ResourceList" not in asset_types:
            return
        self.asset_types_list = [i["Name"] for i in asset_types["ResourceList"]]

        self.asset_types_list.insert(0, " ")
        # self.asset_type_field_default.config(value=types_list)
        # self.asset_type_field_default.current(0)
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
            return
        if "ResourceList" not in asset_class:
            return
        self.asset_class_list = [i["Name"] for i in asset_class["ResourceList"]]
        self.asset_class_list.insert(0, " ")
        # self.asset_Class_field_default.config(value=asset_class_list)
        # self.asset_Class_field_default.current(0)

        # self.asset_type_field_default.config(value=types)

    def asset_subtype_fields__(self, e):
        self.asset_subtype_not_found = 0
        asset_type = self.asset_type_default.get()
        kwargs = {
            'request_params_page': 1,
            'request_params_page_size': 500
        }
        x = self.asset_type_api.asset_configuration_get_asset_types(**kwargs)
        # onet_ttype = "ccs112"
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

        self.asset_sub_type_default.config(value=self.asset_subtype_list)

    def asset_subclass_fields__(self, e):
        self.asset_subclass_not_found = 0
        asset_class = self.asset_class_default.get()
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

        self.asset_sub_class_default.config(value=self.asset_subclass_list)

    def check_asset_class_subclass(self):
        self.xml_asset_class_field_default = None
        self.xml_asset_class_field = None
        self.xml_asset_subclass_field = None
        self.xml_asset_subclass_field_default = None
        error = 0

        if self.asset_class_field.get() in ["", ' '] and self.asset_class_default.get() in ["", ' ']:
            xml_asset_class = None
        # AssetClass in  Core Default is not Null, it should exist in (assetic UI)
        elif self.asset_class_default.get() and self.asset_class_default.get() not in [" ", '']:
            xml_asset_class = self.asset_class_default.get()
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
        if self.asset_sub_class_field.get() in ["", ' '] and self.asset_sub_class_default.get() in ["",
                                                                                                    ' ']:
            xml_asset_subclass = None
        # Asset Subclass in Core Defaults is not Null, it should exist in assetic UI
        elif self.asset_sub_class_default.get() and self.asset_sub_class_default.get() not in [" ", ""]:
            xml_asset_subclass = self.asset_sub_class_default.get()
            self.xml_asset_subclass_field_default = self.asset_sub_class_default.get()
            if xml_asset_subclass not in self.asset_subclass_list:
                error = 1
                messagebox.showerror('Error', 'Asset SubClass in Core Default does not exist')
                return error
            # Asset Subclass in Core Defaults and Core Fields are not Null, Asset Subclass in Core Fields should exist in GIS Table
            if self.asset_sub_class_field.get() and self.asset_sub_class_field.get() not in [" ", ""]:
                xml_asset_subclass = self.asset_sub_class_field.get()
                self.xml_asset_subclass_field = self.asset_sub_class_field.get()
                if xml_asset_subclass not in self.fields:
                    error = 1
                    messagebox.showerror('Error', 'Asset SubClass Fields in Core Fields does not exist')
                    return error
            else:
                self.xml_asset_subclass_field = None


        # Asset Subclass in Core Fields is not Null and Asset Subclass in core defaults is null,Asset Subclass in Core Fields should exist in GIS Table
        else:
            self.xml_asset_subclass_field_default = None
            xml_asset_subclass = self.asset_sub_class_field.get()
            self.xml_asset_subclass_field = self.asset_sub_class_field.get()
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


class XMl_Prompter_for_Component:
    extra_fields = 7
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)
    component_temp_path = os.environ['APPDATA'] + '\\Assetic\\component.xml'
    merged_temp_path = os.environ['APPDATA'] + '\\Assetic\\merged_arcmap_edit_config.xml'

    def __init__(self, master, layer_dict=None, existing_layer=None):
        self.existing_layer = existing_layer
        self.master = master
        self.max_num = {}
        self.layer_dict = layer_dict
        api_client = ApiClient()
        self.api_client = api_client
        self.component_buttons = {}
        self.logger = api_client.configuration.packagelogger
        for i in range(self.extra_fields):
            self.component_buttons[i] = []
        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())

        self.width = master.winfo_screenwidth() * .9
        self.height = master.winfo_screenheight() * .9
        """
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter for Component")
        master.geometry("%dx%d" % (self.width, self.height))
        master.header = Label(master, text="XML Prompter for Component", font=("Arial", 40, "bold")).place(x=400, y=80)

        if os.path.exists(self.save_path):
            message = ""
            Button(master, text="Start", width='20', height='2',
                   command=lambda: self.window_1_(), bg="#349cbc", fg='gray92').place(
                x=650,
                y=600)
        else:
            message = "XML Prompter for asset should be run first"

        Label(master, text=message).place(x=700, y=500)
        """

    def layer_prompter(self):

        self.master.destroy()
        root = tk.Tk()

        prompter = XML_Prompter_for_Layer(root, layer_dict=layer)
        root.mainloop()

    def window_1_(self):

        self.master.withdraw()
        window_1 = Toplevel(self.master)
        self.window_1 = window_1
        self.window_1.geometry("%dx%d" % (self.width, self.height))
        self.window_1.header = Label(
            self.window_1, text="Component Configuration",
            font=("Arial", 20, "bold")
        ).place(x=self.width/2, y=40, anchor=CENTER)
        option = [i for i in range(self.extra_fields)]
        self.select_number = StringVar()
        self.select_number.set(option[0])
        drop = OptionMenu(window_1, self.select_number, *option)
        if self.existing_layer:
            # if existing layer is more than the maximum , set it to the maximum fields
            if (len(self.existing_layer)) > self.extra_fields:
                num_layers = self.extra_fields
            else:
                num_layers = len(self.existing_layer)
            self.select_number.set(num_layers)
            self.ok()

        else:
            # else if there wasnt any file detected, choose the number of layer, it is wrong
            messagebox.showerror("Error", "XML Prompter for asset should be run first")
            return

    def ok(self):
        number = self.select_number.get()
        l_label = {}
        self.c_button = {}
        self.delete_button = {}
        self.new_comp_label = {}
        self.c_label_new = {}
        self.c_button_new = {}
        self.select_c_number = {}
        for i in range(1, int(number) + 1):
            self.curr_layer = i
            self.delete_button[i] = {}
            self.c_button[i] = {}
            self.new_comp_label[i] = {}
            # layer start from1
            self.c_button_new[i] = {}
            self.c_label_new[i] = {}

            l_label[i] = Label(self.window_1, text="{0}. Layer: {1}:".format(i, self.existing_layer[i]["layer_name"]))
            l_label[i].place(x=10, y=i * 40 + 120)
            if (len(self.existing_layer[i]["components"])) > 0:
                Label(self.window_1, text="Note: ", font=("Arial Bold", 8)).place(x=20, y=20)
                Label(self.window_1, text="'-' : Delete ", font=("Arial Bold", 8)).place(x=20, y=40)
                Label(self.window_1, text="Order", font=("Arial Bold", 8)).place(x=20, y=70)
                Label(self.window_1, text="1. Delete Component if needed",
                      font=("Arial Bold", 8)).place(x=20, y=90)
                Label(self.window_1, text="2. Add/edit new Component",
                      font=("Arial Bold", 8)).place(x=20, y=110)

                if (len(self.existing_layer[i]["components"])) > self.extra_fields:
                    num_comp = self.extra_fields
                else:
                    num_comp = (len(self.existing_layer[i]["components"]))
                for j in range(1, num_comp + 1):
                    self.new_comp_label[i][j] = Label(self.window_1, text='', font='Helvetica 8')
                    self.new_comp_label[i][j].place(x=200 + (j) * 150,
                                                    y=(i) * 40 + 120)
                    self.c_button[i][j] = Button(self.window_1, text='{0}. Existing Comp'.format(j), height=1,
                                                 width=13, font='Helvetica 8',
                                                 command=lambda k=i, l=j: self.window_2_(k, l, button_index=l))
                    self.c_button[i][j].place(x=200 + j * 150, y=(i) * 40 + 120)
                    self.delete_button[i][j] = Button(self.window_1, text='-', height=1,
                                                      width=2, font='Helvetica 8 bold', fg="red",
                                                      command=lambda k=i, l=j: self.delete_comp(k, l, button_index=l))

                    self.delete_button[i][j].place(x=290 + j * 150, y=(i) * 40 + 120)
                option = [k for k in range(self.extra_fields - len(self.existing_layer[i]["components"]))]
                if option:
                    self.max_num[i] = max(option) + 1
                    self.select_c_number[i] = ttk.Combobox(self.window_1, values=option,
                                                           width=5)
                    self.add_comp_button(i, curr_comp=j)
            else:
                option = [k for k in range(self.extra_fields)]
                self.max_num[i] = max(option) + 1
                curr_comp = 0
                self.add_comp_button(i, curr_comp=curr_comp)
            """
            Button(self.window_1, text="Finish", width='10', height='2',
                   command=lambda: self.master.destroy(), bg="#349cbc", fg='gray92').place(x=700, y=700)
            """
            Button(self.window_1, text="Finish", width='10', height='2',
                   command=lambda: self.window_1.destroy(), bg="#349cbc",
                   fg='gray92').place(x=700, y=self.height - 50)

    def add_comp_button(self, i, curr_comp):
        """curr_comp in the i th layer"""
        number = self.max_num[i]
        start = 0
        for m in range(1, int(number) + 1):

            self.c_label_new[i][m] = Label(self.window_1, text='', font=("Helvetica", 8))

            self.c_label_new[i][m].place(
                x=200 + (curr_comp + m) * 150,
                y=(i) * 40 + 120)

            self.c_button_new[i][m] = Button(self.window_1, text=''.format(curr_comp + m), height=1,
                                             width=10, font='Helvetica 8', bd=0,
                                             command=lambda j=i, k=m: self.window_2_(i, curr_comp + k, button_index=k,
                                                                                     add=1))
            self.c_button_new[i][m].place(x=200 + (curr_comp + m) * 150, y=(i) * 40 + 120)
            if start == 0:
                self.c_button_new[i][m].configure(bd=1, text="Add comp")

                start += 1

    def delete_comp(self, curr_layer, curr_comp, button_index=None):
        self.add_component_to_xml_file(curr_layer=curr_layer, curr_comp=curr_comp, delete=1, button_index=button_index)

    def window_2_(self, curr_layer, curr_comp, button_index=None, add=None):
        """window 2 for component form"""

        self.window_1.withdraw()
        window_2 = Toplevel(self.master)  # child window
        self.window_2 = window_2
        window_2.title("Assetic XML Prompter")
        window_2.geometry("1600x%d" % (self.height))
        Label(window_2,
              text="once saved button is clicked, the existing arcmap_edit_config.xml will be modififed",
              fg="red", font='Helvetica 11 underline').place(x=500, y=600)
        self.component_left_frame(curr_layer, curr_comp)
        self.component_right_frame(curr_layer, curr_comp)

        self.button_save = Button(window_2, text="Save", width='20', height='2',
                                  command=lambda: self.save_component_info(curr_layer, curr_comp,
                                                                           button_index=button_index, add=add),
                                  bg="#349cbc", fg='gray92').place(x=750, y=700)

    def save_component_info(self, curr_layer, curr_comp, button_index=None, add=None):

        """
        save the information from the form
        params i: The nth of the layer
        """
        c_label = 1
        c_type = 1
        error = 0
        self.xml_c_label_default = self.c_label_default.get()
        self.xml_c_label_field = self.c_label_field.get()
        self.xml_c_type_field = self.c_type_field.get()
        self.xml_c_type_default = self.c_type_default.get()
        if self.xml_c_label_default in [" ", '', None]:
            self.xml_c_label_default = None
        if self.xml_c_type_field in [" ", "", None]:
            self.xml_c_type_field = None
        if self.xml_c_label_field in [" ", '', None]:
            self.xml_c_label_field = None
        if self.xml_c_type_default in [" ", '', None]:
            self.xml_c_type_default = None
        if self.xml_c_label_default is None and self.xml_c_label_field is None:
            c_label = 0
        if self.xml_c_type_field is None and self.xml_c_type_default is None:
            c_type = 0
        if c_label == 1 and c_type == 1:
            self.add_component_to_xml_file(curr_layer=curr_layer, curr_comp=curr_comp, delete=0,
                                           button_index=button_index, add=add)
        elif c_label == 0 and c_type == 1:
            messagebox.showerror('Error', 'Component Label need to select to save Component ')
            return
        elif c_label == 1 and c_type == 0:
            messagebox.showerror('Error', 'Component Type need to select to save Component')
            return
        elif c_label == 0 and c_type == 0:
            messagebox.showerror("Error", message='Component is not saved if Label and Type are empty')
            return

    def add_component_to_xml_file(self, curr_layer, curr_comp, delete=0, button_index=None, add=None):

        layer = 1
        comp_num = 1
        found = 0
        if os.path.isfile(self.save_path):
            tree = ET.parse(self.save_path)

        else:
            messagebox.showerror("Error", "No arcmap_edit_config.xml is found")
            return
        root = tree.getroot()
        # check if there is a layer name
        for operation in root.iter('operation'):
            action = operation.get("action")
            if action == "Asset":
                for onelayer in operation.iter("layer"):
                    if onelayer.get("name") == self.existing_layer[curr_layer]["layer_name"]:
                        # if  components found within a layer
                        components = onelayer.find('components')
                        if components is None:
                            found = 0
                            # create a new one
                            components = ET.SubElement(onelayer, "components")
                            componentdefaults = ET.SubElement(components, "componentdefaults")
                        else:

                            # in case there is more than 1 components
                            comp_num = 1
                            all_component = []
                            comp_num = 1
                            for components in onelayer.iter("components"):
                                # find the label from default and fields

                                componentdefaults = components.find("componentdefaults")
                                component_corefields = components.find("componentfields")
                                try:
                                    l = componentdefaults.find("label")
                                    label = l.text
                                    all_component.append(label)
                                except:
                                    l = component_corefields.find("label")
                                    label = l.text
                                    all_component.append(label)

                                # check by the label to see any matching label and edit. if it is add , then dont check

                                try:
                                    # use try because existing component maynot have component,component default or component fields
                                    label_default = \
                                        self.existing_layer[curr_layer]["components"][curr_comp]["componentdefaults"][
                                            "label"]
                                except:
                                    label_default = None
                                try:
                                    label_field = \
                                        self.existing_layer[curr_layer]["components"][curr_comp]["componentfields"][
                                            "label"]
                                except:
                                    label_field = None

                                if (label == label_default or label == label_field) and add != 1:
                                    # check if it is an existing components, otherwise add a new component
                                    if delete:
                                        onelayer.remove(components)
                                        break;
                                    # if we found the component
                                    found = 1

                                    if (
                                            self.xml_c_label_default in all_component and self.xml_c_label_default != label_default) or (
                                            self.xml_c_label_field in all_component and self.xml_c_label_field != label_field):
                                        messagebox.showerror("Error", "Do not provide duplicate Component")
                                        return
                                    if componentdefaults is None:
                                        componentdefaults = ET.SubElement(components, "componentdefaults")

                                    break
                                comp_num += 1
                            if found == 0 and add != 1 and not delete:
                                messagebox.showerror("Error", "Unable to edit because existing component not found"
                                                     )
                                return
                            if delete:
                                break;
                            if found == 0:
                                # when add a new component, make sure that there is no duplicate label
                                if self.xml_c_label_default in all_component or self.xml_c_label_field in all_component:
                                    messagebox.showerror("Error", "Do not provide duplicate Component")
                                    return

                                # when a new component is added, create a new component tag
                                components = ET.SubElement(onelayer, "components")
                                componentdefaults = components.find("componentdefaults")
                                if componentdefaults is None:
                                    componentdefaults = ET.SubElement(components, "componentdefaults")

                        if self.xml_c_label_default:
                            c_label_default = componentdefaults.find("label")
                            if c_label_default is None:
                                c_label_default = ET.SubElement(componentdefaults, "label")
                            c_label_default.text = self.xml_c_label_default
                        if self.xml_c_type_default:
                            c_type_default = componentdefaults.find("component_type")
                            if c_type_default is None:
                                c_type_default = ET.SubElement(componentdefaults, "component_type")
                            c_type_default.text = self.xml_c_type_default
                        if self.c_dimension_unit_default.get() not in ["", ' ', None]:
                            c_dimension_default = componentdefaults.find("dimension_unit")
                            if c_dimension_default is None:
                                c_dimension_default = ET.SubElement(componentdefaults, "dimension_unit")
                            c_dimension_default.text = self.c_dimension_unit_default.get()
                        if self.c_network_measure_type_default.get() not in ["", ' ', None]:
                            c_network_measure_type_default = componentdefaults.find("network_measure_type")
                            if c_network_measure_type_default is None:
                                c_network_measure_type_default = ET.SubElement(componentdefaults,
                                                                               "network_measure_type")
                            c_network_measure_type_default.text = self.c_network_measure_type_default.get()
                        if self.c_material_type_default.get() not in ["", ' ', None]:
                            c_material_type_default = componentdefaults.find("material_type")
                            if c_material_type_default is None:
                                c_material_type_default = ET.SubElement(componentdefaults, "material_type")
                            c_material_type_default.text = self.c_material_type_default.get()
                        if self.c_design_life_default.get() not in ["", ' ', None]:
                            c_design_life_default = componentdefaults.find("design_life")
                            if c_design_life_default is None:
                                c_design_life_default = ET.SubElement(componentdefaults, "design_life")
                            c_design_life_default.text = self.c_design_life_default.get()
                        component_corefields = components.find("componentfields")
                        if component_corefields is None:
                            component_corefields = ET.SubElement(components, "componentfields")
                        if self.xml_c_label_field:
                            c_label_field = component_corefields.find("label")
                            if c_label_field is None:
                                c_label_field = ET.SubElement(component_corefields, "label")
                            c_label_field.text = self.xml_c_label_field
                        if self.xml_c_type_field:
                            c_type_field = component_corefields.find("component_type")
                            if c_type_field is None:
                                c_type_field = ET.SubElement(component_corefields, "component_type")
                            c_type_field.text = self.xml_c_type_field
                        if self.c_dimension_unit_field.get() not in ["", ' ', None]:
                            c_dimension_unit_field = component_corefields.find("dimension_unit")
                            if c_dimension_unit_field is None:
                                c_dimension_unit_field = ET.SubElement(component_corefields, "dimension_unit")
                            c_dimension_unit_field.text = self.c_dimension_unit_field.get()
                        if self.c_network_measure_type_field.get() not in ["", ' ', None]:
                            c_network_measure_type_field = component_corefields.find("network_measure_type")
                            if c_network_measure_type_field is None:
                                c_network_measure_type_field = ET.SubElement(component_corefields,
                                                                             "network_measure_type")
                            c_network_measure_type_field.text = self.c_network_measure_type_field.get()
                        if self.c_design_life_field.get() not in ["", ' ', None]:
                            c_design_life_field = componentdefaults.find("design_life")
                            if c_design_life_field is None:
                                c_design_life_field = ET.SubElement(component_corefields, "design_life")
                            c_design_life_field.text = self.c_design_life_field.get()
                        if self.c_material_type_field.get() not in ["", ' ', None]:
                            c_material_type_field = componentdefaults.find("material_type")
                            if c_material_type_field is None:
                                c_material_type_field = ET.SubElement(component_corefields, "material_type")
                            c_material_type_field.text = self.c_material_type_field.get()

                    layer += 1

        messagebox.showinfo('Info', 'Successfully Saved')
        dom = xml.dom.minidom.parseString(ET.tostring(root))
        xmlstring = dom.toprettyxml(encoding='UTF-8')
        dom_string = b'\n'.join([s for s in xmlstring.splitlines() if s.strip()])
        with open(self.save_path, 'wb') as file:
            file.write(dom_string)
            file.close()
        if not delete:
            self.window_2.destroy()
            if self.xml_c_label_default is not None:
                label_new = self.xml_c_label_default
            else:
                label_new = self.xml_c_label_field
            if found == 0:
                # add a new component
                self.c_label_new[curr_layer][button_index]["text"] = "{0}. Comp with label:\n" \
                                                                     "'{1}' added".format(curr_comp, label_new)
                self.c_button_new[curr_layer][button_index].place_forget()
                try:
                    self.c_button_new[curr_layer][button_index + 1].configure(bd=1, text="Add comp")
                except:
                    pass
            else:
                # edit existing compoent

                self.new_comp_label[curr_layer][button_index]["text"] = "{0}. Comp with label:\n'{1}' edited".format(
                    curr_comp,
                    label_new)
                self.c_button[curr_layer][button_index].place_forget()
                self.delete_button[curr_layer][button_index].place_forget()

        if delete:
            if label_default is None:
                label = label_field
            else:
                label = label_default
            self.new_comp_label[curr_layer][button_index]['text'] = "{0}. Comp with label: \n'{1}' deleted".format(
                curr_comp,
                label)
            self.c_button[curr_layer][button_index].place_forget()
            self.delete_button[curr_layer][button_index].place_forget()
        self.window_1.deiconify()

    def component_left_frame(self, curr_layer, curr_comp):
        i = 15
        LFrame = self.window_2

        Label(LFrame, text="1. Component Fields (GIS Field Name)", font=("Arial Bold", 9)).place(x=15, y=30 + i)
        Label(LFrame, text="Component Label*").place(x=15, y=70 + i)
        Label(LFrame, text="Component Type*").place(x=15, y=100 + i)
        Label(LFrame, text="Dimension Unit").place(x=15, y=130 + i)
        Label(LFrame, text="Network Measure").place(x=15, y=160 + i)
        Label(LFrame, text="Design Life").place(x=15, y=190 + i)
        Label(LFrame, text="Material Type").place(x=15, y=220 + i)

        one_layer = self.existing_layer[curr_layer]["layer_name"]
        self.fields = []
        if one_layer in self.layer_option:
            self.fields = sorted(self.layer_dict[one_layer], key=lambda x: x.lower())
            self.fields.insert(0, " ")

        try:
            # if the current component is not more than the exising component and the component has all the info
            # self.existing_layer[curr_layer]['components'] and self.existing_layer[curr_layer]["components"][curr_comp]["componentfields"] :
            Label(LFrame, text="Edit component in layer: {0}".format(one_layer)).place(x=550, y=10)
            existing_component = self.existing_layer[curr_layer]["components"][curr_comp]["componentfields"]
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
            self.c_label_field.config(value=self.fields)
            self.c_type_field.config(value=self.fields)
            self.c_dimension_unit_field.config(value=self.fields)
            self.c_network_measure_type_field.config(value=self.fields)
            self.c_material_type_field.config(value=self.fields)
            self.c_design_life_field.config(value=self.fields)
        except KeyError:
            # if the current component is  more than the exising component or it is aa new component
            Label(LFrame, text="Add component to layer: {0}".format(one_layer)).place(x=550, y=10)
            self.c_label_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_dimension_unit_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_network_measure_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_material_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.c_design_life_field = ttk.Combobox(LFrame, values=self.fields, width=40)

        self.c_label_field.place(x=250, y=70 + i)
        self.c_type_field.place(x=250, y=100 + i)
        self.c_dimension_unit_field.place(x=250, y=130 + i)
        self.c_network_measure_type_field.place(x=250, y=160 + i)
        self.c_design_life_field.place(x=250, y=190 + i)
        self.c_material_type_field.place(x=250, y=220 + i)
        Button(self.window_2, text="Previous", width='10', height='2',
               command=lambda: [self.window_2.destroy(), self.window_1.deiconify()],
               font=("Arial", 10, "bold")).place(x=100, y=700)

    def component_right_frame(self, curr_layer, curr_comp):
        RFrame = self.window_2
        Label(RFrame, text="1. Component Defaults (Not Mandatory)\n"
                           "(Hardcoded value)",
              font=("Arial Bold", 9)).place(x=850, y=45)
        Label(RFrame, text="Component Label*").place(x=850, y=85)
        Label(RFrame, text="Component Type*").place(x=850, y=115)
        Label(RFrame, text="Dimension Unit").place(x=850, y=145)
        Label(RFrame, text="Network Measure").place(x=850, y=175)
        Label(RFrame, text="Design Life").place(x=850, y=205)
        Label(RFrame, text="Material Type").place(x=850, y=235)
        try:
            # if we have the information in the existing file for the current component
            existing_component = self.existing_layer[curr_layer]["components"][curr_comp]["componentdefaults"]

            self.c_label_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_component["label"]),
                                         width=40)

            self.c_type_default = Entry(RFrame,
                                        textvariable=StringVar(RFrame, value=existing_component["component_type"]),
                                        width=40)

            self.c_dimension_unit_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_component[
                "dimension_unit"]),
                                                  width=40)
            self.c_network_measure_type_default = Entry(RFrame,
                                                        textvariable=StringVar(RFrame, value=existing_component[
                                                            "network_measure_type"]),
                                                        width=40)

            self.c_design_life_default = Entry(RFrame,
                                               textvariable=StringVar(RFrame, value=existing_component["design_life"]),
                                               width=40)
            self.c_material_type_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_component[
                "material_type"]),
                                                 width=40)

        except KeyError:

            self.c_label_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.c_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.c_dimension_unit_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.c_network_measure_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.c_design_life_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.c_material_type_default = Entry(RFrame, textvariable=StringVar(), width=40)

        self.c_label_default.place(x=1100, y=85)
        self.c_type_default.place(x=1100, y=115)
        self.c_dimension_unit_default.place(x=1100, y=140)
        self.c_network_measure_type_default.place(x=1100, y=175)
        self.c_design_life_default.place(x=1100, y=205)
        self.c_material_type_default.place(x=1100, y=235)


class XMl_Prompter_for_Dimension:
    extra_fields = 6
    extra_dimen_fields = 3
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'

    def __init__(self, master, layer_dict=None, existing_layer=None):
        self.existing_layer = existing_layer
        self.master = master
        self.max_num = {}

        self.layer_dict = layer_dict
        api_client = ApiClient()
        self.api_client = api_client
        self.logger = api_client.configuration.packagelogger

        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())

        """
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic XML Prompter for Dimension")
        self.width = master.winfo_screenwidth()
        self.height = master.winfo_screenheight()
        # setting tkinter window size
        master.geometry("%dx%d" % (self.width, self.height))
        master.header = Label(master, text="XML Prompter for Dimension", font=("Arial", 40, "bold")).place(x=450, y=80)

        if os.path.exists(self.save_path):
            message = "arcmap_edit_config.xml file already exists in \n" \
                      "" \
                      "{0} ".format(self.save_path)
            Button(master, text="Start", width='20', height='2',
                   command=lambda: self.window_1_(), bg="#349cbc", fg='gray92').place(
                x=650,
                y=600)
        else:
            message = "XML Prompter for asset should be run first"

        Label(master, text=message).place(x=500, y=300)
        """

    def window_1_(self):
        self.master.withdraw()
        window_1 = Toplevel(self.master)
        self.window_1 = window_1
        self.width = self.window_1.winfo_screenwidth() * .9
        self.height = self.window_1.winfo_screenheight() * .9
        # setting tkinter window size
        self.window_1.geometry("%dx%d" % (self.width, self.height))
        self.window_1.header = Label(
            self.window_1, text="Dimension Configuration",
            font=("Arial", 12, "bold")).place(x=self.width/2, y=20)
        option = [i for i in range(self.extra_fields)]
        self.select_number = StringVar()
        self.select_number.set(option[0])

        if (self.existing_layer):

            # if existing layer is more than the maximum , set it to the maximum fields

            if (len(self.existing_layer)) > self.extra_fields:
                num_layers = self.extra_fields
            else:
                num_layers = len(self.existing_layer)
            self.select_number.set(num_layers)
            self.ok()


        else:
            # else if there wasnt any file detected, choose the number of layer, it is wrong
            messagebox.showerror("Error", "XML Prompter for asset should be run first")
            return

    def ok(self):
        number = self.select_number.get()
        l_label = {}
        self.d_button_new = {}
        self.d_label_button_new = {}
        self.d_button = {}
        self.delete_button = {}
        self.d_new_label = {}
        option = [i for i in range(self.extra_fields)]
        self.select_c_number = StringVar()
        self.select_c_number.set(option[0])
        row_num = 1
        for i in range(1, int(number) + 1):
            self.curr_layer = i
            # layer start from1
            self.d_button_new[i] = {}
            self.d_label_button_new[i] = {}
            self.d_button[i] = {}
            self.delete_button[i] = {}
            self.d_new_label[i] = {}

            if i <= 3:
                l_label[i] = Label(self.window_1,
                                   text="{0}. Layer: {1}:".format(i, self.existing_layer[i]["layer_name"]))
                l_label[i].place(x=20, y=(row_num * 30) + 40)
                print("label layer {0} row {1} {2}".format(
                    i, row_num, (row_num * 30) + 40))
                row_num += 1
            else:
                l_label[i] = Label(self.window_1,
                                   text="{0}. Layer: {1}:".format(i, self.existing_layer[i]["layer_name"]))
                l_label[i].place(x=800, y=(i - 3) * 220 - 150)

            if len(self.existing_layer[i]["components"]):
                # if component found
                if len(self.existing_layer[i]["components"]) > self.extra_fields:
                    num_component = self.extra_fields
                else:
                    num_component = (len(self.existing_layer[i]["components"]))
                self.select_c_number.set(num_component)
                curr_layer = i

                self.ok_component(curr_layer, row_num)
                row_num += num_component


            else:
                message = "No Component Found"
                if i > 3:
                    Label(self.window_1, text=message).place(x=800, y=(i - 3) * 220 - 120)
                else:
                    Label(self.window_1, text=message).place(
                        x=20, y=(row_num * 30) + 40)
                    print("No component row {0} {1}".format(
                        row_num, (row_num * 30) + 40))
                    row_num += 1

    def view_component(self, curr_layer, curr_comp):
        window_2 = Toplevel(self.master)
        window_2.title("Assetic XML Prompter for Component")
        window_2.geometry("%dx%d" % (self.width, self.height))
        adjust = 40
        self.window_2 = window_2

        Label(window_2, text="Component Number :{0}".format(curr_layer)
              , font=("Arial Bold", 13)).place(x=15, y=15)
        Label(window_2, text="1. Component Fields\n"
                             "(GIS Field Name)", font=("Arial Bold", 9)).place(x=15, y=10 + adjust)

        Label(window_2, text="Component Label*").place(x=15, y=50 + adjust)
        Label(window_2, text="Component Type*").place(x=15, y=80 + adjust)
        Label(window_2, text="Dimension Unit").place(x=15, y=110 + adjust)
        Label(window_2, text="Network Measure").place(x=15, y=140 + adjust)
        Label(window_2, text="Design Life").place(x=15, y=170 + adjust)
        Label(window_2, text="Material Type").place(x=15, y=200 + adjust)
        Label(window_2, text="1. Component Defaults\n"
                             "(Hardcoded value)",
              font=("Arial Bold", 9)).place(x=850, y=10 + adjust)
        Label(window_2, text="Component Label*").place(x=850, y=50 + adjust)
        Label(window_2, text="Component Type*").place(x=850, y=80 + adjust)
        Label(window_2, text="Dimension Unit").place(x=850, y=110 + adjust)
        Label(window_2, text="Network Measure").place(x=850, y=140 + adjust)
        Label(window_2, text="Design Life").place(x=850, y=170 + adjust)
        Label(window_2, text="Material Type").place(x=850, y=200 + adjust)
        try:
            componentdefaults = self.existing_layer[curr_layer]["components"][curr_comp]["componentdefaults"]
            Label(window_2, text="{0}".format(componentdefaults["label"])).place(x=250, y=50 + adjust)
            Label(window_2, text="{0}".format(componentdefaults["component_type"])).place(x=250, y=80 + adjust)
            Label(window_2, text="{0}".format(componentdefaults["dimension_unit"])).place(x=250, y=110 + adjust)
            Label(window_2, text="{0}".format(componentdefaults["network_measure_type"])).place(x=250, y=140 + adjust)
            Label(window_2, text="{0}".format(componentdefaults["material_type"])).place(x=250, y=170 + adjust)
            Label(window_2, text="{0}".format(componentdefaults["design_life"])).place(x=1100, y=200 + adjust)
        except:
            Label(window_2, text=None).place(x=250, y=50 + adjust)
            Label(window_2, text=None).place(x=250, y=80 + adjust)
            Label(window_2, text=None).place(x=250, y=110 + adjust)
            Label(window_2, text=None).place(x=250, y=140 + adjust)
            Label(window_2, text=None).place(x=250, y=170 + adjust)
            Label(window_2, text=None).place(x=250, y=200 + adjust)

        try:
            comp_corefields = self.existing_layer[curr_layer]["components"][curr_comp]["componentfields"]

            Label(window_2, text="{0}".format(comp_corefields["label"])).place(x=1100, y=50 + adjust)
            Label(window_2, text="{0}".format(comp_corefields["component_type"])).place(x=1100, y=80 + adjust)
            Label(window_2, text="{0}".format(comp_corefields["dimension_unit"])).place(x=1100, y=110 + adjust)
            Label(window_2, text="{0}".format(comp_corefields["network_measure_type"])).place(x=1100, y=140 + adjust)
            Label(window_2, text="{0}".format(comp_corefields["material_type"])).place(x=1100, y=170 + adjust)
            Label(window_2, text="{0}".format(comp_corefields["design_life"])).place(x=1100, y=200 + adjust)
        except:
            Label(window_2, text=None).place(x=1100, y=50 + adjust)
            Label(window_2, text=None).place(x=1100, y=80 + adjust)
            Label(window_2, text=None).place(x=1100, y=110 + adjust)
            Label(window_2, text=None).place(x=1100, y=140 + adjust)
            Label(window_2, text=None).place(x=1100, y=170 + adjust)
            Label(window_2, text=None).place(x=1100, y=200 + adjust)
        Button(self.window_2, text="Previous", width='10', height='2',
               command=lambda: [self.window_2.destroy()],
               font=("Arial", 10, "bold")).place(x=100, y=700)

    def ok_component(self, curr_layer, row_num):
        number = self.select_c_number.get()

        row_num -= 1  # since j starts at 1 it will cause a gap at the start

        c_label = {}
        view_Button = {}

        self.select_d_number = {}

        for j in range(1, int(number) + 1):
            self.d_button[curr_layer][j] = {}
            self.delete_button[curr_layer][j] = {}
            self.d_new_label[curr_layer][j] = {}

            view_Button[j] = Button(self.window_1, text='View', height=1,
                                    width=4, font='Helvetica 8',
                                    command=lambda curr_comp=j: self.view_component(curr_layer, curr_comp))
            c_label[j] = Label(self.window_1, text="{0}. Component: {1}:".format(j, j))
            if curr_layer <= 3:
                #c_label[j].place(x=60, y=(j * 30 + 70) + (curr_layer - 1) * 220)
                #view_Button[j].place(x=10, y=j * 30 + 70 + (curr_layer - 1) * 220)
                c_label[j].place(x=60, y=(row_num + j) * 30 + 40)
                view_Button[j].place(x=10, y=(row_num + j) * 30 + 40)
            else:
                c_label[j].place(x=840, y=(j * 30 + 70) + +(curr_layer - 4) * 220)
                view_Button[j].place(x=790, y=j * 30 + 70 + (curr_layer - 4) * 220)
            # if there is a dimension exist
            if (len(self.existing_layer[curr_layer]["components"][j]["dimension"])) > 0:
                Label(self.window_1, text="Note: ", font=("Arial Bold", 8)).place(x=1100, y=670)
                Label(self.window_1, text="'-' : Delete ", font=("Arial Bold", 8)).place(x=1300, y=690)
                Label(self.window_1, text="Order", font=("Arial Bold", 8)).place(x=1100, y=690)
                Label(self.window_1, text="1. Delete Dimension if needed",
                      font=("Arial Bold", 8)).place(x=1100, y=710)
                if (len(self.existing_layer[curr_layer]["components"][j]["dimension"])) > self.extra_dimen_fields:
                    num_dim = self.extra_dimen_fields
                else:
                    num_dim = (len(self.existing_layer[curr_layer]["components"][j]["dimension"]))

                for a in range(1, num_dim + 1):
                    self.d_new_label[curr_layer][j][a] = Label(self.window_1, text="", font='Helvetica 8')
                    self.d_button[curr_layer][j][a] = Button(self.window_1, text='{0}. Current Dim'.format(a), height=1,
                                                             width=11, font='Helvetica 10',
                                                             command=lambda curr_comp=j, curr_dim=a: self.window_3_(
                                                                 curr_layer, curr_comp, curr_dim,
                                                                 button_index=curr_dim))
                    # https://stackoverflow.com/questions/7105874/valueerror-unichr-arg-not-in-range0x10000-narrow-python-build/7107319
                    # http://www.alanwood.net/demos/wingdings.html
                    # 128502
                    self.delete_button[curr_layer][j][a] = Button(
                        self.window_1, text=struct.pack('i', 10062).decode(
                            'utf-32'), height=1, width=1,
                        fg="red", font=("Unicode", 14),
                                                                  command=lambda curr_comp=j,
                                                                                 curr_dim=a: self.delete_dimension(
                                                                      curr_layer,
                                                                      curr_comp,
                                                                      curr_dim, button_index=curr_dim))
                    if curr_layer <= 3:
                        """
                        self.d_new_label[curr_layer][j][a].place(x=70 + a * 130, y=j * 30 + 70 + (curr_layer - 1) * 220)

                        self.d_button[curr_layer][j][a].place(x=70 + a * 130, y=j * 30 + 70 + (curr_layer - 1) * 220)
                        self.delete_button[curr_layer][j][a].place(x=170 + a * 130,
                                                                   y=j * 30 + 70 + (curr_layer - 1) * 220)
                        """
                        self.d_new_label[curr_layer][j][a].place(x=70 + a * 130, y=(row_num + j) * 30 + 40)

                        self.d_button[curr_layer][j][a].place(x=70 + a * 130, y=(row_num + j) * 30 + 40)
                        self.delete_button[curr_layer][j][a].place(
                            x=170 + a * 130,
                            y=(row_num + j) * 30 + 40)
                    else:
                        self.d_new_label[curr_layer][j][a].place(x=850 + a * 130,
                                                                 y=j * 30 + 70 + (curr_layer - 4) * 220)
                        self.d_button[curr_layer][j][a].place(x=850 + a * 130, y=j * 30 + 70 + (curr_layer - 4) * 220)
                        self.delete_button[curr_layer][j][a].place(x=950 + a * 130,
                                                                   y=j * 30 + 70 + (curr_layer - 4) * 220)
                option = [k for k in range(
                    self.extra_dimen_fields - len(self.existing_layer[curr_layer]["components"][j]["dimension"]))]

                if option:
                    self.max_num[j] = max(option) + 1
                    self.select_d_number[j] = ttk.Combobox(self.window_1, values=option,
                                                           width=5)
                    curr_row_num = row_num + j - 1
                    self.add_dim_button(curr_layer, j, a, row_num=curr_row_num)


            else:
                option = [k for k in range(self.extra_dimen_fields)]
                self.max_num[j] = max(option) + 1
                self.select_d_number[j] = ttk.Combobox(self.window_1, values=option,
                                                       width=5)
                a = 0
                curr_row_num = row_num + j - 1
                self.add_dim_button(curr_layer, j, a, curr_row_num)
            """
            Button(self.window_1, text="Finish", width='10', height='2',
                   command=lambda: self.master.destroy(), bg="#349cbc", fg='gray92').place(x=700, y=700)
            """
            Button(self.window_1, text="Finish", width='10', height='2',
                   command=lambda: self.window_1.destroy(), bg="#349cbc",
                   fg='gray92').place(x=self.width - 100, y=self.height -100)

    def add_dim_button(self, curr_layer, curr_comp, curr_dim, row_num):
        """curr_comp in the i th layer"""
        number = self.max_num[curr_comp]

        print ("row num start of comps {0}".format(row_num))
        self.d_button_new[curr_layer][curr_comp] = {}
        self.d_label_button_new[curr_layer][curr_comp] = {}
        start = 0
        for m in range(1, int(number) + 1):

            self.d_label_button_new[curr_layer][curr_comp][m] = Label(self.window_1, text="", font='Helvetica 8')
            self.d_button_new[curr_layer][curr_comp][m] = Button(
                self.window_1,
                text='', height=1,
                width=10, font='Helvetica 10', bd=0,
                command=lambda k=m, j=curr_comp: self.add_button_clicked(
                    curr_layer, curr_comp, curr_dim + k,
                    button_index=k, add=1)
            )

            if curr_layer <= 3:
                if start == 0:
                    self.d_button_new[curr_layer][curr_comp][m].configure(bd=1, text="Add Dim")
                    start += 1

               # self.d_button_new[curr_layer][curr_comp][m].place(x=70 + (curr_dim + m) * 130,
                #                                                  y=(
                #                                                  curr_comp * 30 + 70 + (curr_layer - 1) * 220))
                print("row num {0} and m {1}".format(row_num,m))
                self.d_button_new[curr_layer][curr_comp][m].place(
                    x=70 + (curr_dim + m) * 130,
                    y=(row_num + m) * 30 + 40)
                # self.d_label_button_new[curr_layer][curr_comp][m].place(x=70 + (curr_dim + m) * 130, y=(
                #         curr_comp * 30 + 70 + (curr_layer - 1) * 220))
                self.d_label_button_new[curr_layer][curr_comp][m].place(
                    x=70 + (curr_dim + m) * 130, y=(row_num + m) * 30 + 40)
            else:
                if start == 0:
                    self.d_button_new[curr_layer][curr_comp][m].configure(bd=1, text="Add Dim")
                    start += 1

                self.d_button_new[curr_layer][curr_comp][m].place(x=850 + (curr_dim + m) * 130,
                                                                  y=(curr_comp * 30 + 70 + (curr_layer - 4) * 220))
                self.d_label_button_new[curr_layer][curr_comp][m].place(
                    x=850 + (curr_dim + m) * 130
                    , y=(row_num + curr_comp) * 30 + 40)

    def delete_dimension(self, curr_layer, curr_comp, curr_dim, button_index=None):
        self.add_dim_to_xml_file(curr_layer, curr_comp, curr_dim, delete=1, button_index=button_index)

    def add_button_clicked(self, curr_layer, curr_comp, curr_dim
                           , button_index=None, add=None):

        # ghost the delete buttons
        del_keys1 = self.delete_button.keys()
        for i in del_keys1:
            if len(self.delete_button[i].keys()) > 0:
                del_keys2 = self.delete_button[i].keys()
                for j in del_keys2:
                    if len(self.delete_button[i][j].keys()) > 0:
                        del_keys3 = self.delete_button[i][j].keys()
                    for k in del_keys3:
                        self.delete_button[i][j][k]["state"] = \
                            "disabled"

        self.window_3_(curr_layer, curr_comp, curr_dim,button_index, add)

    def window_3_(self, curr_layer, curr_comp, curr_dim, button_index=None, add=None):

        self.window_1.withdraw()

        window_3 = Toplevel(self.master)
        self.window_3 = window_3
        window_3.title("Assetic XML Prompter")
        self.width = window_3.winfo_screenwidth()
        self.height = window_3.winfo_screenheight()
        # setting tkinter window size
        window_3.geometry("%dx%d" % (self.width, self.height))
        Label(window_3,
              text="Once save button is clicked, the existing "
                   "configuration file will be modified",
              fg="red", font='Helvetica 11 underline').place(x=500, y=600)
        self.dim_left_frame(curr_layer, curr_comp, curr_dim)
        self.dim_right_frame(curr_layer, curr_comp, curr_dim)
        self.button_save = Button(window_3, text="Save", width='20', height='2',
                                  command=lambda: self.add_dim_to_xml_file(curr_layer, curr_comp, curr_dim,
                                                                           button_index=button_index, add=add),
                                  bg="#349cbc", fg='gray92').place(x=750, y=700)

    def add_dim_to_xml_file(self, curr_layer, curr_comp, curr_dim, delete=0, button_index=None, add=None):
        layer = 1
        dim_num = 1
        comp_num = 1
        found = 0

        if os.path.isfile(self.save_path):
            tree = ET.parse(self.save_path)

        else:
            messagebox.showerror("Error", "No arcmap_edit_config.xml is found")
            return
        root = tree.getroot()
        # check if there is a layer name
        for operation in root.iter('operation'):
            action = operation.get("action")
            if action == "Asset":
                for onelayer in operation.iter("layer"):
                    if onelayer.get("name") == self.existing_layer[curr_layer]["layer_name"]:
                        # if  components found within a layer
                        comp_num = 1
                        for one_component in onelayer.iter("components"):

                            c_defaults = one_component.find("componentdefaults")
                            c_fields = one_component.find("componentfields")

                            try:
                                l = c_defaults.find("label")
                                label = l.text

                            except:
                                l = c_fields.find("label")
                                label = l.text
                            try:
                                # use try because existing component maynot have component,component default or component fields
                                label_default = \
                                    self.existing_layer[curr_layer]["components"][curr_comp]["componentdefaults"][
                                        "label"]
                            except:
                                label_default = None
                            try:
                                label_field = \
                                    self.existing_layer[curr_layer]["components"][curr_comp]["componentfields"][
                                        "label"]
                            except:
                                label_field = None
                            if label == label_default or label == label_field:
                                one_dimen = one_component.find('dimension')
                                if one_dimen is None:
                                    one_dimen = ET.SubElement(one_component, "dimension")
                                    dimensiondefaults = ET.SubElement(one_dimen, "dimensiondefaults")
                                else:
                                    dim_num = 1
                                    found = 0
                                    lst = []

                                    for one_dimen in one_component.iter("dimension"):
                                        dimensiondefaults = one_dimen.find("dimensiondefaults")
                                        dimension_corefields = one_dimen.find("dimensionfields")

                                        try:
                                            unit = dimensiondefaults.find("unit").text

                                            record_type = dimensiondefaults.find("record_type").text

                                            network_measure_type = dimensiondefaults.find("network_measure_type").text
                                            lst.append([unit, record_type, network_measure_type])

                                        except:
                                            unit = dimension_corefields.find("unit").text
                                            record_type = dimension_corefields.find("record_type").text
                                            network_measure_type = dimension_corefields.find(
                                                "network_measure_type").text
                                            lst.append([unit, record_type, network_measure_type])
                                        try:
                                            # use try because existing component maynot have component,component default or component fields
                                            default_unit = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensiondefaults"]["unit"]
                                            default_record_type = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensiondefaults"]["record_type"]
                                            default_network_measure_type = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensiondefaults"]["network_measure_type"]


                                        except:
                                            default_unit = None
                                            default_record_type = None
                                            default_network_measure_type = None
                                        try:
                                            field_unit = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensionfields"]["unit"]
                                            field_record_type = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensionfields"]["record_type"]
                                            field_network_measure_type = \
                                                self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][
                                                    curr_dim][
                                                    "dimensionfields"]["network_measure_type"]

                                        except:
                                            field_unit = None
                                            field_record_type = None
                                            field_network_measure_type = None
                                        if (
                                                unit == default_unit and record_type == default_record_type and network_measure_type == default_network_measure_type) or (
                                                unit == field_unit and
                                                record_type == field_record_type and network_measure_type == field_network_measure_type) and add != 1:

                                            found = 1
                                            if delete:
                                                one_component.remove(one_dimen)
                                                break;

                                            if ([self.d_unit_default.get(), self.d_record_type_default.get(),
                                                 self.d_network_measure_type_default.get()] in lst) or (
                                                    [self.d_unit_field.get(), self.d_record_type_field.get(),
                                                     self.d_network_measure_type_field.get()] in lst and [
                                                        self.d_unit_field.get(), self.d_record_type_field.get(),
                                                        self.d_network_measure_type_field.get()] != [field_unit,
                                                                                                     field_record_type,
                                                                                                     field_network_measure_type]):
                                                messagebox.showerror("Error", "Do not provide duplicate Dimension")
                                                return

                                            if dimensiondefaults is None:
                                                dimensiondefaults = ET.SubElement(one_dimen, "dimensiondefaults")
                                            break
                                        dim_num += 1
                                    if found == 0 and add != 1 and not delete:
                                        messagebox.showerror("Error",
                                                             "Unable to edit because existing dimension not found"
                                                             )
                                        return
                                    if delete:
                                        break
                                    if found == 0:

                                        if ([self.d_unit_default.get(), self.d_record_type_default.get(),
                                             self.d_network_measure_type_default.get()] in lst
                                        ) or \
                                                ([self.d_unit_field.get(), self.d_record_type_field.get(),
                                                  self.d_network_measure_type_field.get()] in lst):
                                            messagebox.showerror("Error", "Do not provide duplicate Dimension")
                                            return

                                        one_dimen = ET.SubElement(one_component, "dimension")
                                        dimensiondefaults = one_dimen.find("dimensiondefaults")
                                        if dimensiondefaults is None:
                                            dimensiondefaults = ET.SubElement(one_dimen, dimensiondefaults)
                                unit_default = None
                                record_type_default = None
                                network_measure_type_default = None

                                if self.d_unit_default.get() not in ["", ' ', None]:
                                    d_unit_default = dimensiondefaults.find("unit")
                                    if d_unit_default is None:
                                        d_unit_default = ET.SubElement(dimensiondefaults, "unit")
                                    d_unit_default.text = self.d_unit_default.get()
                                    unit_default = self.d_unit_default.get()
                                if self.d_record_type_default.get() not in ["", ' ', None]:
                                    d_record_type_default = dimensiondefaults.find("record_type")
                                    if d_record_type_default is None:
                                        d_record_type_default = ET.SubElement(dimensiondefaults, "record_type")
                                    d_record_type_default.text = self.d_record_type_default.get()
                                    record_type_default = self.d_record_type_default.get()
                                if self.d_network_measure_type_default.get() not in ["", ' ', None]:
                                    d_network_measure_type_default = dimensiondefaults.find("network_measure_type")
                                    if d_network_measure_type_default is None:
                                        d_network_measure_type_default = ET.SubElement(dimensiondefaults,
                                                                                       "network_measure_type")
                                    d_network_measure_type_default.text = self.d_network_measure_type_default.get()
                                    network_measure_type_default = self.d_network_measure_type_default.get()

                                if self.d_network_measure_default.get() not in ["", ' ', None]:
                                    d_network_measure_default = dimensiondefaults.find("network_measure")
                                    if d_network_measure_default is None:
                                        d_network_measure_default = ET.SubElement(dimensiondefaults,
                                                                                       "network_measure")
                                    d_network_measure_default.text = self.d_network_measure_default.get()
                                    network_measure_default = self.d_network_measure_default.get()

                                if self.d_shape_name_default.get() not in ["", ' ', None]:
                                    d_shape_name_default = dimensiondefaults.find("shape_name")
                                    if d_shape_name_default is None:
                                        d_shape_name_default = ET.SubElement(dimensiondefaults, "shape_name")
                                    d_shape_name_default.text = self.d_shape_name_default.get()
                                if self.d_length_unit_default.get() not in ["", ' ', None]:
                                    d_length_unit_default = dimensiondefaults.find("length_unit")
                                    if d_length_unit_default is None:
                                        d_length_unit_default = ET.SubElement(dimensiondefaults, "length_unit")
                                    d_length_unit_default.text = self.d_length_unit_default.get()
                                if self.d_width_unit_default.get() not in ["", ' ', None]:
                                    d_width_unit_default = dimensiondefaults.find("width_unit")
                                    if d_width_unit_default is None:
                                        d_width_unit_default = ET.SubElement(dimensiondefaults, "width_unit")
                                    d_width_unit_default.text = self.d_width_unit_default.get()
                                dimension_corefields = one_dimen.find("dimensionfields")
                                if dimension_corefields is None:
                                    dimension_corefields = ET.SubElement(one_dimen, "dimensionfields")
                                unit_field = None

                                record_type_field = None
                                network_measure_type_field = None

                                if self.d_unit_field.get() not in ["", ' ', None]:
                                    d_unit_field = dimension_corefields.find("unit")
                                    if d_unit_field is None:
                                        d_unit_field = ET.SubElement(dimension_corefields, "unit")
                                    d_unit_field.text = self.d_unit_field.get()
                                    unit_field = self.d_unit_field.get()
                                if self.d_record_type_field.get() not in ["", ' ', None]:
                                    d_record_type_field = dimension_corefields.find("record_type")
                                    if d_record_type_field is None:
                                        d_record_type_field = ET.SubElement(dimension_corefields, "record_type")
                                    d_record_type_field.text = self.d_record_type_field.get()
                                    record_type_field = self.d_record_type_field.get()
                                if self.d_network_measure_field.get() not in ["", ' ', None]:
                                    d_network_measure_field = dimension_corefields.find("network_measure")
                                    if d_network_measure_field is None:
                                        d_network_measure_field = ET.SubElement(dimension_corefields,
                                                                                     "network_measure")
                                    d_network_measure_field.text = self.d_network_measure_field.get()
                                    network_measure_field = self.d_network_measure_field.get()
                                if self.d_network_measure_field.get() not in ["", ' ', None]:
                                    d_network_measure_field = dimension_corefields.find("network_measure")
                                    if d_network_measure_field is None:
                                        d_network_measure_field = ET.SubElement(dimension_corefields,
                                                                                     "network_measure")
                                    d_network_measure_field.text = self.d_network_measure_field.get()
                                    network_measure_field = self.d_network_measure_field.get()
                                if self.d_shape_name_field.get() not in ["", ' ', None]:
                                    d_shape_name_field = dimension_corefields.find("shape_name")
                                    if d_shape_name_field is None:
                                        d_shape_name_field = ET.SubElement(dimension_corefields, "shape_name")
                                    d_shape_name_field.text = self.d_shape_name_field.get()
                                if self.d_length_unit_field.get() not in ["", ' ', None]:
                                    d_length_unit_field = dimension_corefields.find("length_unit")
                                    if d_length_unit_field is None:
                                        d_length_unit_field = ET.SubElement(dimension_corefields, "length_unit")
                                    d_length_unit_field.text = self.d_length_unit_field.get()
                                if self.d_width_unit_field.get() not in ["", ' ', None]:
                                    d_width_unit_field = dimension_corefields.find("width_unit")
                                    if d_width_unit_field is None:
                                        d_width_unit_field = ET.SubElement(dimension_corefields, "width_unit")
                                    d_width_unit_field.text = self.d_width_unit_field.get()
                                if unit_default is None and unit_field is None:
                                    messagebox.showerror("Error", "Dimension Unit need to select to save dimension")
                                    return
                                if record_type_default is None and record_type_field is None:
                                    messagebox.showerror("Error", "Record Type need to select to save dimension")
                                    return
                                if network_measure_type_field is None and network_measure_type_default is None:
                                    messagebox.showerror("Error",
                                                         "Network Measure type need to select to save dimension")
                                    return

                            comp_num += 1
                        if delete:
                            break

                    layer += 1

        messagebox.showinfo('Info', 'Successfully Saved')
        dom = xml.dom.minidom.parseString(ET.tostring(root))
        xmlstring = dom.toprettyxml(encoding='UTF-8')
        dom_string = b'\n'.join([s for s in xmlstring.splitlines() if s.strip()])
        with open(self.save_path, 'wb') as file:
            file.write(dom_string)
            file.close()
        if not delete:

            self.window_3.destroy()
            if unit_default is not None:
                unit = unit_default

            else:
                unit = unit_field
            if curr_layer <= 3:
                if found == 1:
                    self.d_new_label[curr_layer][curr_comp][button_index][
                        "text"] = "{0}. Dim with Unit\n '{1}' edited".format(curr_dim, unit)
                    self.d_button[curr_layer][curr_comp][button_index].place_forget()
                    self.delete_button[curr_layer][curr_comp][button_index].place_forget()

                else:

                    self.d_label_button_new[curr_layer][curr_comp][button_index][
                        "text"] = "{0}. Dim with Unit\n '{1}' added".format(curr_dim, unit)
                    self.d_button_new[curr_layer][curr_comp][button_index].place_forget()
                    try:
                        self.d_button_new[curr_layer][curr_comp][button_index + 1].configure(bd=1, text="Add Dim")
                    except:
                        pass
            else:
                if found == 0:
                    self.d_label_button_new[curr_layer][curr_comp][button_index][
                        "text"] = "{0}. Dim with Unit '{1}'\n  added".format(curr_dim, unit)
                    self.d_button_new[curr_layer][curr_comp][button_index].place_forget()
                    try:
                        self.d_button_new[curr_layer][curr_comp][button_index + 1].configure(bd=1, text="Add Dim")
                    except:
                        pass
                else:
                    self.d_new_label[curr_layer][curr_comp][button_index][
                        "text"] = "{0}. Dim with Unit\n '{1}' edited".format(curr_dim, unit)
                    self.d_button[curr_layer][curr_comp][button_index].place_forget()
                    self.delete_button[curr_layer][curr_comp][button_index].place_forget()
        if delete:

            try:
                # use try because existing component maynot have component,component default or component fields
                unit_default = \
                    self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][curr_dim][
                        "dimensiondefaults"][
                        "unit"]

            except:
                unit_default = None
            try:
                unit_field = \
                    self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][curr_dim]["dimensionfields"][
                        "unit"]
            except:
                unit_field = None
            if unit_default and unit_default is not None:
                unit_old = unit_default
            else:
                unit_old = unit_field

            self.d_button[curr_layer][curr_comp][button_index].place_forget()
            self.delete_button[curr_layer][curr_comp][button_index].place_forget()
            self.d_new_label[curr_layer][curr_comp][button_index][
                "text"] = "{0}. Dim with Unit\n '{1}' deleted".format(curr_dim, unit_old)

        self.window_1.deiconify()

    def dim_left_frame(self, curr_layer, curr_comp, curr_dim):
        LFrame = self.window_3
        i = 35
        start_y = 50
        height_y = 30

        Label(LFrame, text="1. Dimension Fields (GIS Field Name)", font=("Arial Bold", 9)).place(x=15, y=10 + i)

        row = 0
        y = start_y
        labels = ["Record Type", "Network Measure", "Unit"
            , "Network Measure Type"
            , "Shape Name", "Length Unit", "Width Unit"]
        for label in labels:
            # Iterate list and add labels
            y = start_y + (row * height_y)
            Label(LFrame, text=label).place(x=15, y=y + i)
            row += 1

        one_layer = self.existing_layer[curr_layer]["layer_name"]
        self.fields = []
        if one_layer in self.layer_option:
            self.fields = sorted(self.layer_dict[one_layer], key=lambda x: x.lower())
            self.fields.insert(0, " ")
        try:
            # get the 'Component Type' to help identify the component being
            # edited
            curr_comp_type = "Not Found"
            try:
                curr_comp_type = self.existing_layer[curr_layer]["components"][
                    curr_comp]["componentdefaults"]["component_type"]
            except Exception:
                curr_comp_type = self.existing_layer[curr_layer]["components"][
                    curr_comp]["componentfields"]["component_type"]
            # get the 'Dimension Type' to help identify the component being
            # edited
            curr_dim_type = "Not Found"
            try:
                curr_dim_type = self.existing_layer[curr_layer]["components"][
                    curr_comp]["dimension"][curr_dim]["dimensiondefaults"][
                    "record_type"]
            except Exception:
                curr_dim_type = self.existing_layer[curr_layer][
                    "components"][curr_comp]["dimension"][curr_dim][
                    "dimensionfields"]["record_type"]

            Label(LFrame, text="Edit Dimension in layer: {0} ;Component: {1} "
                               ";Dimension {2}"
                               "".format(one_layer, curr_comp_type,
                                         curr_dim_type)).place(x=550, y=10)

            existing_dimension = self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][curr_dim][
                "dimensionfields"]
            self.d_unit_field = ttk.Combobox(LFrame, values=[existing_dimension["unit"]], width=40)
            self.d_record_type_field = ttk.Combobox(LFrame, values=[existing_dimension["record_type"]], width=40)
            self.d_network_measure_field = ttk.Combobox(LFrame, values=[
                existing_dimension["network_measure"]], width=40)
            self.d_network_measure_type_field = ttk.Combobox(LFrame,
                                                             values=[existing_dimension["network_measure_type"]],
                                                             width=40)
            self.d_shape_name_field = ttk.Combobox(LFrame,
                                                   values=[existing_dimension["shape_name"]],
                                                   width=40)
            self.d_length_unit_field = ttk.Combobox(LFrame, values=[existing_dimension["length_unit"]], width=40)
            self.d_width_unit_field = ttk.Combobox(LFrame, values=[existing_dimension["width_unit"]], width=40)
            self.d_unit_field.current(0)
            self.d_record_type_field.current(0)
            self.d_network_measure_type_field.current(0)
            self.d_shape_name_field.current(0)
            self.d_length_unit_field.current(0)
            self.d_width_unit_field.current(0)
            self.d_unit_field.config(value=self.fields)
            self.d_record_type_field.config(value=self.fields)
            self.d_network_measure_type_field.config(value=self.fields)
            self.d_shape_name_field.config(value=self.fields)
            self.d_length_unit_field.config(value=self.fields)
            self.d_width_unit_field.config(value=self.fields)

        except KeyError:
            Label(LFrame, text="Add Dimension to layer: {0}".format(
                one_layer)).place(x=550, y=10)
            self.d_unit_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.d_record_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.d_network_measure_field = ttk.Combobox(LFrame,
                                                   values=self.fields, width=40)
            self.d_network_measure_type_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.d_shape_name_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.d_length_unit_field = ttk.Combobox(LFrame, values=self.fields, width=40)
            self.d_width_unit_field = ttk.Combobox(LFrame, values=self.fields, width=40)

        self.d_record_type_field.place(x=250, y=50 + i)
        self.d_network_measure_field.place(x=250, y=80 + i)
        self.d_unit_field.place(x=250, y=110 + i)
        self.d_network_measure_type_field.place(x=250, y=140 + i)
        self.d_shape_name_field.place(x=250, y=170 + i)
        self.d_length_unit_field.place(x=250, y=200 + i)
        self.d_width_unit_field.place(x=250, y=230 + i)
        Button(self.window_3, text="Previous", width='10', height='2',
               command=lambda: [self.window_3.destroy(), self.window_1.deiconify()],
               font=("Arial", 10, "bold")).place(x=100, y=700)

    def dim_right_frame(self, curr_layer, curr_comp, curr_dim):
        RFrame = self.window_3
        Label(RFrame, text="1. Dimension Defaults (Hardcoded value)",
              font=("Arial Bold", 9)).place(x=850, y=45)
        Label(RFrame, text="Record Type").place(x=850, y=85)
        Label(RFrame, text="Network Measure").place(x=850, y=115)
        Label(RFrame, text="Unit").place(x=850, y=145)
        Label(RFrame, text="Network Measure Type").place(x=850, y=175)
        Label(RFrame, text="Shape Name").place(x=850, y=205)
        Label(RFrame, text="Length Unit").place(x=850, y=235)
        Label(RFrame, text="Width Unit").place(x=850, y=265)

        try:
            # if we have the information in the existing file for the current component
            existing_dim = self.existing_layer[curr_layer]["components"][curr_comp]["dimension"][curr_dim][
                "dimensiondefaults"]
            self.d_unit_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_dim["unit"]), width=40)
            self.d_record_type_default = Entry(RFrame,
                                               textvariable=StringVar(RFrame, value=existing_dim["record_type"]),
                                               width=40)
            self.d_network_measure_default = Entry(RFrame,
                                               textvariable=StringVar(RFrame,
                                                                      value=existing_dim["network_measure"]),
                                               width=40)
            self.d_network_measure_type_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_dim[
                "network_measure_type"]), width=40)
            self.d_shape_name_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_dim["shape_name"]),
                                              width=40)
            self.d_length_unit_default = Entry(RFrame,
                                               textvariable=StringVar(RFrame, value=existing_dim["length_unit"]),
                                               width=40)
            self.d_width_unit_default = Entry(RFrame, textvariable=StringVar(RFrame, value=existing_dim["width_unit"]),
                                              width=40)

        except KeyError:
            self.d_unit_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.d_record_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.d_network_measure_default = Entry(RFrame,
                                                textvariable=StringVar(),
                                           width=40)
            self.d_network_measure_type_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.d_shape_name_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.d_length_unit_default = Entry(RFrame, textvariable=StringVar(), width=40)
            self.d_width_unit_default = Entry(RFrame, textvariable=StringVar(), width=40)
        self.d_record_type_default.place(x=1100, y=85)
        self.d_network_measure_default.place(x=1100, y=115)
        self.d_unit_default.place(x=1100, y=145)
        self.d_network_measure_type_default.place(x=1100, y=175)
        self.d_shape_name_default.place(x=1100, y=205)
        self.d_length_unit_default.place(x=1100, y=235)
        self.d_width_unit_default.place(x=1100, y=265)


def run_prompter(layer, existing_layer=None):
    pass


class MainMenuPrompter:
    extra_fields = 6
    extra_dimen_fields = 3
    save_path = os.environ['APPDATA'] + '\\Assetic\\arcmap_edit_config.xml'

    def __init__(self, master, layer_dict=None, existing_layer=None):
        self.existing_layer = existing_layer
        self.master = master
        self.max_num = {}

        self.layer_dict = layer_dict
        api_client = ApiClient()
        self.api_client = api_client
        self.logger = api_client.configuration.packagelogger

        if layer_dict is None:
            message = "No layer found from the file"
            self.logger.error(message)
            return
        self.layer_option = sorted(self.layer_dict.keys(), key=lambda x: x.lower())
        master.option_add('*Font', 'Helvetica 12')
        master.title("Assetic GIS Integration Configuration Builder")
        self.width = master.winfo_screenwidth() * .9
        self.height = master.winfo_screenheight() * .9
        # setting tkinter window size
        master.geometry("%dx%d" % (self.width, self.height))
        master.header = Label(
            master, text="Assetic GIS Integration Configuration Builder",
            font=("Arial", 20, "bold")).place(
            x=self.width/2, y=40, anchor=CENTER)

        if os.path.exists(self.save_path):
            message = "Using existing configuration file: \n" \
                      "" \
                      "{0} ".format(self.save_path)

            # Add buttons to initiate each level of configuration
            Button(master, text="Asset Attributes", width='30', height='2',
                   command=lambda: self.asset_window_1_(),
                   bg="#349cbc",
                   fg='gray92').place(
                x=50,
                y=350)
            Button(master, text="Component", width='30', height='2',
                   command=lambda: self.component_window_1_(),
                   bg="#349cbc",
                   fg='gray92').place(
                x=50,
                y=425)
            Button(master, text="Dimensions", width='30', height='2',
                   command=lambda: self.dimension_window_1_(),
                   bg="#349cbc",
                   fg='gray92').place(
                x=50,
                y=500)
        else:
            message = "No existing configuration file \n" \
                      "Configure asset level first"

        Label(master, text=message).place(
            x=self.width/2, y=100, anchor=CENTER)

    def asset_window_1_(self):
        self.master.withdraw()
        prompter = XMl_Prompter_for_Asset(
            self.master, layer_dict=self.layer_dict,
            existing_layer=self.existing_layer)
        prompter.window_1_()
        self.master.deiconify()

    def component_window_1_(self):
        self.master.withdraw()
        prompter = XMl_Prompter_for_Component(
            self.master, layer_dict=self.layer_dict,
            existing_layer=self.existing_layer)
        prompter.window_1_()
        self.master.deiconify()

    def dimension_window_1_(self):
        self.master.withdraw()
        prompter = XMl_Prompter_for_Dimension(
            self.master, layer_dict=self.layer_dict,
            existing_layer=self.existing_layer)
        prompter.window_1_()
        self.master.deiconify()

if __name__ == '__main__':
    assetic.AsseticSDK(None, None, "info")
    gdbfile = r"C:\Users\cynthia\Downloads\Town of Walkerville Assets.gdb"
    gdbfile = r"C:\Projects\TAS\tas_gdb\tasdata.gdb"
    # 1. Get layer
    layer = XML_Prompter_for_Layer.layer(gdbfile)
    existing_layer = XML_Prompter_for_Layer.get_existing_xml()
    """
    # 2. Layer Prompter.
    root = tk.Tk()
    prompter = XML_Prompter_for_Layer(root, layer_dict=layer, existing_layer=existing_layer)
    root.mainloop()

    # # 3. Asset Prompter. Parameter cannot be changed
    root = tk.Tk()
    existing_layer = XML_Prompter_for_Layer.get_existing_xml()
    prompter = XMl_Prompter_for_Asset(root, layer_dict=layer, existing_layer=existing_layer)
    root.mainloop()
    #
    # # 4. Component Prompter. Parameter cannot be changed
    root = tk.Tk()
    existing_layer = XML_Prompter_for_Layer.get_existing_xml()
    prompter = XMl_Prompter_for_Component(root, layer_dict=layer, existing_layer=existing_layer)
    root.mainloop()
    #
    
    # # 5. Dimension Prompter. Parameter cannot be changed
    root = tk.Tk()
    existing_layer = XML_Prompter_for_Layer.get_existing_xml()
    prompter = XMl_Prompter_for_Dimension(root, layer_dict=layer, existing_layer=existing_layer)
    root.mainloop()
    """
    root = tk.Tk()
    existing_layer = XML_Prompter_for_Layer.get_existing_xml()
    prompter = MainMenuPrompter(
        root, existing_layer=existing_layer, layer_dict=layer)
    root.mainloop()

