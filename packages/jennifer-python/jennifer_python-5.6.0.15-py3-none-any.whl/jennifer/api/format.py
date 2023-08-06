import inspect


def format_function(func):
    # if im_class exist it is probably unbound method
    name = ''
    if hasattr(func, 'im_class'):
        im_class = func.im_class
        name = '.'.join([
            im_class.__module__,
            im_class.__name__,
            func.__name__,
        ])
    elif hasattr(func, '__qualname__'):
        if func.__name__ == func.__qualname__:  # class name is not defined
            name = '.'.join([func.__module__, func.__name__])
        else:
            name = '.'.join([func.__module__, func.__qualname__])
    else:
        name = '.'.join([func.__module__, func.__name__])

    args = ''
    if hasattr(inspect, 'getfullargspec'):
        args = ','.join(inspect.getfullargspec(func).args)
    elif hasattr(inspect, 'getargspec'):
        args = ','.join(inspect.getargspec(func).args)

    name = '%s(%s)' % (name, args)

    return name
