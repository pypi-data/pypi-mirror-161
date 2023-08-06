import os
import platform
import glob
from contextlib import contextmanager

oldcwd = os.getcwd()
base_path = os.path.dirname(os.path.realpath(__file__))

if platform.system() == 'Windows':
    added_dll = None
    curpath = os.environ.get('PATH', '')

    # Check if safe dll addition is provided (None is to avoid
    # throwing an exception in case attribute is not there).
    if getattr(os, 'add_dll_directory', None):
        added_dll = os.add_dll_directory(base_path + '\\lib')
        os.environ['PATH'] = os.path.pathsep.join([base_path + '\\lib', curpath])
    else:
        os.environ['PATH'] = os.path.pathsep.join([
            base_path + '\\lib',
            base_path + '\\..\\..',
            curpath
        ])

    del curpath


def manual():
    """Returns the full path to the PDF reference manual of the Python
    interface.

    Syntax: xpress.manual()

    Note that only the manual of the Python interface (in PDF format)
    is included in the PyPI and conda package downloaded from these
    repositories; the PDF version of all other Xpress-related
    documentation is contained in the Xpress distribution, and on the
    on-line, HTML format documentation is available on the FICO web
    pages.

    The online documentation includes that for the Xpress Optimizer
    and the Nonlinear solvers and can be found at
    https://www.fico.com/fico-xpress-optimization/docs/latest/overview.html
    """
    return os.path.join(base_path, "doc", "python-interface.pdf")


def examples():
    """
    Returns the full path to the directory containint the examples
    that come with the Python interface.

    Syntax: xpress.examples()

    In the modeling_examples/ subdirectory you will find some of the Mosel
    examples translated into their Python counterpart.

    The online documentation includes that for the Xpress Optimizer and
    the Nonlinear solvers and can be found at
    https://www.fico.com/fico-xpress-optimization/docs/latest/overview.html
    """
    return os.path.join(base_path, "examples") + os.sep


def _check_for_xpress_in_lib_path():
    """
    Looks for an Xpress library in the relevant environment variable,
    and prints a warning if one is found.
    """
    if platform.system() == 'Windows':
        env_var_name = 'PATH'
        lib_pattern = 'xprs.dll'
    elif platform.system() == 'Darwin':
        env_var_name = 'DYLD_LIBRARY_PATH'
        lib_pattern = 'libxprs.dylib'
    else:
        env_var_name = 'LD_LIBRARY_PATH'
        lib_pattern = 'libxprs.so*'
    env_var = os.environ.get(env_var_name, '')
    for path in env_var.split(os.path.pathsep):
        print(path)
        if path and not path.startswith(base_path):
            files = glob.glob(path + '/' + lib_pattern)
            if len(files):
                print(('Could not import xpress module. The %s environment variable points ' +
                       'to an Xpress library which may be interfering with the module:\n  %s\n' + 
                       'Please try unsetting this environment variable and restarting Python.\n') % (env_var_name, files[0]))
                return


from . import __version_file__
__version__ = __version_file__.__version__
__version_library__ = __version_file__.__version_library__
del __version_file__


# Try to import the actual library. Once its members/methods are
# imported with "from ... import *" all symbols become those of the
# xpress module.

try:
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    import xpresslib as _xpresslib
except:
    _check_for_xpress_in_lib_path()
    raise
finally:
    os.chdir(oldcwd)
    del oldcwd


# Check that version in xprs.lib is the same as the one saved in
# __version__.py

libver = _xpresslib.getversion()

split_libver = libver.split('.')
split_intver = __version_library__.split('.')

if split_libver[0] != split_intver[0]:
    print('The Xpress Python API version ' + __version_library__ +
            ' found the Xpress libraries version ' + libver +
            '. Those versions are incompatible. If you have a local ' +
            'Xpress installation in addition to the Xpress package in ' +
            'Python, then please make sure that both Xpress ' +
            'installations have the same version number.')
elif __version_library__ != libver:
    print('Warning: The Xpress Python interface\'s version does not ' +
            'match that of the Xpress Optimizer library:\n\n' +
            __version_library__ + '!=' + libver +
            '\n\nWhile the two versions are compatible, you may want '
            'to check your installation')

del split_libver
del split_intver


# Lazily define xpress.controls to avoid acquiring the license on import
def __getattr__(name):
    if name == 'controls':
        global controls
        controls = _xpresslib._getcontrols()
        return controls
    else:
        raise AttributeError("module '%s' has no attribute '%s'" % (__name__, name))


# Eagerly define xpress.controls in Python <3.7, where __getattr__ is not supported
if tuple(map(int, platform.python_version_tuple())) < (3, 7):
    __getattr__('controls')


# Support 'with xp.init()' via a context manager which calls xp.free() on __exit__
def init(lic_path=None):
    @contextmanager
    def _free_on_exit():
        yield
        _xpresslib.free()

    _xpresslib._init(lic_path)
    return _free_on_exit()

init.__doc__ = _xpresslib._init.__doc__


# Close import; delete all temporary variables and modules
if platform.system() == 'Windows':
    if added_dll is not None:
        added_dll.close()
    del added_dll


# Export only public symbols from xpresslib
from xpresslib import *
__all__ = [name for name in dir(_xpresslib) if name[0] != '_']
