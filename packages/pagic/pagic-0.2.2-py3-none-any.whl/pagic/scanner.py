from devtools import debug
from werkzeug.utils import find_modules, import_string


def scan_modules(module_path: str, callback=None, recursive=True):
    for name in find_modules(module_path, include_packages=True, recursive=recursive):
        debug(name)
        module = import_string(name)
        if callback:
            callback(module)
