import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading

class FileSearchExplorer:
    def __init__(self, master):
        self.master = master
        master.title("Explorador de Búsqueda")
        master.geometry("1200x800")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.search_pattern = tk.StringVar()
        self.stop_search = False
        self.file_data = {}
        self.tree_nodes = {}
        
        self.create_widgets()
        self.configure_exclusions()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', background='#4CAF50', foreground='white', font=('Arial', 10))
        self.style.map('TButton', background=[('active', '#45a049')])
        self.style.configure('Treeview', font=('Arial', 10), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
        
    def configure_exclusions(self):
        self.excluded_dirs = ['/proc', '/sys', '/dev', '/run', '/tmp']
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Buscar", command=self.start_search).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Detener", command=self.stop_search).pack(side=tk.LEFT, padx=5)
        
        # Panel principal
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Árbol de directorios
        self.tree = ttk.Treeview(paned_window, columns=('size', 'modified'), selectmode='browse')
        self.tree.heading('#0', text='Estructura de Archivos', anchor=tk.W)
        self.tree.heading('size', text='Tamaño')
        self.tree.heading('modified', text='Modificación')
        self.tree.column('#0', width=400)
        self.tree.column('size', width=100)
        self.tree.column('modified', width=150)
        
        # Detalles del archivo
        details_frame = ttk.Frame(paned_window)
        self.details_text = tk.Text(details_frame, wrap=tk.NONE, font=('Arial', 10))
        scroll_y = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.details_text.yview)
        scroll_x = ttk.Scrollbar(details_frame, orient=tk.HORIZONTAL, command=self.details_text.xview)
        self.details_text.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.details_text.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        details_frame.grid_rowconfigure(0, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        paned_window.add(self.tree, weight=1)
        paned_window.add(details_frame, weight=2)
        
        self.tree.bind('<<TreeviewSelect>>', self.show_details)
        
    def start_search(self):
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Advertencia", "Ingrese un patrón de búsqueda")
            return
        
        self.tree.delete(*self.tree.get_children())
        self.tree_nodes.clear()
        self.file_data.clear()
        self.stop_search = False
        
        search_thread = threading.Thread(target=self.search_files, args=(pattern,), daemon=True)
        search_thread.start()
        
    def stop_search(self):
        self.stop_search = True
        
    def search_files(self, pattern):
        try:
            for root, dirs, files in os.walk('/'):
                if self.stop_search:
                    break
                
                if any(root.startswith(excl) for excl in self.excluded_dirs):
                    dirs[:] = []
                    continue
                
                for name in files + dirs:
                    if fnmatch.fnmatch(name, pattern):
                        filepath = os.path.join(root, name)
                        self.add_to_tree(filepath)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
            
    def add_to_tree(self, filepath):
        parent = ''
        path_parts = filepath.split('/')[1:]  # Ignorar el primer slash vacío
        
        for i, part in enumerate(path_parts):
            node_path = '/' + '/'.join(path_parts[:i+1])
            
            if node_path not in self.tree_nodes:
                if os.path.exists(node_path):
                    stats = os.stat(node_path)
                    size = self.format_size(stats.st_size)
                    mod_date = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    size = ''
                    mod_date = ''
                
                self.tree_nodes[node_path] = self.tree.insert(
                    parent,
                    'end',
                    iid=node_path,
                    text=part,
                    values=(size, mod_date),
                    tags=('file' if i == len(path_parts)-1 else 'folder')
                )
            parent = node_path
            
        self.master.after(0, self.update_tree_view)
        
    def update_tree_view(self):
        for node in self.tree_nodes.values():
            self.tree.see(node)
            
    def show_details(self, event):
        self.details_text.delete(1.0, tk.END)
        selected = self.tree.selection()
        if not selected:
            return
        
        filepath = selected[0]
        try:
            stats = os.stat(filepath)
            details = [
                f"Ruta completa: {filepath}",
                f"Tamaño: {self.format_size(stats.st_size)}",
                f"Última modificación: {datetime.fromtimestamp(stats.st_mtime)}",
                f"Último acceso: {datetime.fromtimestamp(stats.st_atime)}",
                f"Permisos: {self.format_permissions(stats.st_mode)}",
                f"Tipo: {'Directorio' if os.path.isdir(filepath) else 'Archivo'}"
            ]
            
            if os.path.islink(filepath):
                details.append(f"Enlace a: {os.readlink(filepath)}")
            
            self.details_text.insert(tk.END, '\n'.join(details))
        except Exception as e:
            self.details_text.insert(tk.END, f"Error: {str(e)}")
            
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def format_permissions(self, mode):
        perm = []
        for who in "USR", "GRP", "OTH":
            for what in "R", "W", "X":
                if mode & getattr(os, f"S_I{what}{who}"):
                    perm.append(what)
                else:
                    perm.append("-")
        return ''.join(perm)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()