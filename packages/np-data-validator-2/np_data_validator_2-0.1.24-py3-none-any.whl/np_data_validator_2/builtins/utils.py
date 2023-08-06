import inspect


def is_mod_function(mod, func):
    "checks that func is a function defined in module mod"
    return inspect.isfunction(func) and inspect.getmodule(func) == mod


def list_functions(mod):
    "list of functions defined in module mod"
    return [
        func.__name__ for func in mod.__dict__.values() if is_mod_function(mod, func)
    ]
