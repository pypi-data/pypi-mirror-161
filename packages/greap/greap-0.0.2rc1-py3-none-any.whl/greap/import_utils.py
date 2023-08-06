from pathlib import Path
import os
import contextlib
import gc
import importlib
import importlib.util
import glob
from typing import Optional
import sys


def noop(ctx, *args, **kwargs):
    raise NotImplementedError()


@contextlib.contextmanager
def ImportFrom(root_dir: str, fn_name: Optional[str] = None, all: bool = False):
    """
    ImportFrom is a context manager that imports all dependencies
    in the package directory that user provides. It first adds the
    directory to sys.path so that python knows where to find packages.
    It then loads the module from the spec created using importlib.
    Then it iterates over every python file, create spec for each
    module in the file, add module to sys.modules. It then iterates
    all objects in the module and add the object to the
    global scope for access. While iterating over all objects in
    all modules in the directory, it also checks if name of object
    is the same as the function name provided. If it is the same,
    then it will yield this function. If no such function can be
    found, it will yield a noop function which raises `NotImplementedError`.
    At any given point in time, if an error is raised during the process
    of finding and loading modules/objects, a function `raise_exception`
    is created which raise the exception. This `raise_exception` will
    be called as an immortal, and exception will get sent to controller
    as a result. When exiting this context manager, sys.path, sys.modules
    and all global variables will be restored to before.

    :param root_dir: the root directory user provides which stores all
        necessary materials
    :param fn_name: an optional string that returns the function with
        the given name if provided
    :param all: when yield, return all global variables, not just the function
    """

    try:
        root_dir = str(root_dir)
        # append root_dir to source path
        old_sys_path = sys.path[:]
        old_globals = {}
        new_sys_modules = set()

        importlib.invalidate_caches()
        fn = None
        sys.path.append(root_dir)
        for filepath in glob.glob(str(Path(root_dir) / "**" / "*.py"), recursive=True):
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            try:
                importlib.import_module(module_name)
            except ModuleNotFoundError:
                pass
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            old_modules = set(sys.modules.keys())
            spec.loader.exec_module(module)
            sys.modules[module.__name__] = module
            new_sys_modules |= set(sys.modules.keys()) - old_modules
            for n, obj in module.__dict__.items():
                old_globals[n] = globals().get(n, None)

                globals()[n] = obj
                if n == fn_name:
                    fn = obj

        if not all and fn:
            # NOTE: This is needed to solve Python's  _pickle.PicklingError:
            # Can't pickle <class 'x.X'>: it's not the same object as x.X.
            # This seems to happen only when function name is same as filename
            # for file where import is invoked. (e.g. in unit test, analyzer.py).
            importlib.reload(sys.modules[fn.__module__])

        if all:
            yield globals()
        else:
            yield (fn or noop)
    finally:
        assert sys.path != old_sys_path
        for n, m in old_globals.items():
            a = globals().pop(n, None)
            del a
            if m is not None:
                globals()[n] = m
        for n in new_sys_modules:
            del sys.modules[n]
        gc.collect()
        sys.path = old_sys_path
