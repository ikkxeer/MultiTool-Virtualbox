import subprocess
import os
import tkinter as tk
import tkinter.font as font
import customtkinter
from tkinter import ttk, filedialog
import re

class VirtualBoxDiskCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("VirtualBox Disk Creator")
        self.root.geometry("400x400")
        self.virtualbox_path = tk.StringVar()
        self.selected_machine = tk.StringVar()
        self.disk_name = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        Font = font.Font(family='Helvetica')
        Font = font.Font(size=9)
        self.virtualbox_label = tk.Label(self.root, text="Seleccionar directorio de VirtualBox:")
        self.virtualbox_label.pack()

        self.virtualbox_entry = tk.Entry(self.root, textvariable=self.virtualbox_path, width=50)
        self.virtualbox_entry.insert(0, r"C:\Program Files\Oracle\VirtualBox")
        self.virtualbox_entry.pack()

        self.virtualbox_button = tk.Button(self.root, text="Seleccionar", command=self.select_virtualbox_directory, bg='#89CFF0')
        self.virtualbox_button['font'] = Font
        self.virtualbox_button.pack(pady=(5, 0))

        # Combobox for selecting VirtualBox machine
        self.machine_label = tk.Label(self.root, text="Seleccionar máquina virtual:")
        self.machine_label.pack(pady=(20, 0))

        machines_list = self.get_virtualbox_machines()
        self.machine_combobox = ttk.Combobox(self.root, values=machines_list, textvariable=self.selected_machine, width=50)
        self.machine_combobox.pack()

        # Entry for the number of disks
        self.num_disks_label = tk.Label(self.root, text="Número de discos:")
        self.num_disks_label.pack(pady=(20, 0))

        self.num_disks_entry = tk.Entry(self.root)
        self.num_disks_entry.pack()

        # Entry for the disk size in GB
        self.disk_size_label = tk.Label(self.root, text="Tamaño de cada disco (en GB):")
        self.disk_size_label.pack(pady=(20, 0))

        self.disk_size_entry = tk.Entry(self.root)
        self.disk_size_entry.pack()
        
        # Entry for the name of the disks
        self.disk_name_label = tk.Label(self.root, text="Nombre de los discos:")
        self.disk_name_label.pack(pady=(20, 0))

        self.disk_name_entry = tk.Entry(self.root, textvariable=self.disk_name)
        self.disk_name_entry.pack()

        # Button to start the disk creation process
        self.create_button = tk.Button(self.root, text="Crear Discos", command=self.create_disks, bg='#89CFF0')
        self.create_button.pack(pady=(20, 0))

    def select_virtualbox_directory(self):
        virtualbox_directory = filedialog.askdirectory()
        self.virtualbox_path.set(virtualbox_directory)

    def get_virtualbox_machines(self):
        try:
            virtualbox_path = self.virtualbox_path.get()
            os.chdir(virtualbox_path)
            machines_list = subprocess.run(["VBoxManage", "list", "vms"], capture_output=True, text=True)
            machines = machines_list.stdout.splitlines()
            return machines
        except Exception as e:
            print(f"Error obtaining VirtualBox machines: {e}")
            return []

    def create_disks(self):
        virtualbox_path = self.virtualbox_path.get()
        selected_machine_str = self.machine_combobox.get()

        # Extract the machine name from the selected item in the combobox
        selected_machine_match = re.match(r'"(.*)"', selected_machine_str)
        if selected_machine_match:
            selected_machine = selected_machine_match.group(1)
        else:
            print("Error obtaining VirtualBox machine name. Exiting...")
            return

        try:
            os.chdir(virtualbox_path)
            print(f"Cambiado al directorio de VirtualBox: {os.getcwd()}")
        except FileNotFoundError:
            print(f"Directorio no encontrado: {virtualbox_path}")
            return
        except PermissionError:
            print(f"Error de permiso: no se puede cambiar a {virtualbox_path}")
            return

        try:
            num_disks = int(self.num_disks_entry.get())
        except ValueError:
            print("Entrada no válida para el número de discos, saliendo...")
            return

        try:
            disk_size_gb = int(self.disk_size_entry.get())
        except ValueError:
            print("Entrada no válida para el tamaño del disco, saliendo...")
            return

        disk_size_gb = disk_size_gb * 1024

        disksfolder = r"C:\Discos Virtuales"

        # Sanitize the machine name
        sanitized_machine_name = re.sub(r'[\/:*?"<>|]', '', selected_machine)

        ruta_vm = os.path.join(disksfolder, sanitized_machine_name)
        os.makedirs(ruta_vm, exist_ok=True)

        print(f"Se ha creado una carpeta específica para almacenar los discos en la siguiente ruta: {ruta_vm}")

        # Obtienes el nombre del disco que has insertado en la entrada para la asignación de nombre
        nametodisk = self.disk_name.get() if self.disk_name.get() else f"{sanitized_machine_name}_disk"

        for i in range(1, num_disks + 1):
            diskname = f"{nametodisk}_{i}"

            if os.path.isfile(os.path.join(ruta_vm, f"{diskname}.vdi")):
                print(f"El archivo de disco '{diskname}.vdi' ya existe, saliendo...")
            else:
                subprocess.run(["VBoxManage", "createhd", "--filename", os.path.join(ruta_vm, f"{diskname}.vdi"),
                                "--size", str(disk_size_gb), "--format", "VDI"])

                subprocess.run(["VBoxManage", "storageattach", selected_machine.strip('"'), "--storagectl", "SATA", "--port", str(i),
                                "--device", "0", "--type", "hdd", "--medium", os.path.join(ruta_vm, f"{diskname}.vdi")])

        print(f"{num_disks} discos creados y adjuntos a la máquina virtual {selected_machine}.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualBoxDiskCreator(root)
    root.mainloop()
