import os
import json
import argparse
import sys
import time
import re
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

DB_FILE = 'file_index.json'
EXCLUDED_PATHS = {
    '/proc', '/sys', '/dev', '/run', '/tmp', '/var/run', '/var/tmp', '/mnt', '/media', '/snap'
}

def is_root():
    return os.geteuid() == 0

def is_excluded(path):
    return any(path.startswith(excluded) for excluded in EXCLUDED_PATHS)

def scan_dir(dirpath):
    result = []
    try:
        for entry in os.scandir(dirpath):
            full_path = os.path.join(dirpath, entry.name)
            if entry.is_file(follow_symlinks=False):
                try:
                    mtime = os.path.getmtime(full_path)
                    result.append((full_path, mtime))
                except Exception:
                    pass
            elif entry.is_dir(follow_symlinks=False) and not is_excluded(full_path):
                result.append((full_path + '/', None))
    except Exception:
        pass
    return result

def parallel_walk(start_dir='/', use_threads=False, existing_index=None):
    to_scan = [start_dir]
    updated_index = existing_index.copy() if existing_index else {}

    if use_threads:
        print(Fore.CYAN + "🚀 Usando ThreadPoolExecutor (modo threading)")
        executor = ThreadPoolExecutor(max_workers=8)
        map_func = executor.map
    else:
        print(Fore.CYAN + f"🚀 Usando multiprocessing con {cpu_count()} núcleos")
        pool = Pool(cpu_count())
        map_func = pool.map

    try:
        while to_scan:
            results = map_func(scan_dir, to_scan)
            to_scan = []
            for result in results:
                for path, mtime in result:
                    if path.endswith('/'):
                        to_scan.append(path.rstrip('/'))
                    elif mtime is not None:
                        if path not in updated_index or updated_index[path] != mtime:
                            updated_index[path] = mtime
    finally:
        if use_threads:
            executor.shutdown()
        else:
            pool.close()
            pool.join()

    # Eliminar archivos eliminados
    paths_to_remove = [p for p in updated_index if not os.path.exists(p)]
    for p in paths_to_remove:
        del updated_index[p]

    return updated_index

def save_database(index):
    with open(DB_FILE, 'w') as f:
        json.dump(index, f)
    try:
        os.chmod(DB_FILE, 0o666)
    except Exception as e:
        print(Fore.YELLOW + f"⚠️ No se pudo cambiar permisos: {e}")

def load_database():
    if not os.path.exists(DB_FILE):
        print(Fore.RED + "⚠️ No se encontró la base de datos. Ejecuta con --update primero.")
        sys.exit(1)
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
        if isinstance(data, list):
            print(Fore.YELLOW + "⚠️ Base de datos antigua detectada. Se descartará y se reindexará desde cero.")
            return {}
        return data

def parse_size(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    size_str = size_str.upper().strip()
    for unit in units:
        if size_str.endswith(unit):
            return int(float(size_str[:-len(unit)].strip()) * units[unit])
    return int(size_str)

def search(query, index, min_size=None, max_size=None, modified_within=None):
    results = []

    is_regex = False
    if query.startswith('regex:'):
        pattern = query[6:].strip()
        is_regex = True
    elif query.startswith('r"') and query.endswith('"'):
        pattern = query[2:-1]
        is_regex = True
    else:
        pattern = query.lower()

    now = time.time()

    for path, mtime in index.items():
        filename = os.path.basename(path)
        if is_regex:
            try:
                if not re.search(pattern, filename):
                    continue
            except re.error:
                continue
        else:
            if pattern not in filename.lower():
                continue

        try:
            size = os.path.getsize(path)
        except Exception:
            continue

        if min_size and size < min_size:
            continue
        if max_size and size > max_size:
            continue
        if modified_within and mtime < now - (modified_within * 86400):
            continue

        results.append((path, size, mtime))

    return results

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} PB"

def format_time(ts):
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def get_total_size(index):
    total = 0
    for path in index:
        try:
            total += os.path.getsize(path)
        except Exception:
            continue
    return total

def main():
    parser = argparse.ArgumentParser(description="🔎 Buscar archivos rápidamente (estilo locate).")
    parser.add_argument('query', nargs='?', help='Nombre o expresión regular del archivo a buscar.')
    parser.add_argument('--update', action='store_true', help='Actualizar la base de datos de archivos.')
    parser.add_argument('--path', default='/', help='Ruta desde donde escanear (por defecto /)')
    parser.add_argument('--min-size', help='Tamaño mínimo (ej: 100MB, 1GB)')
    parser.add_argument('--max-size', help='Tamaño máximo')
    parser.add_argument('--modified-within', type=int, help='Archivos modificados en los últimos X días')
    args = parser.parse_args()

    if args.update:
        if not is_root():
            print(Fore.RED + "🚫 Este comando necesita permisos de administrador.")
            print("👉 Intenta ejecutar: sudo python files.py --update")
            sys.exit(1)

        use_threads = cpu_count() <= 2
        mode = "Threading" if use_threads else "Multiprocessing"

        print(Fore.GREEN + f"🔄 Indexación incremental desde {args.path} usando {mode}...")
        start_time = time.time()

        previous_index = {}
        if os.path.exists(DB_FILE):
            previous_index = load_database()

        updated_index = parallel_walk(args.path, use_threads=use_threads, existing_index=previous_index)
        duration = time.time() - start_time
        total_size = get_total_size(updated_index)

        save_database(updated_index)

        print(Fore.GREEN + f"\n✅ Base de datos actualizada (indexado incremental)")
        print(Fore.BLUE + f"📄 Archivos indexados: {len(updated_index)}")
        print(Fore.BLUE + f"📦 Tamaño total: {format_size(total_size)}")
        print(Fore.BLUE + f"⏱️ Tiempo total: {duration:.2f} segundos")
        print(Fore.BLUE + f"⚙️ Modo: {mode}")

    elif args.query:
        index = load_database()

        min_size = parse_size(args.min_size) if args.min_size else None
        max_size = parse_size(args.max_size) if args.max_size else None
        modified_within = args.modified_within

        results = search(args.query, index, min_size, max_size, modified_within)
        if results:
            print(Fore.GREEN + f"🔍 Se encontraron {len(results)} coincidencias:\n")
            for path, size, mtime in results:
                print(f"{Fore.YELLOW}{path}")
                print(f"{Fore.CYAN}   ↳ Tamaño: {format_size(size)} | Modificado: {format_time(mtime)}\n")
        else:
            print(Fore.RED + "❌ No se encontraron coincidencias.")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

