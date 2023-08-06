from rs4.termcolor import tc
import os, sys
from importlib import reload
import time
from types import ModuleType, FunctionType
import copy
import inspect

class Services:
    def __init__ (self):
        self.mount_p = "/"
        self.path_suffix_len = 0
        self.service_roots = []
        self.mount_params = {}
        self.reloadables = {}
        self.reloadable_objects = {}
        self.last_reloaded = time.time ()
        self._mount_order = []
        self._mount_funcs = []
        self._package_dirs = set ()
        self._mount_option = {}
        self._current_mount_options = []
        self._mounted_funcs = []

    PACKAGE_DIRS = ["services", "exports"]
    def set_mount_point (self, mount):
        if not mount or mount == '/':
            self.mount_p = "/"
        elif mount [-1] != "/":
            self.mount_p = mount + "/"
        else:
            self.mount_p = mount
        self.path_suffix_len = len (self.mount_p) - 1

    def add_package (self, *names):
        for name in names:
            self.PACKAGE_DIRS.append (name)

    MOUNT_HOOKS = ["__mount__", "mount"]
    UMOUNT_HOOKS = ["__umount__", "umount", "dettach"]
    def _mount (self, module):
        mount_func = None
        for hook in self.MOUNT_HOOKS:
            if hasattr (module, hook):
                mount_func = getattr (module, hook)
                break

        if mount_func:
            if not self.auto_mount and module not in self.mount_params:
                return
            params = copy.deepcopy (self.mount_params.get (module, {}))
            if params.get ("debug_only") and not self.debug:
                return
            params ["module_name"] = module.__name__
            if self.enable_namespace and "ns" not in params:
                if module.__name__ not in self.PACKAGE_DIRS:
                    try:
                        _, ns = module.__name__.split (".", 1)
                        if _ not in self.PACKAGE_DIRS:
                            ns = module.__name__
                    except ValueError:
                        ns = module.__name__
                    params ["ns"] = ns

            setattr (module, "__mntopt__", params)
            # for app initialzing and reloading
            self._mount_option = params

            fspec = inspect.getfullargspec (mount_func)
            try:
                if len (fspec.args) == 1:
                    mount_func (self)
                else:
                    mount_func (self, params)

                if 'point' in params:
                    self.log ("- {} mounted to {}".format (module.__name__, tc.white (self.mount_p [:-1] + params ['point'])), "info")
                else:
                    self.log ("- {} mounted".format (module.__name__), "info")

                if hasattr (module, "__mounted__"):
                    self._mounted_funcs.append ((getattr (module, "__mounted__"), params))

            finally:
                self._mount_option = {}

        try:
            self.reloadables [module] = self.get_file_info (module)
        except FileNotFoundError:
            del self.reloadables [module]
            return

        # find recursively
        self.find_mountables (module)

    def _reload_objects (self, origin):
        if origin not in self.reloadable_objects:
            return

        deletables = []
        for objname, includers in self.reloadable_objects [origin].items ():
            for each in includers:
                try:
                    attr = getattr (origin, objname)
                except AttributeError:
                    deletables.append (objname)
                    continue
                setattr (each, objname, attr)

        for objname in deletables:
            try:
                del self.reloadable_objects [origin][objname]
            except KeyError:
                pass

    def _set_reloadable_object (self, objname, origin, includer):
        if origin not in self.reloadable_objects:
            self.reloadable_objects [origin] = {}
        if objname not in self.reloadable_objects [origin]:
            self.reloadable_objects [origin][objname] = set ()
        self.reloadable_objects [origin][objname].add (includer)

    def get_modpath (self, module):
        try:
            modpath = module.__spec__.origin
        except AttributeError:
            try:
                modpath = module.__file__
            except AttributeError:
                return
        return modpath

    def find_mountables (self, module):
        for attr in dir (module):
            if attr.startswith ("__"):
                continue
            v = getattr (module, attr)
            maybe_object = None
            mountable = False

            if hasattr (v, "__module__"):
                maybe_object = attr
                try:
                    v = sys.modules [v.__module__]
                    if v == module:
                        continue
                except KeyError:
                    continue

            if type (v) is not ModuleType:
                continue

            modpath = self.get_modpath (v)
            if not modpath:
                continue

            maybe_object and self._set_reloadable_object (maybe_object, v, module)
            if v in self.reloadables:
                continue

            if v in self.reloadables:
                continue

            for package_dir in self._package_dirs:
                if modpath.startswith (package_dir):
                    mountable = True
                    break

            if mountable:
                self._mount (v)

    def add_package_dir (self, path):
        # DEPRECATED. for mounting external package or module, use app.extends ()
        for exist in self._package_dirs:
            if exist.startswith (path) and len (path) > len (exist):
                return
        self._package_dirs.add (path)

    def mount_explicit (self):
        try:
            for module in self._mount_order:
                if module in self.reloadables:
                    continue
                self._mount (module)
        except RuntimeError:
            raise RuntimeError ('cannot call app.mount () in __mount__ () hook. move to __setup__ () hook')

    def have_mounted (self):
        # _mount () collects mounted_funcs
        for mounted, params in self._mounted_funcs:
            mounted (self, params)
        self._mounted_funcs = []

    def mount_funcs (self):
        for mount_func, params in self._mount_funcs:
            fspec = inspect.getfullargspec (mount_func)
            if len (fspec.args) == 1:
                mount_func (self)
            else:
                mount_func (self, params)
            if 'point' in params:
                self.log ("- {} mounted to {}".format (mount_func.__name__, tc.white (self.mount_p [:-1] + params ['point'])), "info")
            else:
                self.log ("- {} mounted".format (mount_func.__name__), "info")

    def mount_nested (self):
        # within __mount__
        for module in list (sys.modules.values ()):
            if module in self.reloadables:
                continue
            modpath = self.get_modpath (module)
            if not modpath:
                continue
            for package_dir in self._package_dirs:
                if modpath.startswith (package_dir):
                    self._mount (module)
                    break

    def remount (self, module):
        self.setup (module)
        self._mount (module)
        self.have_mounted ()

    def setup (self, module):
        options = copy.deepcopy (self.mount_params.get (module, {}))
        try:
            setup_func = getattr (module, '__setup__')
        except AttributeError:
            return
        fspec = inspect.getfullargspec (setup_func)
        if len (fspec.args) == 1:
            setup_func (self)
        else:
            setup_func (self, options)
        return setup_func

    def mount (self, maybe_point = None, *modules, **kargs):
        self.auto_mount = False # set to explicit mount mode
        if maybe_point or maybe_point == '':
            if isinstance (maybe_point, str):
                assert maybe_point == "" or maybe_point.startswith ("/"), "mount point should be balnk or startswith `/`"
                kargs ["point"] = maybe_point
            else:
                modules = (maybe_point,) + modules

        if self._current_mount_options:
            inherited_options = copy.deepcopy (self._current_mount_options [-1])
            # called in __setup__ hook, make sure sub path mount
            kargs ['point'] = inherited_options ['point'] + kargs ['point']
            if kargs ['point'].endswith ('//'):
                kargs ['point'] = kargs ['point'][:-1]
            if kargs ['point'].startswith ('//'):
                kargs ['point'] = kargs ['point'][1:]
            inherited_options.update (kargs)

        else:
            inherited_options = kargs

        self._current_mount_options.append (inherited_options)
        try:
            for module in modules:
                if isinstance (module, FunctionType):
                    self._mount_funcs.append ((module, inherited_options))
                    continue

                self.mount_params [module] = (inherited_options)
                setup_func = self.setup (module)
                mount_func = None
                for hook in self.MOUNT_HOOKS:
                    if hasattr (module, hook):
                        mount_func = getattr (module, hook)
                        break

                if not setup_func:
                    assert mount_func, "__mount__ hook doesn't exist"

                if mount_func:
                    self.add_package_dir (os.path.dirname (self.get_modpath (module)))
                    if module not in self.mount_params:
                        self._mount_order.append (module)

        finally:
            self._current_mount_options.pop (-1)

    mount_with = decorate_with = mount

    def umount (self, *modules):
        _umounted_funcs = []
        for module in modules:
            umount_func = None
            for hook in self.UMOUNT_HOOKS:
                if hasattr (module, hook):
                    umount_func = getattr (module, hook)
                    break
            if not umount_func:
                return
            umount_func (self)
            if hasattr (module, "__umounted__"):
                _umounted_funcs.append (getattr (module, "__umounted__"))
            self.log ("- %s umount" % module.__name__, "info")

        for umounted in _umounted_funcs:
            umounted (self)

    def umount_all (self):
        self.umount (*tuple (self.reloadables.keys ()))
    dettach_all = umount_all

    def _reload (self):
        reloaded = 0
        for module in list (self.reloadables.keys ()):
            try:
                fi = self.get_file_info (module)
            except FileNotFoundError:
                del self.reloadables [module]
                continue
            if self.reloadables [module] == fi:
                continue

            self.log ("- reloading service, %s" % module.__name__, "info")
            for each in self.service_roots:
                # reinstead package root for path finder
                sys.modules [each.__name__] = each

            if hasattr (module, "__reload__"):
                getattr (module, "__reload__") (self)

            try:
                newmodule = reload (module)
            except:
                self.log ("- reloading failed. see exception log, %s" % module.__name__, "fatal")
                raise

            reloaded += 1
            self._current_function_specs = {}
            self.umount (module)
            del self.reloadables [module]
            self.remount (newmodule)

            self._reload_objects (newmodule)
            if hasattr (newmodule, "__reloaded__"):
                getattr (newmodule, "__reloaded__") (self)

        return reloaded

    def maybe_reload (self):
        with self.lock:
            if self._reloading or time.time () - self.last_reloaded < 1.0:
                return
            self._reloading = True

        try:
            self._reload () and self.load_jinja_filters ()
        finally:
            with self.lock:
                self.last_reloaded = time.time ()
                self._reloading = False
