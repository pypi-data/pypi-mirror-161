from functools import wraps
import os
from importlib import reload
import time, threading
from rs4.attrdict import AttrDictTS, AttrDict
from . import decorators, auth, template_engine, router, events, testutils, services, parameters, deprecated
import skitai
from ..events import *
from skitai.wastuff import preference

class MixIn (
        decorators.Decorators,
        parameters.Parameters,
        router.Router,
        services.Services,
        events.Events,
        auth.Auth,
        template_engine.TemplateEngine,
        testutils.TestUtils,
        preference.PreferenceBase,
        deprecated.Deprecated
    ):

    # core settings --------------------------------
    debug = False
    use_reloader = False
    enable_namespace = True
    auto_mount = True
    expose_spec = False
    restrict_parameter_count = True

    # session and auth -----------------------------
    securekey = None
    session_timeout = None
    access_control_allow_origin = None
    access_control_max_age = 0
    authenticate = None

    # global app objects ----------------------------
    glock = threading.RLock ()

    def __init__ (self):
        decorators.Decorators.__init__ (self)
        router.Router.__init__ (self)
        services.Services.__init__ (self)
        events.Events.__init__ (self)
        auth.Auth.__init__ (self)
        template_engine.TemplateEngine.__init__ (self)

        self.module = None
        self.packagename = None
        self.wasc = None
        self.logger = None

        self.g = self.store = AttrDictTS ()
        self.g ["__last_maintern"] = 0.0
        self.g ["__maintern_count"] = 0

        self.lock = threading.RLock ()

        self.init_time = time.time ()

        self._maintern_funcs = {}
        self._started = False
        self._salt = None
        self._locks = {}

    @property
    def r (self):
        return AttrDict ()

    def get_lock (self, name = None):
        if name is None:
            return self.lock
        with self.lock:
            lock = self._locks.get (name)
            if lock is None:
                lock = self._locks [name] = threading.RLock ()
        return lock

    def maintern (self):
        # called from wsgi_executeor.find_method ()
        if not self._maintern_funcs:
            return

        now = time.time ()
        if (now - self.g ["__last_maintern"]) < self.config.MAINTAIN_INTERVAL:
            return

        was = skitai.was._get ()
        with self.lock:
            for func, interval, threading in self._maintern_funcs.values ():
                count = self.g ["__maintern_count"]
                if count % interval != 0:
                    continue
                if threading:
                    was.Thread (func, args = (was, now, count))
                else:
                    func (was, now, count)
        self.g ["__last_maintern"] = now
        self.g ["__maintern_count"] = count + 1

    def get_resource (self, *args):
        return self.joinpath ("resources", *args)

    def joinpath (self, *args):
        return os.path.normpath (os.path.join (self.home, *args))

    def init (self, module, packagename = "app", mount = "/"):
        self.module = module
        self.packagename = packagename
        self.set_mount_point (mount)

        if self.module:
            self.abspath = self.module.__file__
            if self.abspath [-3:] != ".py":
                self.abspath = self.abspath [:-1]
            self.update_file_info    ()

    def __getitem__ (self, k):
        return self.route_map [k]

    def get_file_info (self, module):
        stat = os.stat (module.__file__)
        return stat.st_mtime, stat.st_size

    def update_file_info (self):
        stat = os.stat (self.abspath)
        self.file_info = (stat.st_mtime, stat.st_size)

    #------------------------------------------------------
    @property
    def salt (self):
        if self._salt:
            return self._salt
        if not self.securekey:
            self._salt = None
        else:
            self._salt = self.securekey.encode ("utf8")
        return self._salt

    def set_default_session_timeout (self, timeout):
        self.session_timeout = timeout

    def set_devel (self, debug = True, use_reloader = True):
        self.debug = debug
        self.use_reloader = use_reloader

    # logger ----------------------------------------------------------
    def set_logger (self, logger):
        self.logger = logger
        self.bus.set_logger (logger)

    def log (self, msg, type = "info"):
        if self.logger is None:
            if type != 'info':
                raise SystemError ('[{}] {}'.format (type, msg))
        self.logger (msg, type)

    def traceback (self):
        self.logger.trace ()
    trace = traceback

    def life_cycle (self, phase, obj):
        obj.app = self
        self.bus.emit (phase, obj)

    # Error handling ------------------------------------------------------
    def render_error (self, error, was = None):
        handler = self.handlers.get (error ['code'], self.handlers.get (0))
        if not handler:
            return
        was = was or skitai.was._get ()
        if not hasattr (was, "response") or was.response is None:
            return
        # reset was.app for rendering
        was.app = self
        content = was.execute_function (handler [0], (was, error))
        was.app = None
        return content


    # app startup and shutdown --------------------------------------------
    def cleanup (self):
        self.umount_all ()
    shutdown = cleanup

    def _start (self, wasc, route, reload = False):
        self.wasc = wasc
        if not route:
            self.basepath = "/"
        elif not route.endswith ("/"):
            self.basepath = route + "/"
        else:
            self.basepath = route

    def start (self, wasc, route):
        self._start (wasc, route)
        self._started = True

    def restart (self, wasc, route):
        self._reloading = True
        self._start (wasc, route, True)
        self._reloading = False

