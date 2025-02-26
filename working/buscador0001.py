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
    
    def add_to_tree(self, filepath):
        parent = ''
        path_parts = filepath.split(os.sep)
        
        # Manejar rutas de Windows
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
        # Usar una copia estática de los nodos
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
        
        start_directory = "C:\\" if platform.system() == "Windows" else "/"
        
        self.search_thread = threading.Thread(
            target=self.search_files, 
            args=(pattern, start_directory),
            daemon=True
        )
        self.search_thread.start()
        self.master.after(100, self.check_thread)
    
    def search_files(self, pattern, start_directory):
        try:
            for root, dirs, files in os.walk(start_directory):
                if self.stop_search:
                    break
                
                # Excluir directorios no deseados
                dirs[:] = [d for d in dirs if not any(
                    os.path.join(root, d).startswith(excl) for excl in self.excluded_dirs
                )]
                
                for name in files + dirs:
                    if self.stop_search:
                        break
                    if fnmatch.fnmatch(name, pattern):
                        filepath = os.path.join(root, name)
                        self.master.after(0, self.add_to_tree, filepath)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
    
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
            try:
                info = cpuinfo.get_cpu_info()
                return [
                    f"Procesador: {info['brand_raw']}",
                    f"Núcleos: {psutil.cpu_count(logical=False)} físicos / {psutil.cpu_count()} lógicos",
                    f"Frecuencia: {psutil.cpu_freq().current:.2f} MHz",
                    f"Uso actual: {psutil.cpu_percent()}%"
                ]
            except Exception:
                return ["Información de CPU no disponible"]
        return ["Instalar py-cpuinfo para más detalles"]
    
    def update_system_info(self):
        self.master.after(5000, self.update_system_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()