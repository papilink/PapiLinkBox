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
        master.title("Explorador de Archivos")
        master.geometry("1200x800")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.search_pattern = tk.StringVar()
        self.stop_search = False
        self.search_thread = None
        self.tree_nodes = {}
        
        self.create_widgets()
        self.configure_exclusions()
    
    def configure_styles(self):
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4CAF50', foreground='white')
        self.style.map('TButton', background=[('active', '#45a049')])
        self.style.configure('Treeview', rowheight=25)
    
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
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = ttk.Button(search_frame, text="Buscar", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Árbol de resultados
        self.tree = ttk.Treeview(main_frame, columns=('size', 'modified'), show='headings')
        self.tree.heading('#0', text='Nombre')
        self.tree.heading('size', text='Tamaño')
        self.tree.heading('modified', text='Modificación')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Barra de estado
        self.status = ttk.Label(main_frame, text="Listo")
        self.status.pack(fill=tk.X)
    
    def start_search(self):
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Error", "Ingrese un patrón de búsqueda")
            return
        
        self.tree.delete(*self.tree.get_children())
        self.stop_search = False
        self.btn_search.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status.config(text="Buscando...")
        
        start_dir = "C:\\" if platform.system() == "Windows" else "/"
        
        self.search_thread = threading.Thread(
            target=self.search_files,
            args=(pattern, start_dir),
            daemon=True
        )
        self.search_thread.start()
        self.check_thread()
    
    def search_files(self, pattern, start_dir):
        try:
            for root, dirs, files in os.walk(start_dir):
                if self.stop_search:
                    break
                
                # Filtrar directorios excluidos
                dirs[:] = [d for d in dirs if not any(
                    os.path.join(root, d).startswith(excl) for excl in self.excluded_dirs
                )]
                
                for name in files + dirs:
                    if self.stop_search:
                        break
                    if fnmatch.fnmatch(name, pattern):
                        filepath = os.path.join(root, name)
                        self.add_to_tree(filepath)
            
            self.master.after(0, lambda: self.status.config(text="Búsqueda completada"))
        
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
    
    def add_to_tree(self, filepath):
        try:
            stats = os.stat(filepath)
            size = self.format_size(stats.st_size)
            modified = datetime.fromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M')
            name = os.path.basename(filepath)
            
            self.tree.insert('', 'end', text=name, values=(size, modified))
        
        except Exception as e:
            pass
    
    def stop_search_process(self):
        self.stop_search = True
        self.btn_search.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.status.config(text="Búsqueda detenida")
    
    def check_thread(self):
        if self.search_thread.is_alive():
            self.master.after(100, self.check_thread)
        else:
            self.btn_search.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
    
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