import urllib3
import assetic
import tkinter.font as font
import os
import configparser
from assetic import ApiClient
from assetic import Configuration, AuthApi, __version__
from tkinter import *
from tkinter import messagebox
from tkinter.messagebox import showinfo
import logging
from .vault_tools import VaultTools

try:
    import tkinter as tk  # python3
except ImportError:
    import Tkinter as tk  # python2
# urllib3.disable_warnings()
save_path = os.environ['APPDATA'] + '\\Assetic\\assetic.ini'
path = os.path.dirname(assetic.__file__)
a_list = [path, "tools", "assetic_name.gif"]
b_list = [path, "tools", "logo.gif"]
assetic_name = os.path.join(*a_list)
assetic_logo = os.path.join(*b_list)


class AuthTools(Frame):
    """
    create an ini file prompter
    """

    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        master.title('Assetic')
        master.configure()
        master.geometry('700x200')
        self.check_ini = Button(master, text='Update ini file', width='20', height='2', bg="#349cbc", fg='gray92')
        self.check_ini['command'] = self.check_ini_file
        self.create_ini = Button(master, text='Create ini file', width='20', height='2', bg="#349cbc", fg='gray92')
        self.create_ini['command'] = self.create_ini_file
        self.windows_vault = Button(master, text='Save password\n to Windows Vault', width='20', height='2',
                                    bg="#349cbc", fg='gray92')
        self.windows_vault['command'] = self.add_windows_vault
        self.create_ini.place(x=15, y=100)
        self.check_ini.place(x=240, y=100)
        self.windows_vault.place(x=495, y=100)
        self.logger = logging.getLogger(__name__)
        my_font = font.Font(family='Arial Black', size=10)
        self.check_ini['font'] = my_font
        self.create_ini['font'] = my_font
        self.windows_vault['font'] = my_font

    def check_ini_file(self):
        """check if ini file exist or not"""
        Window1(self.master)

    def create_ini_file(self):
        """create ini file"""
        Window2(self.master)

    def add_windows_vault(self):
        Window3(self.master)


class Window1:
    """
    Show existing ini file
    """

    def __init__(self, master):
        self.master = master
        self.newWindow = Toplevel(self.master)
        self.newWindow.title("Update ini file")
        self.newWindow.configure()
        assetic_names = PhotoImage(file=assetic_name)
        canvas = Canvas(self.newWindow, width=300, height=100)
        canvas.create_image(20, 20, anchor=NW, image=assetic_names)
        canvas.theimage = assetic_names
        canvas.pack()
        icon = PhotoImage(file=assetic_logo)
        self.newWindow.tk.call('wm', 'iconphoto', self.newWindow._w, icon)
        self.newWindow.geometry('500x500')
        config = configparser.ConfigParser()
        config.read(save_path)
        my_font = font.Font(family='Arial Black', size=10)
        w = Text(self.newWindow, height=2, borderwidth=0)
        w.insert(1.0, "Once updated, paste the path below to file explorer and find assetic.ini file\n"
                      "%AppData%/assetic")
        w.configure(font=("Arial", 8, "bold"), foreground="#273746")
        w.pack(side=BOTTOM)
        w.configure(state="disabled")
        try:
            self.username_info = config.get("auth", "username")
            self.environment_info = config.get("environment", "url")
            self.username = Label(self.newWindow, text="Username:")
            self.username_text = Label(self.newWindow, text=self.username_info)
            self.environment = Label(self.newWindow, text="Url:", fg='black')
            self.environment_text = Label(self.newWindow, text=self.environment_info)
            self.password_text = Label(self.newWindow, text='Password ')
            self.password = StringVar()
            self.password_entry = Entry(self.newWindow, textvariable=self.password, show='*', width='50')
            self.button = Button(self.newWindow, text='Update', width='20', height='2', bg="#349cbc", fg='gray92')
            self.button['command'] = self.update_info
            self.button['font'] = my_font
            self.username['font'] = my_font
            self.environment['font'] = my_font
            self.password_text['font'] = my_font
            self.username.pack()
            self.environment.pack()
            self.username.place(x=15, y=100)
            self.username_text.place(x=15, y=140)
            self.environment.place(x=15, y=260)
            self.environment_text.place(x=15, y=300)
            self.password_entry.place(x=15, y=220)
            self.password_text.place(x=15, y=180)
            self.button.place(x=250, y=350)
        except:
            self.message = Label(self.newWindow, text="either assetic.ini file is not found in the app data\n"
                                                      "or username and environment is missing in the assetic.ini",
                                 font=9, fg="black")
            my_font = font.Font(family='Arial', size=10)
            self.message['font'] = my_font
            self.message.pack()
            self.message.place(x=100, y=200)
        self.button_exit = Button(self.newWindow, text="Exit", width='20', height='2', command=self.newWindow.destroy,
                                  bg="#349cbc", fg='gray92')
        self.button_exit['font'] = my_font
        self.button_exit.place(x=15, y=350)

    def update_info(self):
        """
        update the api key in ini file
        """
        self.password_info = self.password.get()
        config_ = Configuration()
        config_.host = self.environment_info
        config_.username = self.username_info
        config_.password = self.password_info
        auth = config_.get_basic_auth_token()
        try:
            client = ApiClient(config_, "Authorization", auth)
            client.user_agent = "Assetic_Python_SDK_{0}".format(__version__)
            auth_api = AuthApi(client)
            response = auth_api.auth_get_token()
            config = configparser.ConfigParser()
            config.read(save_path)
            config.set("auth", "api_key", response)
            with open(save_path, 'w') as configfile:
                config.write(configfile)
            showinfo(title='Information', message='Your credentials have been successfully updated')
            self.newWindow.destroy()

        except:
            messagebox.showerror('Error', 'Wrong Password')
            self.password_entry.delete(0, END)


class Window3:
    """
    save credentials to Windows Vault
    """

    def __init__(self, master):
        self.master = master
        self.newWindow = Toplevel(self.master)
        my_font = font.Font(family='Arial Black', size=10)
        self.newWindow.title("Assetic")
        self.newWindow.geometry('650x500')
        assetic_names = PhotoImage(file=assetic_name)
        canvas = Canvas(self.newWindow, width=300, height=100)
        canvas.create_image(20, 20, anchor=NW, image=assetic_names)
        canvas.theimage = assetic_names
        canvas.pack()
        logo = PhotoImage(file=assetic_logo)
        self.newWindow.tk.call('wm', 'iconphoto', self.newWindow._w, logo)
        self.username_text = Label(self.newWindow, text='Username ')
        self.password_text = Label(self.newWindow, text='Password ')
        self.environment_text = Label(self.newWindow, text='Url (start with https://)')
        self.username = StringVar()
        self.password = StringVar()
        self.environment = StringVar()
        self.username_entry = Entry(self.newWindow, textvariable=self.username, width='50')
        self.password_entry = Entry(self.newWindow, textvariable=self.password, show='*', width='50')
        self.environment_entry = Entry(self.newWindow, textvariable=self.environment, width='50')
        self.button_exit = Button(self.newWindow, text="Exit", width='20', height='2', command=self.newWindow.destroy,
                                  bg="#349cbc", fg='gray92')
        self.button_save_encode = Button(self.newWindow, text="Save & Encode", width='20', height='2',
                                         command=self.newWindow.destroy,
                                         bg="#349cbc", fg='gray92')
        self.button_save = Button(self.newWindow, text='Save', width='20', height='2', bg="#349cbc", fg='gray92')
        self.correct_password = 0

        self.button_save['command'] = self.save_info
        self.button_save_encode['command'] = self.save_encode_info
        self.button_save['font'] = my_font
        self.button_exit['font'] = my_font
        self.button_save_encode['font'] = my_font
        self.username_text['font'] = my_font
        self.password_text['font'] = my_font
        self.environment_text['font'] = my_font
        self.username_text.place(x=15, y=100)
        self.password_text.place(x=15, y=180)
        self.environment_text.place(x=15, y=260)
        self.username_entry.place(x=15, y=140)
        self.password_entry.place(x=15, y=220)
        self.environment_entry.place(x=15, y=300)
        self.button_exit.place(x=440, y=350)
        self.button_save.place(x=15, y=350)
        self.button_save_encode.place(x=230, y=350)

    def save_info(self):
        """
        save the information from the form
        """
        self.username_info = self.username.get()
        self.password_info = self.password.get()
        self.environment_info = self.environment.get()
        config_ = Configuration()
        config_.host = self.environment_info
        config_.username = self.username_info
        config_.password = self.password_info
        auth = config_.get_basic_auth_token()

        try:
            http = urllib3.connectionpool.connection_from_url(config_.host)
            http.request('GET', '/')
            client = ApiClient(config_, "Authorization", auth)
            client.user_agent = "Assetic_Python_SDK_{0}".format(__version__)
            auth_api = AuthApi(client)
            response = auth_api.auth_get_token()
        except urllib3.exceptions.HostChangedError as e:
            messagebox.showerror('Error', 'Include "https://" in the URL')
        except urllib3.exceptions.MaxRetryError as e:
            messagebox.showerror('Error', 'Unable to access Assetic site URL, check URL')
        except assetic.rest.ApiException as e:
            messagebox.showerror('Error', 'Wrong Password/Username')
        else:
            config = configparser.ConfigParser()
            config.add_section("auth")
            config.set('auth', "username", self.username_info)
            config.add_section("environment")
            config.set("environment", "url", self.environment_info)
            with open(save_path, 'w') as configfile:
                config.write(configfile)
            self.newWindow.destroy()
            a = VaultTools(self.environment_info, encode=0)
            a.set_password(self.username_info, response)
            showinfo(title='Information', message='Your password has been saved in Windows vault')
            self.newWindow.destroy()

    def save_encode_info(self):
        """
        save the information from the form
        """
        self.username_info = self.username.get()
        self.password_info = self.password.get()
        self.environment_info = self.environment.get()
        config_ = Configuration()
        config_.host = self.environment_info
        config_.username = self.username_info
        config_.password = self.password_info
        auth = config_.get_basic_auth_token()

        try:
            http = urllib3.connectionpool.connection_from_url(config_.host)
            http.request('GET', '/')
            client = ApiClient(config_, "Authorization", auth)
            client.user_agent = "Assetic_Python_SDK_{0}".format(__version__)
            auth_api = AuthApi(client)
            response = auth_api.auth_get_token()
        except urllib3.exceptions.HostChangedError as e:
            messagebox.showerror('Error', 'Include "https://" in the URL')
        except urllib3.exceptions.MaxRetryError as e:
            messagebox.showerror('Error', 'Unable to access Assetic site URL, check URL')
        except assetic.rest.ApiException as e:
            messagebox.showerror('Error', 'Wrong Password/Username')
        else:
            config = configparser.ConfigParser()
            config.add_section("auth")
            config.set('auth', "username", self.username_info)
            config.add_section("environment")
            config.set("environment", "url", self.environment_info)

            with open(save_path, 'w') as configfile:
                config.write(configfile)

            self.newWindow.destroy()
            a = VaultTools(self.environment_info, encode=1)
            a.set_password(self.username_info, response)
            showinfo(title='Information', message='Your credentials have been encoded and saved in Windows vault')
            self.newWindow.destroy()


class Window2:
    """
    create ini file
    """

    def __init__(self, master):
        self.master = master
        self.newWindow = Toplevel(self.master)
        my_font = font.Font(family='Arial Black', size=10)
        self.newWindow.title("Create ini file")
        self.newWindow.geometry('500x500')
        assetic_names = PhotoImage(file=assetic_name)
        canvas = Canvas(self.newWindow, width=300, height=100)
        canvas.create_image(20, 20, anchor=NW, image=assetic_names)
        canvas.theimage = assetic_names
        canvas.pack()
        logo = PhotoImage(file=assetic_logo)
        self.newWindow.tk.call('wm', 'iconphoto', self.newWindow._w, logo)
        self.username_text = Label(self.newWindow, text='Username ')
        self.password_text = Label(self.newWindow, text='Password ')
        self.environment_text = Label(self.newWindow, text='Url (start with https://)')
        self.username = StringVar()
        self.password = StringVar()
        self.environment = StringVar()
        self.username_entry = Entry(self.newWindow, textvariable=self.username, width='50')
        self.password_entry = Entry(self.newWindow, textvariable=self.password, show='*', width='50')
        self.environment_entry = Entry(self.newWindow, textvariable=self.environment, width='50')
        self.button_exit = Button(self.newWindow, text="Exit", width='20', height='2', command=self.newWindow.destroy,
                                  bg="#349cbc", fg='gray92')
        self.button_save = Button(self.newWindow, text='Save', width='20', height='2', bg="#349cbc", fg='gray92')
        self.correct_password = 0
        self.button_save['command'] = self.save_info

        self.button_save['font'] = my_font
        self.button_exit['font'] = my_font
        self.username_text['font'] = my_font
        self.password_text['font'] = my_font
        self.environment_text['font'] = my_font
        self.username_text.place(x=15, y=100)
        self.password_text.place(x=15, y=180)
        self.environment_text.place(x=15, y=260)
        self.username_entry.place(x=15, y=140)
        self.password_entry.place(x=15, y=220)
        self.environment_entry.place(x=15, y=300)
        self.button_exit.place(x=250, y=350)
        self.button_save.place(x=15, y=350)
        w = Text(self.newWindow, height=2, borderwidth=0)
        w.insert(1.0, "Once saved, paste the path below to file explorer and find assetic.ini file\n"
                      "%AppData%/assetic")
        w.pack(side=BOTTOM)
        w.configure(font=("Arial", 8, "bold"), foreground="#273746", state="disabled")

    def save_info(self):
        """
        save the information from the form
        """
        self.username_info = self.username.get()
        self.password_info = self.password.get()
        self.environment_info = self.environment.get()
        config_ = Configuration()
        config_.host = self.environment_info
        config_.username = self.username_info
        config_.password = self.password_info
        auth = config_.get_basic_auth_token()

        try:
            http = urllib3.connectionpool.connection_from_url(config_.host)
            http.request('GET', '/')
            client = ApiClient(config_, "Authorization", auth)
            client.user_agent = "Assetic_Python_SDK_{0}".format(__version__)
            auth_api = AuthApi(client)
            response = auth_api.auth_get_token()
        except urllib3.exceptions.HostChangedError as e:
            messagebox.showerror('Error', 'Include "https://" in the URL')
        except urllib3.exceptions.MaxRetryError as e:
            messagebox.showerror('Error', 'Unable to access Assetic site URL, check URL')
        except assetic.rest.ApiException as e:
            messagebox.showerror('Error', 'Wrong Password/Username')
        else:
            config = configparser.ConfigParser()
            config.add_section("auth")
            config.set("auth", "api_key", response)
            config.set('auth', "username", self.username_info)
            config.add_section("environment")
            config.set("environment", "url", self.environment_info)

            with open(save_path, 'w') as configfile:
                config.write(configfile)
            showinfo(title='Information', message='Your credentials have been successfully saved')
            self.newWindow.destroy()


def ini_prompter():
    assetic_folder = os.environ['APPDATA'] + '\\Assetic'
    if not os.path.exists(assetic_folder):
        os.makedirs(assetic_folder)
    root = Tk()
    a = PhotoImage(file=assetic_name)
    canvas = Canvas(root, width=300, height=100)
    canvas.create_image(20, 20, anchor=NW, image=a)
    canvas.theimage = a
    canvas.pack()
    logo = PhotoImage(file=assetic_logo)
    root.tk.call('wm', 'iconphoto', root._w, logo)
    ex = AuthTools(root)
    root.mainloop()
