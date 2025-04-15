# 🗂️ **File Indexer & Search Tool** 🔎

Una herramienta rápida y eficiente para **indexar archivos** en tu sistema y realizar **búsquedas avanzadas** utilizando parámetros como **tamaño** de archivo, **fecha de modificación** y **expresiones regulares**. Al estilo de `locate`, pero con un índice incremental que puedes mantener actualizado fácilmente.


## 🚀 **Características**

- **🔄 Indexación incremental**: Actualiza el índice de archivos del sistema sin necesidad de escanear todo el disco.
- **📝 Búsqueda avanzada**: Encuentra archivos por nombre, tamaño, fecha de modificación y más.
- **⚡ Optimización**: Usa **multiprocessing** o **threading** para acelerar el proceso según los recursos del sistema.
- **📂 Excluye rutas del sistema**: Evita indexar directorios como `/proc`, `/sys`, y otros directorios de sistema.
- **📦 Control total sobre el tamaño de los archivos**: Filtra resultados por tamaño mínimo o máximo.
- **📅 Filtra por fecha de modificación**: Busca archivos modificados dentro de un rango de días.


## 🔧 **Requisitos**

- Python 3.x
- Paquete `colorama` para color en la terminal.


## 📦 **Instalación**

1. Clona este repositorio:

   ```bash
   git clone https://github.com/Santitub/fastlocate.git
   cd fastlocate
   ```

2. (Opcional) Crea un entorno virtual para evitar conflictos de dependencias:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias necesarias:

   ```bash
   pip install -r requirements.txt
   ```


## 📝 **Uso**

### 1. **Actualizar la base de datos de archivos**

Para crear o actualizar el índice de archivos en el sistema, usa el siguiente comando:

```bash
sudo python3 fastlocate.py --update
```

Este comando necesita privilegios de administrador (`sudo`) para acceder a archivos protegidos del sistema.

### 2. **Buscar archivos**

Puedes buscar archivos por nombre, utilizando un nombre simple o una expresión regular:

```bash
python3 fastlocate.py "documento"           # Busca archivos que contengan "documento" en el nombre
python3 fastlocate.py "regex:^.*\.txt$"     # Busca archivos que terminen con ".txt"
```

#### **Parámetros adicionales**:

- **`--min-size`**: Filtra archivos por tamaño mínimo (ej: `100MB`, `1GB`).
- **`--max-size`**: Filtra archivos por tamaño máximo.
- **`--modified-within`**: Filtra archivos modificados en los últimos X días.

Ejemplo:

```bash
python3 fastlocate.py "imagen" --min-size 10MB --modified-within 30
```

Este comando busca archivos que contengan "imagen" en el nombre, que sean mayores a 10MB y que hayan sido modificados en los últimos 30 días.

---

## ⚙️ **Comandos disponibles**

| Comando                             | Descripción                                                            |
|-------------------------------------|------------------------------------------------------------------------|
| `--update`                          | Actualiza la base de datos de archivos (requiere permisos de root).    |
| `--path <ruta>`                     | Ruta desde donde escanear (por defecto: `/`).                          |
| `--min-size <tamaño>`               | Tamaño mínimo de archivo (ej: `100MB`, `1GB`).                         |
| `--max-size <tamaño>`               | Tamaño máximo de archivo (ej: `500MB`, `2GB`).                         |
| `--modified-within <días>`          | Filtra archivos modificados dentro de los últimos X días.              |
| `<consulta>`                        | Nombre o expresión regular del archivo a buscar.                       |

---

## 📊 **Ejemplo de uso**

### Actualización del índice:

```bash
sudo python3 fastlocate.py --update --path /home/user
```

### Búsqueda de archivos con nombre "report":

```bash
python3 fastlocate.py "report"
```

### Búsqueda de archivos mayores a 100MB, modificados en los últimos 7 días:

```bash
python3 fastlocate.py "documento" --min-size 100MB --modified-within 7
```

## 📜 **Licencia**

Este proyecto está licenciado bajo la **MIT License** - consulta el archivo [LICENSE](LICENSE) para más detalles.
