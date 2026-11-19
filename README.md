# GreenPower — Proyecto Integrador MongoDB

Proyecto académico de base de datos NoSQL con **MongoDB** y **Python (Tkinter + PyMongo)** para gestionar la información de **GreenPower**, una plataforma de generación y distribución de energía renovable.

## ¿Qué contiene cada archivo?

- `1-modelo.md`: modelado de datos en MongoDB, correspondencia con el modelo relacional, decisiones de embebido/referencia, ejemplos de documentos y antipatrones evitados.
- `2-datos.mongodb.js`: creación/selección de la base `greenpower`, limpieza y recreación de colecciones, y carga inicial de datos de demostración (`plantas`, `produccion`, `mantenimientos`, `contratos`, `subestaciones`).
- `3-validacion.mongodb.js`: reglas `$jsonSchema` para `plantas` y `mantenimientos`, junto con pruebas de inserciones inválidas dentro de bloques `try/catch`[cite: 6, 11].
- `4-reportes.mongodb.js`: cinco consultas de agregación (incluyendo energía por tecnología y mes, equipos por tipo y estado, mantenimientos por planta y dos reportes adicionales) usando `$lookup`, `$unwind` y `$group`[cite: 7, 11].
- `5-indices.mongodb.js`: creación de índices compuestos y comparación con `explain("executionStats")` antes y después[cite: 8, 11].
- `6-transaccion.mongodb.js`: demostración de transacción multidocumento con `startSession()`, `startTransaction()`, `commitTransaction()` y `abortTransaction()` (reversión ante fallo y confirmación).
- `app.py`: aplicación de escritorio con interfaz gráfica en **Tkinter** conectada a MongoDB mediante **PyMongo** (listado de plantas, agregar, consultar, actualizar información/estado, eliminar y ejecutar reporte de energía por tecnología y mes)[cite: 10, 11].
- `requirements.txt`: dependencias de Python (`pymongo[srv]` y `python-dotenv`)[cite: 12].
- `.env.example`: plantilla de configuración de `MONGODB_URI` sin credenciales reales.
- `.gitignore`: exclusión de archivos privados y temporales como `.env`, `.venv/`, `venv/`, `__pycache__/`, `*.pyc` y `respaldo/`.
- `README.md`: guía de instalación, configuración, ejecución, seguridad, transacciones y copias de seguridad.

## Requisitos de instalación (Windows 10)

- **Python 3.10+** (con `tkinter` incluido en la instalación estándar de Windows).
- **MongoDB Shell (`mongosh`)** y **MongoDB Database Tools** (`mongodump` / `mongorestore`).
- **MongoDB Atlas** o un **Replica Set** (necesario para ejecutar `6-transaccion.mongodb.js`).
- **MongoDB Compass**, **CMD**, **PowerShell** o **PyCharm** (no se requiere VS Code).

## Cómo instalar dependencias y configurar el proyecto

1. Clona o descarga el repositorio desde GitHub y abre una terminal (**CMD**, **PowerShell** o la terminal de **PyCharm**) dentro de la carpeta del proyecto.
2. Crea y activa un entorno virtual en Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1