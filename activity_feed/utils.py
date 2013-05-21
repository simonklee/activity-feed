import datetime
import os
import pkgutil
import sys
import time

try:
    from IPython.core.debugger import Pdb, BdbQuit_excepthook
except ImportError:
    pass

def s(color='NoColor'):
    BdbQuit_excepthook.excepthook_ori = sys.excepthook
    Pdb(color).set_trace(sys._getframe().f_back)

def timeit(method):
    def wrapper(*args, **kw):
        t = time.time()
        result = method(*args, **kw)
        print '%r (%r, %r) %2.3f sec' % \
              (method.__name__, args, kw, time.time() - t)
        return result
    return wrapper

def safe_unicode(s):
    if isinstance(s, unicode):
        return s

    if not isinstance(s, basestring):
        s = unicode(str(s))

    return s.decode('utf-8')

def safe_bytestr(s):
    try:
        return str(s)
    except UnicodeEncodeError:
        return unicode(s).encode('utf-8')

def datetime_to_timestamp(v):
    "Converts a Python datetime object to a unix timestamp"
    return int(time.mktime(v.timetuple()))

def timestamp_to_utc(v):
    "Converts a unix timestamp to a Python datetime object"
    if not v:
        return None
    try:
        v = int(v)
    except ValueError:
        return None
    return datetime.datetime.utcfromtimestamp(v)

def utcnow():
    '''Returns a UTC datetime.datetime.utcnow object with
    microseconds removed.
    '''
    return datetime.datetime.utcnow().replace(microsecond=0)

def isiterable(v):
    '''check if v is iterable, but not a string'''
    return not isinstance(v, basestring) and getattr(v, '__iter__', False)

# Copyright (c) 2013 by Armin Ronacher and contributors.
#
# Some rights reserved.
#
# Redistribution and use in source and binary forms of the software as well
# as documentation, with or without modification, are permitted provided
# that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above
#   copyright notice, this list of conditions and the following
#   disclaimer in the documentation and/or other materials provided
#   with the distribution.
#
# * The names of the contributors may not be used to endorse or
#   promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE AND DOCUMENTATION IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE AND DOCUMENTATION, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

class ImportStringError(ImportError):
    """Provides information about a failed :func:`import_string` attempt."""

    #: String in dotted notation that failed to be imported.
    import_name = None
    #: Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception

        msg = (
            'import_string() failed for %r. Possible reasons are:\n\n'
            '- missing __init__.py in a package;\n'
            '- package or module path not included in sys.path;\n'
            '- duplicated package or module name taking precedence in '
            'sys.path;\n'
            '- missing module, class, function or variable;\n\n'
            'Debugged import:\n\n%s\n\n'
            'Original exception:\n\n%s: %s')

        name = ''
        tracked = []
        for part in import_name.replace(':', '.').split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, getattr(imported, '__file__', None)))
            else:
                track = ['- %r found in %r.' % (n, i) for n, i in tracked]
                track.append('- %r not found.' % name)
                msg = msg % (import_name, '\n'.join(track),
                             exception.__class__.__name__, str(exception))
                break

        ImportError.__init__(self, msg)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.import_name,
                                 self.exception)

def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    if isinstance(import_name, unicode):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        try:
            return getattr(__import__(module, None, None, [obj]), obj)
        except (ImportError, AttributeError):
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            modname = module + '.' + obj
            __import__(modname)
            return sys.modules[modname]
    except ImportError, e:
        if not silent:
            raise ImportStringError(import_name, e), None, sys.exc_info()[2]

def get_root_path(import_name):
    """Returns the path to a package or cwd if that cannot be found.  This
    returns the path of a package or the folder that contains a module.

    Not to be confused with the package path returned by :func:`find_package`.
    """
    # Module already imported and has a file attribute.  Use that first.
    mod = sys.modules.get(import_name)
    if mod is not None and hasattr(mod, '__file__'):
        return os.path.dirname(os.path.abspath(mod.__file__))

    # Next attempt: check the loader.
    loader = pkgutil.get_loader(import_name)

    # Loader does not exist or we're referring to an unloaded main module
    # or a main module without path (interactive sessions), go with the
    # current working directory.
    if loader is None or import_name == '__main__':
        return os.getcwd()

    # For .egg, zipimporter does not have get_filename until Python 2.7.
    # Some other loaders might exhibit the same behavior.
    if hasattr(loader, 'get_filename'):
        filepath = loader.get_filename(import_name)
    else:
        # Fall back to imports.
        __import__(import_name)
        filepath = sys.modules[import_name].__file__

    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))

# sentinel
_missing = object()

class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.

    .. versionchanged:: 0.6
       the `writeable` attribute and parameter was deprecated.  If a
       cached property is writeable or not has to be documented now.
       For performance reasons the implementation does not honor the
       writeable setting and will always make the property writeable.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None, writeable=False):
        if writeable:
            from warnings import warn
            warn(DeprecationWarning('the writeable argument to the '
                                    'cached property is a noop since 0.6 '
                                    'because the property is writeable '
                                    'by default for performance reasons'))

        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

