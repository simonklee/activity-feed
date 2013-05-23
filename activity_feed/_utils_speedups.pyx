def isiterable(v):
    '''check if v is iterable, but not a string'''
    return not isinstance(v, basestring) and getattr(v, '__iter__', False)
