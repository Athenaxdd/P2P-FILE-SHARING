import os
import threading
import customtkinter
from c_server import start_server
from ping import ping
from discover import discover
from shutdown import shutdown
from tkinter import messagebox

# Support function
def get_address_list():
    address_list = ['Choose hostname']
    try:
        if not os.path.exists("peers"):
            os.makedirs("peers")
        adds = os.scandir("peers")
        for add in adds:
            address_list.append(add.name)
            print(str(add.name))
        adds.close()
    except Exception as e:
        print(f"An error occurred while retrieving the address list: {e}")
    print(address_list)
    return address_list

def get_published_files(hostname):
    files = []
    with open(f'peers/{hostname}', 'r') as f:
        while True:
            data = f.readline()
            if not data:
                break
            files.append(data.split('|')[1])
    print(files)
    return files

# Settings
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

# Frames
class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.options = get_address_list()
        
        self.fname_label = customtkinter.CTkLabel(self, text="Hostname")
        self.fname_label.grid(row=0, padx=16, pady=(4, 0), sticky="w")

        self.hostname_entry = customtkinter.CTkComboBox(self, width=229, height=40, values=self.options, command=self.handle_hostname_change)
        self.hostname_entry.grid(row=1, column=0, padx=16, pady=(0,16), sticky="we")

        self.ping_button = customtkinter.CTkButton(self, text="Ping", width=103, height=40, state='disabled', command=self.ping_button_callback)
        self.ping_button.grid(row=1, column=1, padx=16, pady=(0,16), sticky="w")

        self.discover_button = customtkinter.CTkButton(self, text="Discover", width=103, height=40, state='disabled', command=self.discover_button_callback)
        self.discover_button.grid(row=1, column=2, padx=16, pady=(0,16), sticky="w")

        self.published_file = customtkinter.CTkTextbox(self, width=500, height=250, state='normal')
        self.published_file.grid(row=2, column=0, columnspan=4, padx=16, pady=(0, 16), sticky="news")

    def ping_button_callback(self):
        hostname = self.hostname_entry.get()
        res = ping(hostname)
        if res == 0:
            messagebox.showinfo(title=f'Ping Result to {hostname}', message='Alive!')
        else:
            messagebox.showinfo(title=f'Ping Result to {hostname}', message='Not Alive!')

    def discover_button_callback(self):
        hostname = self.hostname_entry.get()
        self.published_file.configure(state='normal')
        self.published_file.delete("0.0", "end")
        data = discover(self.hostname_entry.get())
        self.published_file.insert("0.0", data)
        self.published_file.configure(state='disabled')

    def handle_hostname_change(self, hostname):
        if hostname == 'Choose hostname':
            self.ping_button.configure(state='disabled')
            self.discover_button.configure(state='disabled')
        else:
            self.ping_button.configure(state='normal')
            self.discover_button.configure(state='normal')

# Main App
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Some metadata
        self.title("P2P File Sharing System - Centralized Server")
        self.geometry("580x460")

        # Frames
        self.ping_frame = MainFrame(self)
        self.ping_frame.grid(row=1, column=0, columnspan=4)
        
        # Grid configurations
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Adding UI elements
        self.start_button = customtkinter.CTkButton(self, text="Start Server", command=self.start_button_callback)
        self.start_button.grid(row=0, column=0, padx=(24, 0), pady=24, sticky="w")

        self.shutdown_button = customtkinter.CTkButton(self, text="Shutdown Server", state='disabled', command=self.shutdown_button_callback)
        self.shutdown_button.grid(row=0, column=1, pady=24)

        self.refresh_button = customtkinter.CTkButton(self, text="Refresh", command=self.refresh_button_callback)
        self.refresh_button.grid(row=0, column=2, padx=(0, 24), pady=24, sticky="e")


    def start_button_callback(self):
        threading.Thread(target=start_server).start()
        self.start_button.configure(state='disabled')
        self.shutdown_button.configure(state='normal')

    def shutdown_button_callback(self):
        threading.Thread(target=shutdown).start()
        self.start_button.configure(state='normal')
        self.shutdown_button.configure(state='disabled')

    def refresh_button_callback(self):
        address_list = get_address_list()
        self.ping_frame.hostname_entry.configure(require_redraw=True, values=address_list)

app = App()
app.mainloop()