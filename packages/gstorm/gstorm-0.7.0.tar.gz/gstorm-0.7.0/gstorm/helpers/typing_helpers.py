from importlib import import_module
from enum import Enum
from gstorm import BaseGraphQLType


def is_enum(x):
    return Enum in type(x).__mro__


def is_gql_subtype(x):
    return BaseGraphQLType in type(x).__mro__


def enum_cast(x):
    return x.value if is_enum(x) else x


def convert_to(models_path, classname):
    """Returns a casting function to determined type
    Parameters
    ----------
    models_path : str
      String denoting the path to the models directory: "path.to.models"
    classname : str
      Model name (Ej: "Author", "User", etc)
    Returns
    -------
    function
      function to cast to the specified type
    Raises
    ------
    Exception
      When the class was not found in the available models
    """
    models = import_module(models_path)

    def concrete_cast(value):
        if hasattr(models, classname):
            cls = getattr(models, classname)
        else:
            raise Exception(
                f'"{classname}" model not found inside models module ({models_path})')
        '''casts to specified type'''
        if value is None:
            return None
        if type(value) == dict:
            return cls(**value)
        elif type(value) == str or is_enum(value):
            return cls(value)
        elif is_gql_subtype(value):
            return value
        else:
            return value
    return concrete_cast


def list_convert_to(models_path: str, classname: str):
    """Returns a casting function to determined type

    Parameters
    ----------
    models_path : str
      module path where to look for GraphQL models (ej: "tests.models")
    classname : str
      concrete type to convert-to

    Returns
    -------
    function
        function to cast to the specified type
    """
    models = import_module(models_path)

    def concrete_cast(values):
        if hasattr(models, classname):
            cls = getattr(models, classname)
        else:
            raise Exception(
                f'"{classname}" model not found inside models module ({models_path})')
        '''casts list items to specified type'''
        casted_values = []
        for value in values:
            if type(value) == dict:
                casted_values.append(cls(**value))
            elif type(value) == cls:
                init_values = {
                    k: v for k, v in value.__dict__.items() if not k.startswith('_')}
                casted_values.append(cls(**init_values))
        return casted_values
    return concrete_cast


def gql_repr(value):
    if value is None:
        return 'None'
    return f'{type(value).__name__}(...)'


def gql_list_repr(values):
    if values is None:
        return 'None'
    if len(values) == 0:
        return '[]'
    else:
        return f'[{type(values[0]).__name__}({len(values)})]'
