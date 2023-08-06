import importlib
from typing import Optional, Any, List


def model_str(instance, attr) -> str:
    """
    The field to display for an object's __str__. If the field doesn't exist then an
    alternative will be displayed.
    :param instance:    Instance object
    :param attr:        Field name to get data from if it exists
    :return:            str
    """
    return hasattr(instance, attr) and getattr(instance, attr) \
           or f'<{instance.__class__.__name__}: {instance.id}>'


# TESTME: Untested
def modstr(instance, *attr, data: Optional[List[Any]] = None, onlyid: bool = False) -> str:
    """
    The field to display for an object's __str__. If the field doesn't exist then an
    alternative will be displayed.
    :param instance:    Instance object
    :param *attr:       Field/s name to get data from if it exists
    :param data:        Any data not
    :param onlyid:      Only return the id
    :return:            str
    """
    clsname = instance.__class__.__name__
    data = data or []
    ll = [getattr(instance, i) for i in attr if hasattr(instance, i) and getattr(instance, i)]
    ll += [i for i in data if i]
    try:
        if onlyid or not ll:
            return f'<{clsname}: {instance.id}>'
        return f'<{clsname} {instance.id}: {", ".join(ll)}>'
    except AttributeError:
        return f'<{clsname}>'


def classgrabber(dotpath: str):
    """
    Returns the class from a dot path that leads to the class to be imported.
    The class would be ready for use.
    Example:
        Settings = classgrabber('app.folder.file.Settings')
        # Settings class now ready for use
        myobj = Settings()
    :param dotpath:   A dot path
    :return:            class
    """
    x = dotpath.split('.')
    path = '.'.join(x[0:-1])
    models = importlib.import_module(path)
    return getattr(models, x[-1])