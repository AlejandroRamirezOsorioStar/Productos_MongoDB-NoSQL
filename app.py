import os
from datetime import datetime, timezone
import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

load_dotenv()


class GreenPowerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("GreenPower — Gestión de Plantas Renovables (MongoDB)")
        self.root.geometry("980x620")
        self.root.minsize(820, 520)

        self.uri = os.getenv("MONGODB_URI", "").strip()
        self.client = None
        self.db = None
        self.plantas = None
        self.produccion = None

        self._construir_interfaz()
        self.conectar_mongodb()

    def _construir_interfaz(self):
        # Barra superior de conexión
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=tk.X)

        self.lbl_estado = ttk.Label(
            top_frame,
            text="Estado: Inicializando...",
            font=("Segoe UI", 10, "bold"),
        )
        self.lbl_estado.pack(side=tk.LEFT)

        ttk.Button(
            top_frame,
            text="Reconectar / Actualizar",
            command=self.conectar_y_refrescar,
        ).pack(side=tk.RIGHT, padx=(5, 0))

        ttk.Button(
            top_frame,
            text="Reporte Energía por Tecnología y Mes",
            command=self.ejecutar_reporte_energia,
        ).pack(side=tk.RIGHT)

        # Contenedor principal dividido en izquierda (formulario/acciones) y derecha (listado/detalle)
        main_frame = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = ttk.LabelFrame(main_frame, text="Datos de la Planta", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(form_frame, text="ID (automático al crear):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.var_id = tk.StringVar()
        self.entry_id = ttk.Entry(form_frame, textvariable=self.var_id, width=28, state="readonly")
        self.entry_id.grid(row=1, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form_frame, text="Nombre *:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.var_nombre = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_nombre, width=28).grid(row=3, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form_frame, text="Tecnología *:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.var_tecnologia = tk.StringVar(value="Solar")
        self.combo_tec = ttk.Combobox(
            form_frame,
            textvariable=self.var_tecnologia,
            values=["Solar", "Eolica", "Hidroelectrica", "Biomasa"],
            width=25,
        )
        self.combo_tec.grid(row=5, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form_frame, text="Capacidad MW (> 0) *:").grid(row=6, column=0, sticky=tk.W, pady=3)
        self.var_capacidad = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_capacidad, width=28).grid(row=7, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form_frame, text="Departamento *:").grid(row=8, column=0, sticky=tk.W, pady=3)
        self.var_depto = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.var_depto, width=28).grid(row=9, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form_frame, text="Estado:").grid(row=10, column=0, sticky=tk.W, pady=3)
        self.var_estado = tk.StringVar(value="Operativa")
        self.combo_estado = ttk.Combobox(
            form_frame,
            textvariable=self.var_estado,
            values=["Operativa", "En mantenimiento", "Inactiva"],
            width=25,
        )
        self.combo_estado.grid(row=11, column=0, sticky=tk.EW, pady=(0, 12))

        # Botones CRUD
        ttk.Button(form_frame, text="Agregar Planta", command=self.agregar_planta).grid(row=12, column=0, sticky=tk.EW, pady=3)
        ttk.Button(form_frame, text="Consultar Seleccionada", command=self.consultar_seleccionada).grid(row=13, column=0, sticky=tk.EW, pady=3)
        ttk.Button(form_frame, text="Guardar Cambios", command=self.actualizar_planta).grid(row=14, column=0, sticky=tk.EW, pady=3)
        ttk.Button(form_frame, text="Eliminar Seleccionada", command=self.eliminar_planta).grid(row=15, column=0, sticky=tk.EW, pady=3)
        ttk.Button(form_frame, text="Limpiar Campos", command=self.limpiar_formulario).grid(row=16, column=0, sticky=tk.EW, pady=(8, 3))

        # Panel derecho: tabla y detalle
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        list_frame = ttk.LabelFrame(right_frame, text="Listado de Plantas", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columnas = ("id", "nombre", "tecnologia", "capacidad", "departamento", "estado")
        self.tree = ttk.Treeview(list_frame, columns=columnas, show="headings", height=12)
        encabezados = {
            "id": ("ID", 95),
            "nombre": ("Nombre", 170),
            "tecnologia": ("Tecnología", 115),
            "capacidad": ("Capacidad (MW)", 105),
            "departamento": ("Departamento", 125),
            "estado": ("Estado", 115),
        }
        for col, (texto, ancho) in encabezados.items():
            self.tree.heading(col, text=texto)
            self.tree.column(col, width=ancho, anchor=tk.W)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_seleccionar_fila)

        detalle_frame = ttk.LabelFrame(right_frame, text="Detalle / Resultado", padding=8)
        detalle_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))

        self.txt_detalle = tk.Text(detalle_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
        self.txt_detalle.pack(fill=tk.BOTH, expand=True)

    def _escribir_detalle(self, texto: str):
        self.txt_detalle.configure(state=tk.NORMAL)
        self.txt_detalle.delete("1.0", tk.END)
        self.txt_detalle.insert(tk.END, texto)
        self.txt_detalle.configure(state=tk.DISABLED)

    def conectar_mongodb(self):
        self.uri = os.getenv("MONGODB_URI", "").strip()
        if not self.uri:
            self.lbl_estado.configure(text="Estado: Sin MONGODB_URI en .env")
            self._escribir_detalle(
                "No se encontró la variable MONGODB_URI.\n"
                "Copia .env.example a .env y configura tu URI de MongoDB Atlas o replica set."
            )
            messagebox.showwarning(
                "Configuración faltante",
                "Falta MONGODB_URI en el archivo .env.\nRevisa .env.example para configurar la conexión.",
            )
            return False

        try:
            if self.client:
                self.client.close()
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client["greenpower"]
            self.plantas = self.db["plantas"]
            self.produccion = self.db["produccion"]
            self.lbl_estado.configure(text="Estado: Conectado a greenpower")
            self.cargar_plantas()
            return True
        except ServerSelectionTimeoutError:
            self.lbl_estado.configure(text="Estado: MongoDB no disponible")
            self._escribir_detalle(
                "No se pudo conectar con MongoDB (tiempo de espera agotado).\n"
                "Verifica tu conexión a internet, la URI en .env, las credenciales y Network Access en Atlas."
            )
            messagebox.showerror(
                "MongoDB no disponible",
                "No fue posible conectar con el servidor de MongoDB.\n"
                "Revisa la URI en .env, tu red y la configuración de MongoDB Atlas.",
            )
            return False
        except PyMongoError as err:
            self.lbl_estado.configure(text="Estado: Error de conexión")
            self._escribir_detalle(f"Error de PyMongo al conectar:\n{err}")
            messagebox.showerror("Error de MongoDB", f"Ocurrió un error al conectar:\n{err}")
            return False

    def conectar_y_refrescar(self):
        if self.conectar_mongodb():
            self.cargar_plantas()

    def cargar_plantas(self):
        if self.plantas is None:
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)

            docs = list(self.plantas.find().sort("_id", 1))
            for doc in docs:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=str(doc.get("_id", "")),
                    values=(
                        doc.get("_id", ""),
                        doc.get("nombre", ""),
                        doc.get("tecnologia", ""),
                        doc.get("capacidad_mw", ""),
                        doc.get("departamento", ""),
                        doc.get("estado", ""),
                    ),
                )
            self._escribir_detalle(f"Plantas cargadas: {len(docs)}")
        except PyMongoError as err:
            messagebox.showerror("Error al consultar", f"No se pudieron cargar las plantas:\n{err}")

    def _on_seleccionar_fila(self, _event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        planta_id = seleccion[0]
        valores = self.tree.item(planta_id, "values")
        if valores:
            self.var_id.set(valores[0])
            self.var_nombre.set(valores[1])
            self.var_tecnologia.set(valores[2])
            self.var_capacidad.set(str(valores[3]))
            self.var_depto.set(valores[4])
            self.var_estado.set(valores[5])

    def _validar_formulario(self):
        nombre = self.var_nombre.get().strip()
        tecnologia = self.var_tecnologia.get().strip()
        depto = self.var_depto.get().strip()
        estado = self.var_estado.get().strip() or "Operativa"
        cap_texto = self.var_capacidad.get().strip().replace(",", ".")

        if not nombre or not tecnologia or not depto:
            messagebox.showwarning("Campos obligatorios", "Nombre, Tecnología y Departamento son obligatorios.")
            return None

        try:
            capacidad = float(cap_texto)
        except ValueError:
            messagebox.showwarning("Capacidad inválida", "La capacidad en MW debe ser un número válido.")
            return None

        if capacidad <= 0:
            messagebox.showwarning("Capacidad inválida", "La capacidad en MW debe ser mayor que cero.")
            return None

        return nombre, tecnologia, capacidad, depto, estado

    def agregar_planta(self):
        if self.plantas is None:
            messagebox.showwarning("Sin conexión", "Conecta primero con MongoDB.")
            return
        datos = self._validar_formulario()
        if not datos:
            return
        nombre, tecnologia, capacidad, depto, estado = datos
        nuevo_id = "APP-" + uuid4().hex[:8].upper()

        documento = {
            "_id": nuevo_id,
            "nombre": nombre,
            "tecnologia": tecnologia,
            "capacidad_mw": capacidad,
            "departamento": depto,
            "municipio": "Por definir",
            "estado": estado,
            "ubicacion": {"latitud": 0.0, "longitud": 0.0},
            "fecha_puesta_marcha": datetime.now(timezone.utc),
            "mantenimientos_realizados": 0,
            "equipos": [],
            "estaciones": [],
        }

        try:
            self.plantas.insert_one(documento)
            self.cargar_plantas()
            self.var_id.set(nuevo_id)
            messagebox.showinfo("Planta registrada", f"Se registró la planta '{nombre}' con ID {nuevo_id}.")
        except PyMongoError as err:
            messagebox.showerror("Error al insertar", f"MongoDB rechazó o no pudo guardar la planta:\n{err}")

    def consultar_seleccionada(self):
        if self.plantas is None:
            messagebox.showwarning("Sin conexión", "Conecta primero con MongoDB.")
            return
        planta_id = self.var_id.get().strip()
        if not planta_id:
            messagebox.showinfo("Consulta", "Selecciona una planta de la lista para consultar su detalle.")
            return
        try:
            doc = self.plantas.find_one({"_id": planta_id})
            if not doc:
                messagebox.showwarning("No encontrada", f"No existe una planta con ID {planta_id}.")
                return
            lineas = [f"{k}: {v}" for k, v in doc.items()]
            self._escribir_detalle("\n".join(lineas))
        except PyMongoError as err:
            messagebox.showerror("Error al consultar", f"No se pudo consultar la planta:\n{err}")

    def actualizar_planta(self):
        if self.plantas is None:
            messagebox.showwarning("Sin conexión", "Conecta primero con MongoDB.")
            return
        planta_id = self.var_id.get().strip()
        if not planta_id:
            messagebox.showwarning("Sin selección", "Selecciona una planta de la lista para modificarla.")
            return
        datos = self._validar_formulario()
        if not datos:
            return
        nombre, tecnologia, capacidad, depto, estado = datos

        try:
            res = self.plantas.update_one(
                {"_id": planta_id},
                {
                    "$set": {
                        "nombre": nombre,
                        "tecnologia": tecnologia,
                        "capacidad_mw": capacidad,
                        "departamento": depto,
                        "estado": estado,
                    }
                },
            )
            if res.matched_count == 0:
                messagebox.showwarning("No encontrada", f"No se encontró la planta {planta_id}.")
                return
            self.cargar_plantas()
            messagebox.showinfo("Actualizada", f"Se actualizó la planta {planta_id}.")
        except PyMongoError as err:
            messagebox.showerror("Error al actualizar", f"No se pudo actualizar la planta:\n{err}")

    def eliminar_planta(self):
        if self.plantas is None:
            messagebox.showwarning("Sin conexión", "Conecta primero con MongoDB.")
            return
        planta_id = self.var_id.get().strip()
        nombre = self.var_nombre.get().strip() or planta_id
        if not planta_id:
            messagebox.showwarning("Sin selección", "Selecciona una planta de la lista para eliminarla.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar la planta '{nombre}' ({planta_id})?",
        )
        if not confirmar:
            return

        try:
            res = self.plantas.delete_one({"_id": planta_id})
            if res.deleted_count == 0:
                messagebox.showwarning("No encontrada", f"No se encontró la planta {planta_id}.")
                return
            self.limpiar_formulario()
            self.cargar_plantas()
            messagebox.showinfo("Eliminada", f"Se eliminó la planta {planta_id}.")
        except PyMongoError as err:
            messagebox.showerror("Error al eliminar", f"No se pudo eliminar la planta:\n{err}")

    def ejecutar_reporte_energia(self):
        if self.produccion is None:
            messagebox.showwarning("Sin conexión", "Conecta primero con MongoDB.")
            return
        pipeline = [
            {
                "$lookup": {
                    "from": "plantas",
                    "localField": "planta_id",
                    "foreignField": "_id",
                    "as": "planta",
                }
            },
            {"$unwind": "$planta"},
            {
                "$group": {
                    "_id": {
                        "tecnologia": "$planta.tecnologia",
                        "mes": {"$dateToString": {"format": "%Y-%m", "date": "$fecha"}},
                    },
                    "energia_total_mwh": {"$sum": "$energia_mwh"},
                    "registros": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "tecnologia": "$_id.tecnologia",
                    "mes": "$_id.mes",
                    "energia_total_mwh": 1,
                    "registros": 1,
                }
            },
            {"$sort": {"mes": -1, "energia_total_mwh": -1}},
        ]
        try:
            resultados = list(self.produccion.aggregate(pipeline))
            if not resultados:
                self._escribir_detalle("El reporte no devolvió registros de producción.")
                return
            lineas = ["REPORTE: Energía generada por tecnología y mes", "-" * 52]
            for fila in resultados:
                lineas.append(
                    f"{fila.get('mes')} | {fila.get('tecnologia')}: "
                    f"{fila.get('energia_total_mwh', 0):,.2f} MWh ({fila.get('registros', 0)} reg.)"
                )
            self._escribir_detalle("\n".join(lineas))
        except PyMongoError as err:
            messagebox.showerror("Error en reporte", f"No se pudo ejecutar el reporte:\n{err}")

    def limpiar_formulario(self):
        self.var_id.set("")
        self.var_nombre.set("")
        self.var_tecnologia.set("Solar")
        self.var_capacidad.set("")
        self.var_depto.set("")
        self.var_estado.set("Operativa")
        self.tree.selection_remove(self.tree.selection())

    def cerrar(self):
        if self.client:
            self.client.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = GreenPowerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()


if __name__ == "__main__":
    main()