import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import threading

class FileSearchExplorer:
    def __init__(self, master):
        self.master = master
        master.title("Explorador Visual de Archivos")
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
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 10))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 10))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='#2c3e50', rowheight=25)
        self.style.configure('Treeview.Heading', background='#2c3e50', foreground='white', font=('Arial', 10, 'bold'))
        self.style.configure('Details.TFrame', background='#ecf0f1')
        self.style.configure('Details.TLabel', background='#ecf0f1', foreground='#2c3e50', font=('Arial', 10))
        
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
        
        # Panel de detalles
        details_frame = ttk.Frame(paned_window, style='Details.TFrame')
        self.details_panel = ttk.Frame(details_frame)
        self.details_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        paned_window.add(self.tree, weight=1)
        paned_window.add(details_frame, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self.show_details)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
    def create_detail_row(self, parent, title, value):
        frame = ttk.Frame(parent, style='Details.TFrame')
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=title + ":", style='Details.TLabel', width=15, anchor=tk.E).pack(side=tk.LEFT)
        ttk.Label(frame, text=value, style='Details.TLabel', anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True)
        return frame
        
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
            
    def show_details(self, event):
        for widget in self.details_panel.winfo_children():
            widget.destroy()
        
        selected = self.tree.selection()
        if not selected:
            return
        
        filepath = selected[0]
        try:
            stats = os.stat(filepath)
            is_dir = os.path.isdir(filepath)
            is_link = os.path.islink(filepath)
            
            # Sección de información básica
            ttk.Label(self.details_panel, text="Detalles del archivo", style='Details.TLabel', font=('Arial', 12, 'bold')).pack(pady=5, anchor=tk.W)
            self.create_detail_row(self.details_panel, "Nombre", os.path.basename(filepath))
            self.create_detail_row(self.details_panel, "Ruta completa", filepath)
            self.create_detail_row(self.details_panel, "Tipo", "Directorio" if is_dir else "Enlace simbólico" if is_link else "Archivo")
            
            # Separador
            ttk.Separator(self.details_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            
            # Sección de metadatos
            ttk.Label(self.details_panel, text="Metadatos", style='Details.TLabel', font=('Arial', 12, 'bold')).pack(pady=5, anchor=tk.W)
            self.create_detail_row(self.details_panel, "Tamaño", self.format_size(stats.st_size))
            self.create_detail_row(self.details_panel, "Última modificación", datetime.fromtimestamp(stats.st_mtime).strftime('%d/%m/%Y %H:%M:%S'))
            self.create_detail_row(self.details_panel, "Último acceso", datetime.fromtimestamp(stats.st_atime).strftime('%d/%m/%Y %H:%M:%S'))
            self.create_detail_row(self.details_panel, "Permisos", self.format_permissions(stats.st_mode))
            self.create_detail_row(self.details_panel, "Propietario", pwd.getpwuid(stats.st_uid).pw_name)
            self.create_detail_row(self.details_panel, "Grupo", grp.getgrgid(stats.st_gid).gr_name)
            
            if is_link:
                self.create_detail_row(self.details_panel, "Destino enlace", os.readlink(filepath))
            
            # Botón de apertura
            btn_frame = ttk.Frame(self.details_panel, style='Details.TFrame')
            btn_frame.pack(pady=10)
            ttk.Button(btn_frame, text="Abrir ubicación", command=lambda: self.open_location(filepath)).pack(side=tk.LEFT)
            
        except Exception as e:
            ttk.Label(self.details_panel, text=f"Error: {str(e)}", style='Details.TLabel', foreground='red').pack()
            
    def open_location(self, filepath):
        try:
            if os.path.isdir(filepath):
                os.startfile(filepath)
            else:
                os.startfile(os.path.dirname(filepath))
        except AttributeError:
            messagebox.showinfo("Abrir ubicación", f"Ubicación:\n{os.path.dirname(filepath)}")
            
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
        return ''.join(perm) + f" ({oct(mode)[-3:]})"

if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchExplorer(root)
    root.mainloop()