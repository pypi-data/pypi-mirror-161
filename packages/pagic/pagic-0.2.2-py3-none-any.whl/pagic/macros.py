from pagic.scanner import scan_modules

MACROS = []


def macro(f):
    MACROS.append(f)
    return f


def register_macros(app, path):
    scan_modules(path)

    for macro in MACROS:
        app.template_global(macro.__name__)(macro)
