import glob, importlib, os


def matches_patterns(test_string, include_patterns):
    for i in include_patterns:
        if glob.fnmatch.fnmatch(test_string, i):
            return True

    return False


def get_loader_files(src):
    cwd = os.getcwd()
    py_files = []
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith("_loader.py"):
                py_files.append(os.path.join(cwd, root, file))
    return py_files


def dynamic_import(module_name, py_path):
    module_spec = importlib.util.spec_from_file_location(module_name, py_path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


def dynamic_import_from_src(src, star_import=False):
    loader_files = get_loader_files(src)
    imported_modules = []
    for py_file in loader_files:
        module_name = os.path.split(py_file)[-1].strip(".py")
        imported_module = dynamic_import(module_name, py_file)
        imported_modules.append(imported_module)
        if star_import:
            for obj in dir(imported_module):
                globals()[obj] = imported_module.__dict__[obj]
        else:
            globals()[module_name] = imported_module
    return imported_modules
