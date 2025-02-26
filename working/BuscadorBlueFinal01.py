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
        master.geometry("1200x800")
        master.configure(bg="#2c3e50")
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.search_pattern = tk.StringVar()
        self.stop_search = False
        self.search_thread = None
        
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
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(search_frame, text="Patrón de búsqueda (ej: *.py):").pack(side=tk.LEFT)
        self.entry = ttk.Entry(search_frame, textvariable=self.search_pattern, width=50)
        self.entry.pack(side=tk.LEFT, padx=10)
        
        self.btn_search = ttk.Button(search_frame, text="Buscar", command=self.start_search)
        self.btn_search.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(search_frame, text="Detener", command=self.stop_search_process, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=10)
        
        self.tree = ttk.Treeview(main_frame, columns=('Propiedad', 'Valor'), show='headings')
        self.tree.heading('Propiedad', text='Propiedad')
        self.tree.heading('Valor', text='Valor')
        self.tree.column('Propiedad', width=250, anchor=tk.W)
        self.tree.column('Valor', width=900, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.status = ttk.Label(main_frame, text="Listo")
        self.status.pack(fill=tk.X)
        
    def start_search(self):
        pattern = self.search_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Advertencia", "Ingresa un patrón de búsqueda")
            return
        
        self.tree.delete(*self.tree.get_children())
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
            self.status.config(text=f"Búsqueda completada. {len(self.tree.get_children())} resultados encontrados")
        
    def search_files(self, pattern):
        try:
            for root, dirs, files in os.walk('/'):
                if self.stop_search:
                    break
                
                # Saltar directorios excluidos
                if any(root.startswith(excl) for excl in self.excluded_dirs):
                    dirs[:] = []
                    continue
                
                for name in files + dirs:
                    if fnmatch.fnmatch(name, pattern):
                        filepath = os.path.join(root, name)
                        self.master.after(0, self.show_file_details, filepath)
                
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
        
    def show_file_details(self, filepath):
        try:
            stat = os.stat(filepath)
            file_type = "Directorio" if os.path.isdir(filepath) else "Archivo"
            if os.path.islink(filepath):
                file_type = "Enlace simbólico"
            
            details = {
                'Nombre': os.path.basename(filepath),
                'Ruta completa': filepath,
                'Tipo': file_type,
                'Tamaño': self.format_size(stat.st_size),
                'Última modificación': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'Último acceso': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'Fecha creación': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'Permisos': self.format_permissions(stat.st_mode),
                'Propietario': pwd.getpwuid(stat.st_uid).pw_name,
                'Grupo': grp.getgrgid(stat.st_gid).gr_name,
                'Inodo': stat.st_ino,
                'Dispositivo': f"{os.major(stat.st_dev)}:{os.minor(stat.st_dev)}",
                'Enlaces duros': stat.st_nlink
            }
            
            if os.path.islink(filepath):
                details['Destino enlace'] = os.readlink(filepath)
            
            parent = self.tree.insert('', tk.END, values=(f"ARCHIVO: {filepath}", ""))
            for key, value in details.items():
                self.tree.insert(parent, tk.END, values=(key, value))
                
            self.tree.insert(parent, tk.END, values=("-"*50, "-"*100))
            
        except Exception as e:
            self.tree.insert('', tk.END, values=("Error", f"{filepath} - {str(e)}"))
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
    
    def format_permissions(self, mode):
        perm = ''
        permissions = [
            ('r', 4), ('w', 2), ('x', 1),  # Usuario
            ('r', 4), ('w', 2), ('x', 1),  # Grupo
            ('r', 4), ('w', 2), ('x', 1)   # Otros
        ]
        
        for i in range(9):
            if mode & (0x100 >> i):
                perm += permissions[i][0]
            else:
                perm += '-'
            if i in [2, 5]:
                perm += ' '
        return f"{perm} ({oct(mode)[-3:]})"

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedFileSearch(root)
    root.mainloop()