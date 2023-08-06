from . import processors, validators
from .utils import list_functions


def get_processor_names():
    return list_functions(processors)


def get_validator_names():
    return list_functions(validators)


def _resolve_function(mod, function_name: str):
    try:
        return getattr(mod, function_name)
    except KeyError:
        raise Exception(f"Couldn't resolve function: {mod} from: {function_name}")


def resolve_validator(name):
    return _resolve_function(validators, name)


def resolve_processor(name):
    return _resolve_function(processors, name)
