import importlib
import os

import codefast as cf
from flask import Blueprint


class Const(object):
    blueprints = {}


def get_blueprint(module_name):
    if module_name not in Const.blueprints:
        bp = Blueprint(module_name, module_name)
        Const.blueprints[module_name] = bp
    return Const.blueprints[module_name]


def register_blueprints(app, contr_path='controllers', bp_attr='bp'):
    contr_path_abs = '/'.join([app.root_path, contr_path])
    possible_modules = find_possible_modules(contr_path_abs)

    for pm in possible_modules:
        module_name = '.'.join([contr_path, pm])
        # module = importlib.import_module(module_name)
        url_prefix = '/{}'.format(pm.replace('.', '/'))
        bp = get_blueprint(module_name)
        app.register_blueprint(bp, url_prefix=url_prefix)
        importlib.import_module(module_name)


def find_possible_modules(path, father_module=""):
    """Find all possible modules recursively.

    Rule: 1. path must contain a file named "__init__.py"
          2. module must be in a .py file
    Return: ['demo.hello', 'demo.hey.hello', 'demo.bye']
    """
    all_modules = []

    if has_init_file(path):
        fnames = os.listdir(path)
        for fname in fnames:
            fname_abs = '/'.join([path, fname])
            if os.path.isfile(fname_abs):
                if os.path.splitext(
                        fname)[-1] == ".py" and fname != "__init__.py":
                    if father_module != "":
                        module = '.'.join(
                            [father_module,
                             os.path.splitext(fname)[0]])
                    else:
                        module = os.path.splitext(fname)[0]
                    all_modules.append(module)
            else:
                if father_module != "":
                    module = '.'.join([father_module, fname])
                else:
                    module = fname
                son_modules = find_possible_modules(fname_abs, module)
                all_modules += son_modules
    else:
        cf.info("ignore a path without __init__.py: {}".format(path))

    return all_modules


def has_init_file(path):
    has_init_file = False

    fnames = os.listdir(path)
    for fname in fnames:
        if fname == "__init__.py":
            has_init_file = True

    return has_init_file
