import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import psutil
import platform
import cpuinfo

class FileSearchExplorer:
    def __init__(self, master):
        self.master = master
        master.title("Explorador de Sistema Avanzado")
        master.geometry("1400x800")
        master.configure(bg="#2c3e50")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.search_pattern = tk.StringVar()
        self.stop_search = False
        self.search_thread = None
        self.tree_nodes = {}
        
        self.create_widgets()
        self.configure_exclusions()
        self.update_system_info()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 10))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='#2c3e50', rowheight=25)
        self.style.configure('Treeview.Heading', background='#2c3e50', foreground='white', font=('Arial', 10, 'bold'))
        self.style.configure('System.TFrame', background='#2c3e50')
        self.style.configure('System.TLabel', background='#2c3e50', foreground='white', font=('Arial', 10))
        
    def configure_exclusions(self):
        self.excluded_dirs = ['/proc', '/sys', '/dev', '/run', '/tmp']
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Buscar archivos:", style='TLabel').pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = ttk.Button(search_frame, text="🔍 Iniciar búsqueda", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="⏹ Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Panel principal
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Árbol de directorios
        self.tree = ttk.Treeview(paned_window, columns=('size', 'type', 'modified'), selectmode='browse')
        self.tree.heading('#0', text='Estructura de archivos', anchor=tk.W)
        self.tree.heading('size', text='Tamaño')
        self.tree.heading('type', text='Tipo')
        self.tree.heading('modified', text='Modificación')
        self.tree.column('#0', width=400)
        self.tree.column('size', width=100)
        self.tree.column('type', width=100)
        self.tree.column('modified', width=150)
        
        # Panel de sistema
        system_frame = ttk.Frame(paned_window, style='System.TFrame')
        self.create_system_panel(system_frame)
        
        paned_window.add(self.tree, weight=2)
        paned_window.add(system_frame, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self.show_path_details)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
    def create_system_panel(self, parent):
        # Marco desplazable
        canvas = tk.Canvas(parent, bg='#2c3e50', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='System.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Información del sistema
        self.system_labels = {}
        sections = [
            ('💽 Disco Duro', self.get_disk_info),
            ('🖥️ Procesador', self.get_cpu_info),
            ('🧠 Memoria RAM', self.get_ram_info),
            ('🌐 Red', self.get_network_info),
            ('⚙️ Sistema', self.get_system_info)
        ]
        
        for title, func in sections:
            frame = ttk.Frame(scrollable_frame, style='System.TFrame')
            frame.pack(fill=tk.X, padx=10, pady=5)
            ttk.Label(frame, text=title, style='System.TLabel', font=('Arial', 12, 'bold')).pack(anchor=tk.W)
            self.system_labels[title] = []
            for line in func():
                lbl = ttk.Label(frame, text=line, style='System.TLabel')
                lbl.pack(anchor=tk.W)
                self.system_labels[title].append(lbl)
            ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=5)
        
    def get_disk_info(self):
        info = []
        partitions = psutil.disk_partitions()
        for part in partitions:
            if 'snap' in part.mountpoint:
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                info.append(f"📌 {part.device} ({part.fstype})")
                info.append(f" Punto de montaje: {part.mountpoint}")
                info.append(f" Espacio: {self.format_size(usage.used)} / {self.format_size(usage.total)}")
                info.append(f" Uso: {usage.percent}%")
            except:
                pass
        return info
        
    def get_cpu_info(self):
        info = cpuinfo.get_cpu_info()
        return [
            f"Procesador: {info['brand_raw']}",
            f"Núcleos: {psutil.cpu_count(logical=False)} físicos / {psutil.cpu_count()} lógicos",
            f"Frecuencia: {psutil.cpu_freq().current:.2f} MHz",
            f"Uso actual: {psutil.cpu_percent()}%"
        ]
        
    def get_ram_info(self):
        mem = psutil.virtual_memory()
        return [
            f"Total: {self.format_size(mem.total)}",
            f"En uso: {self.format_size(mem.used)} ({mem.percent}%)",
            f"Disponible: {self.format_size(mem.available)}"
        ]
        
    def get_network_info(self):
        net = psutil.net_if_addrs()
        info = []
        for interface, addrs in net.items():
            info.append(f"🌍 {interface}")
            for addr in addrs:
                info.append(f" {addr.family.name}: {addr.address}")
        return info
        
    def get_system_info(self):
        return [
            f"Sistema: {platform.system()} {platform.release()}",
            f"Versión: {platform.version()}",
            f"Arquitectura: {platform.machine()}",
            f"Usuario: {os.getlogin()}"
        ]
        
    def update_system_info(self):
        for title, func in [
            ('💽 Disco Duro', self.get_disk_info),
            ('🖥️ Procesador', self.get_cpu_info),
            ('🧠 Memoria RAM', self.get_ram_info),
            ('🌐 Red', self.get_network_info),
            ('⚙️ Sistema', self.get_system_info)
        ]:
            new_info = func()
            for lbl, text in zip(self.system_labels[title], new_info):
                lbl.config(text=text)
        self.master.after(5000, self.update_system_info)
        
    def show_path_details(self, event):
        selected = self.tree.selection()
        if not selected:
            return
            
        filepath = selected[0]
        path_frame = ttk.Frame(self.tree, style='System.TFrame')
        
        # Limpiar información previa
        for child in self.tree.get_children():
            if 'path_info' in self.tree.item(child)['tags']:
                self.tree.delete(child)
        
        # Mostrar ruta jerárquica
        parts = filepath.split('/')[1:]
        parent = ''
        for i, part in enumerate(parts):
            node_path = '/' + '/'.join(parts[:i+1])
            self.tree.insert(
                parent,
                'end',
                iid=f"path_{i}",
                text=f"📁 {part}" if i < len(parts)-1 else f"📄 {part}",
                tags=('path_info',),
                open=True
            )
            parent = f"path_{i}"
        
    def start_search(self):
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Advertencia", "Ingrese un patrón de búsqueda")
            return
        
        self.tree.delete(*self.tree.get_children())
        self.tree_nodes.clear()
        self.stop_search = False
        self.btn_search.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.progress.start()
        
        self.search_thread = threading.Thread(target=self.search_files, args=(pattern,), daemon=True)
        self.search_thread.start()
        self.master.after(100, self.check_thread)
        
    def stop_search_process(self):
        self.stop_search = True
        self.btn_search.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.progress.stop()
        
    def check_thread(self):
        if self.search_thread.is_alive():
            self.master.after(100, self.check_thread)
        else:
            self.progress.stop()
            self.btn_search.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
        
    def search_files(self, pattern):
        try:
            for root, dirs, files in os.walk('/'):
                if self.stop_search:
                    break
                
                if any(root.startswith(excl) for excl in self.excluded_dirs):
                    dirs[:] = []
                    continue
                
                for name in files + dirs:
                    if self.stop_search:
                        break
                    if fnmatch.fnmatch(name, pattern):
                        filepath = os.path.join(root, name)
                        self.add_to_tree(filepath)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
            
    def add_to_tree(self, filepath):
        parent = ''
        path_parts = filepath.split('/')[1:]
        
        for i, part in enumerate(path_parts):
            node_path = '/' + '/'.join(path_parts[:i+1])
            
            if node_path not in self.tree_nodes and os.path.exists(node_path):
                stats = os.stat(node_path)
                file_type = '📁' if os.path.isdir(node_path) else '📄'
                self.tree_nodes[node_path] = self.tree.insert(
                    parent,
                    'end',
                    iid=node_path,
                    text=f" {part}",
                    values=(
                        self.format_size(stats.st_size),
                        file_type,
                        datetime.fromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M')
                    ),
                    tags=('dir' if os.path.isdir(node_path) else 'file')
                )
            parent = node_path
            
        self.master.after(0, self.update_tree_view)
        
    def update_tree_view(self):
        for node in self.tree_nodes.values():
            self.tree.see(node)
            
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()