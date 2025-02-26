import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import psutil
import platform

try:
    import cpuinfo
    CPU_INFO_AVAILABLE = True
except ImportError:
    CPU_INFO_AVAILABLE = False

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
        self.excluded_dirs = ['/proc', '/sys', '/dev', '/run', '/tmp'] if platform.system() == "Linux" else []
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Buscar archivos:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = ttk.Button(search_frame, text="🔍 Iniciar búsqueda", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="⏹ Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        self.tree = ttk.Treeview(main_frame, columns=('size', 'type', 'modified'), selectmode='browse')
        self.tree.heading('#0', text='Estructura de archivos', anchor=tk.W)
        self.tree.heading('size', text='Tamaño')
        self.tree.heading('type', text='Tipo')
        self.tree.heading('modified', text='Modificación')
        
        self.tree.pack(fill=tk.BOTH, expand=True)
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
            f"Usuario: {user}"
        ]
    
    def get_cpu_info(self):
        if CPU_INFO_AVAILABLE:
            info = cpuinfo.get_cpu_info()
            return [
                f"Procesador: {info['brand_raw']}",
                f"Núcleos: {psutil.cpu_count(logical=False)} físicos / {psutil.cpu_count()} lógicos",
                f"Frecuencia: {psutil.cpu_freq().current:.2f} MHz",
                f"Uso actual: {psutil.cpu_percent()}%"
            ]
        return ["Información de CPU no disponible"]
    
    def update_system_info(self):
        print("\n".join(self.get_system_info()))
        self.master.after(5000, self.update_system_info)
    
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
        
        start_directory = "C:/" if platform.system() == "Windows" else "/"
        
        self.search_thread = threading.Thread(target=self.search_files, args=(pattern, start_directory), daemon=True)
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
    
    def search_files(self, pattern, start_directory):
        try:
            for root, dirs, files in os.walk(start_directory):
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
                        print(f"Encontrado: {filepath}")
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
    
if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()
