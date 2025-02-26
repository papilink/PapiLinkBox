import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import pwd
import grp
import threading

class AdvancedFileSearch:
    def __init__(self, master):
        self.master = master
        master.title("Buscador de Archivos Avanzado")
        master.geometry("1400x800")
        master.configure(bg="#2c3e50")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.search_pattern = tk.StringVar()
        self.stop_search = False
        self.search_thread = None
        self.file_data = {}  # Almacenar metadatos de archivos
        
        self.create_widgets()
        self.configure_exclusions()
        
    def configure_styles(self):
        self.style.configure('TFrame', background='#3498db')
        self.style.configure('TLabel', background='#3498db', foreground='white', font=('Arial', 12))
        self.style.configure('TButton', background='#2980b9', foreground='white', font=('Arial', 12))
        self.style.map('TButton', background=[('active', '#1f618d')])
        self.style.configure('TEntry', fieldbackground='white', font=('Arial', 12))
        self.style.configure('Treeview', background='white', fieldbackground='white', foreground='black')
        self.style.configure('Treeview.Heading', background='#2980b9', foreground='white', font=('Arial', 10, 'bold'))
        
    def configure_exclusions(self):
        self.excluded_dirs = [
            '/proc', '/sys', '/dev', '/run', '/snap',
            '/var/lib', '/var/cache', '/tmp', '/lost+found'
        ]
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="Patrón de búsqueda (ej: *.py):").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=50)
        self.entry.pack(side=tk.LEFT, padx=10)
        
        self.btn_search = ttk.Button(search_frame, text="Buscar", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        # Frame principal para resultados
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tabla de resultados a la derecha
        self.results_table = ttk.Treeview(results_frame, columns=('Nombre', 'Modificación', 'Tipo', 'Tamaño'), show='headings')
        self.results_table.heading('Nombre', text='Nombre')
        self.results_table.heading('Modificación', text='Última Modificación')
        self.results_table.heading('Tipo', text='Tipo')
        self.results_table.heading('Tamaño', text='Tamaño')
        
        self.results_table.column('Nombre', width=300)
        self.results_table.column('Modificación', width=200)
        self.results_table.column('Tipo', width=100)
        self.results_table.column('Tamaño', width=100)
        
        # Detalles a la izquierda
        self.details_tree = ttk.Treeview(results_frame, columns=('Propiedad', 'Valor'), show='headings')
        self.details_tree.heading('Propiedad', text='Propiedad')
        self.details_tree.heading('Valor', text='Valor')
        self.details_tree.column('Propiedad', width=200, anchor=tk.W)
        self.details_tree.column('Valor', width=400, anchor=tk.W)
        
        # Configurar scrollbars
        scroll_results = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_table.yview)
        scroll_details = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.details_tree.yview)
        
        self.results_table.configure(yscrollcommand=scroll_results.set)
        self.details_tree.configure(yscrollcommand=scroll_details.set)
        
        # Diseño de la interfaz
        self.details_tree.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        scroll_details.grid(row=0, column=1, sticky='ns')
        self.results_table.grid(row=0, column=2, sticky='nsew', padx=(10, 0))
        scroll_results.grid(row=0, column=3, sticky='ns')
        
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_columnconfigure(2, weight=3)
        
        # Configurar evento de selección
        self.results_table.bind('<<TreeviewSelect>>', self.show_selected_details)
        
        # Estado
        self.status = ttk.Label(main_frame, text="Listo")
        self.status.pack(fill=tk.X)
        
    def start_search(self):
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Advertencia", "Ingresa un patrón de búsqueda")
            return
        
        self.results_table.delete(*self.results_table.get_children())
        self.details_tree.delete(*self.details_tree.get_children())
        self.file_data = {}
        self.stop_search = False
        self.btn_search.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.status.config(text="Buscando...")
        
        self.search_thread = threading.Thread(target=self.search_files, args=(pattern,), daemon=True)
        self.search_thread.start()
        self.master.after(100, self.check_thread)
        
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
            self.status.config(text=f"Búsqueda completada. {len(self.results_table.get_children())} resultados encontrados")
        
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
                        file_info = self.get_file_info(filepath)
                        self.file_data[filepath] = file_info
                        self.master.after(0, self.add_to_results_table, file_info)
                
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
    
    def get_file_info(self, filepath):
        try:
            stat = os.stat(filepath)
            file_type = "Directorio" if os.path.isdir(filepath) else "Archivo"
            if os.path.islink(filepath):
                file_type = "Enlace"
            
            return {
                'path': filepath,
                'name': os.path.basename(filepath),
                'type': file_type,
                'size': self.format_size(stat.st_size),
                'modification': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'permissions': self.format_permissions(stat.st_mode),
                'owner': pwd.getpwuid(stat.st_uid).pw_name,
                'group': grp.getgrgid(stat.st_gid).gr_name,
                'inode': stat.st_ino,
                'creation': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def add_to_results_table(self, file_info):
        if 'error' in file_info:
            return
        
        self.results_table.insert('', tk.END, 
            values=(
                file_info['name'],
                file_info['modification'],
                file_info['type'],
                file_info['size']
            ), 
            iid=file_info['path']
        )
    
    def show_selected_details(self, event):
        self.details_tree.delete(*self.details_tree.get_children())
        selected = self.results_table.selection()
        if not selected:
            return
        
        filepath = selected[0]
        file_info = self.file_data.get(filepath, {})
        
        if 'error' in file_info:
            self.details_tree.insert('', tk.END, values=("Error", file_info['error']))
            return
        
        details = [
            ("Ruta completa", file_info['path']),
            ("Nombre", file_info['name']),
            ("Tipo", file_info['type']),
            ("Tamaño", file_info['size']),
            ("Última modificación", file_info['modification']),
            ("Fecha creación", file_info['creation']),
            ("Permisos", file_info['permissions']),
            ("Propietario", file_info['owner']),
            ("Grupo", file_info['group']),
            ("Inodo", file_info['inode'])
        ]
        
        for prop, val in details:
            self.details_tree.insert('', tk.END, values=(prop, val))
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def format_permissions(self, mode):
        perm = ''
        for i in range(9):
            if mode & (0x100 >> i):
                perm += 'rwx'[i % 3]
            else:
                perm += '-'
            if i in [2, 5]:
                perm += ' '
        return f"{perm} ({oct(mode)[-3:]})"

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFileSearch(root)
    root.mainloop()