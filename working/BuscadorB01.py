import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading

class FileSearchExplorer:
    def __init__(self, master):
        self.master = master
        master.title("Buscador Azul")
        master.geometry("1200x800")
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
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 10))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='black')
        self.style.configure('Treeview.Heading', background='#2c3e50', foreground='white', font=('Arial', 10, 'bold'))
        
    def configure_exclusions(self):
        self.excluded_dirs = ['/proc', '/sys', '/dev', '/run', '/tmp']
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Patrón de búsqueda:", style='TLabel').pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=40)
        self.entry.pack(side=tk.LEFT, padx=5)
        
        self.btn_search = ttk.Button(search_frame, text="Buscar", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
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
        self.details_text = tk.Text(details_frame, wrap=tk.NONE, font=('Arial', 10), bg='#ecf0f1')
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
        self.stop_search = False
        self.btn_search.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        
        self.search_thread = threading.Thread(target=self.search_files, args=(pattern,), daemon=True)
        self.search_thread.start()
        self.master.after(100, self.check_thread)
        
    def stop_search_process(self):
        self.stop_search = True
        self.btn_search.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        
    def check_thread(self):
        if self.search_thread.is_alive():
            self.master.after(100, self.check_thread)
        else:
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
        path_parts = filepath.split('/')[1:]  # Ignorar el primer slash vacío
        
        for i, part in enumerate(path_parts):
            node_path = '/' + '/'.join(path_parts[:i+1])
            
            if node_path not in self.tree_nodes and os.path.exists(node_path):
                stats = os.stat(node_path)
                self.tree_nodes[node_path] = self.tree.insert(
                    parent,
                    'end',
                    iid=node_path,
                    text=part,
                    values=(
                        self.format_size(stats.st_size),
                        datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    ),
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