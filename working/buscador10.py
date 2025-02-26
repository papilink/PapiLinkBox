import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import platform
import sys
import ctypes
import stat

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
    
    def configure_exclusions(self):
        if platform.system() == "Linux":
            self.excluded_dirs = ['/proc', '/sys', '/dev', '/run', '/tmp']
        else:
            self.excluded_dirs = []
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Buscar archivos:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = ttk.Button(search_frame, text="🔍 Iniciar búsqueda", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="⏹ Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Árbol de directorios
        self.tree = ttk.Treeview(main_frame, columns=('size', 'type', 'modified'), selectmode='browse')
        self.tree.heading('#0', text='Estructura de archivos', anchor=tk.W)
        self.tree.heading('size', text='Tamaño')
        self.tree.heading('type', text='Tipo')
        self.tree.heading('modified', text='Modificación')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
    
    def get_system_info(self):
        try:
            user = os.getlogin()
        except Exception:
            user = os.environ.get('USERNAME', 'Desconocido')
            
        return [
            f"Sistema: {platform.system()} {platform.release()}",
            f"Versión: {platform.version()}",
            f"Arquitectura: {platform.machine()}",
            f"Usuario: {user}",
            f"Python: {sys.version.split()[0]}"
        ]
    
    def get_cpu_info(self):
        info = []
        try:
            if platform.system() == "Windows":
                arch = "64-bit" if platform.machine().endswith('64') else "32-bit"
                info.append(f"Procesador: {platform.processor()}")
                info.append(f"Arquitectura: {arch}")
            else:
                with open('/proc/cpuinfo') as f:
                    for line in f:
                        if line.strip() and 'model name' in line:
                            info.append(f"Procesador: {line.split(':')[1].strip()}")
                            break
        except Exception:
            info.append("Información de CPU no disponible")
        
        return info
    
    def get_disk_info(self):
        info = []
        try:
            if platform.system() == "Windows":
                drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
                for drive in drives:
                    free = ctypes.c_ulonglong(0)
                    total = ctypes.c_ulonglong(0)
                    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                        drive,
                        None,
                        ctypes.pointer(total),
                        ctypes.pointer(free)
                    )
                    info.append(f"Disco {drive}: {self.format_size(free.value)} libres de {self.format_size(total.value)}")
            else:
                statvfs = os.statvfs('/')
                total = statvfs.f_frsize * statvfs.f_blocks
                free = statvfs.f_frsize * statvfs.f_bfree
                info.append(f"Disco raíz: {self.format_size(free)} libres de {self.format_size(total)}")
        except Exception:
            info.append("Información de disco no disponible")
        
        return info
    
    def update_system_info(self):
        print("\n=== Información del Sistema ===")
        print("\n".join(self.get_system_info()))
        print("\n=== Información de CPU ===")
        print("\n".join(self.get_cpu_info()))
        print("\n=== Información de Almacenamiento ===")
        print("\n".join(self.get_disk_info()))
        self.master.after(10000, self.update_system_info)
    
    def add_to_tree(self, filepath):
        parent = ''
        path_parts = filepath.split(os.sep)
        
        if platform.system() == "Windows" and len(path_parts) > 0 and ':' in path_parts[0]:
            parent = path_parts[0]
            path_parts = path_parts[1:]
        
        for i, part in enumerate(path_parts):
            if not part:
                continue
            
            node_path = os.path.join(parent, part) if parent else part
            
            if node_path not in self.tree_nodes and os.path.exists(node_path):
                try:
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
                except Exception as e:
                    continue
            parent = node_path
        
        self.master.after(0, self.update_tree_view)
    
    def update_tree_view(self):
        nodes = list(self.tree_nodes.values())
        for node in nodes:
            try:
                self.tree.see(node)
            except tk.TclError:
                pass
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    # Resto de métodos se mantienen igual...

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()