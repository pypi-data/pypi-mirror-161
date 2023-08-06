from functools import wraps
import os
import time, threading
import re
import inspect
import skitai
import sys
from ..events import *
from rs4.annotations import deprecated
import atila
import asyncio

class Decorators:
    def __init__ (self):
        self.handlers = {}
        self._ws_channels = {}
        self._maintern_funcs = {}
        self._testpasses = {}
        self._depends = {}
        self._decos = {
            "bearer_handler": self.default_bearer_handler
        }
        self._reloading = False
        self._function_specs = {}
        self._function_map = {}
        self._current_function_specs = {}
        self._parameter_caches = {}
        self._conditions = {}
        self._websocket_configs = {}
        self._cond_check_lock = threading.RLock ()
        self._binds_request = [None] * 4

    # function param saver ------------------------------------------
    def _base_func_id (self, func, mount_option = None):
        mount_option = mount_option or self._mount_option
        func_id = ("ns" in mount_option and mount_option ["ns"] + "." or "") + func.__name__
        return func_id, func_id.split (".")

    def _get_services_root (self, parts):
        if len (parts) < 3:
            return 0
        try:
            root = parts.index ("services")
        except ValueError:
            return 0
        mount_hook = '.'.join (parts [:root])
        if root > 0:
            for hook in ('__config__', '__setup__', '__mount__'):
                if hasattr (sys.modules [mount_hook], hook): # extension module
                    return root + 1
        return 0

    def get_func_id (self, func, mount_option = None):
        func_id, parts = self._base_func_id (func, mount_option)
        index = self._get_services_root (parts)
        if index:
            func_id = '.'.join (parts [index:])
        return func_id

    def is_overridable (self, func, mount_option = None):
        func_id, parts = self._base_func_id (func, mount_option)
        if self._get_services_root (parts) >= 2:
            for m, t in self._mro.items ():
                if func_id.startswith (m):
                    return t
        return None

    def save_function_spec (self, func):
        # save original function spec for preventing distortion by decorating wrapper
        # all wrapper has *args and **karg but we want to keep original function spec for auto parametering call
        func_id = self.get_func_id (func)
        if func_id not in self._function_specs or func_id not in self._current_function_specs:
            # save origin spec
            self._function_specs [func_id] = inspect.getfullargspec (func)
            self._current_function_specs [func_id] = None
            self._function_map [func_id] = func
        return func_id

    def get_function_spec (self, func, mount_option = None):
        # called by websocet_handler with mount_option
        func_id = self.get_func_id (func, mount_option)
        return self._function_specs.get (func_id)

    def get_parameter_requirements (self, func_id):
        return self._parameter_caches.get (func_id, {})

    # Request chains ----------------------------------------------
    def before_request (self, f):
        self._binds_request [0] = f
        return f

    def request_success (self, f):
        self._binds_request [1] = f
        return f
    finish_request = request_success

    def request_failed (self, f):
        self._binds_request [2] = f
        return f
    failed_request = request_failed

    def teardown_request (self, f):
        self._binds_request [3] = f
        return f

    # Automation ------------------------------------------------------
    def testpass_required (self, testfunc):
        def decorator(f):
            func_id = self.save_function_spec (f)
            self._testpasses [func_id] = testfunc
            self.set_auth_flag (f, ('testpass', testfunc.__name__))
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                testfunc = self._testpasses [func_id]
                response = testfunc (was)
                if response is False:
                    return was.response ("403 Permission Denied")
                elif response is not True and response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator

    def depends (self, on_request = None, on_response = None):
        def decorator(f):
            self.save_function_spec (f)
            if not on_request:
                request = []
            elif not isinstance (on_request, (list, tuple)):
                request = [on_request]
            else:
                request = on_request

            if not on_response:
                response = []
            elif not isinstance (on_response, (list, tuple)):
                response = [on_response]
            else:
                response = on_response

            @wraps(f)
            def wrapper (was, *args, **kwargs):
                nonlocal request, response
                for func in request:
                    r = was.execute_function (func, (was,))
                    if r is not None:
                        return r
                r = f (was, *args, **kwargs)

                if response:
                    if asyncio.iscoroutine (r):
                        was.request._depends = response
                    else:
                        for func in response:
                            r_ = was.execute_function (func, (was, r))
                            if r_ is not None:
                                r = r_
                return r

            return wrapper
        return decorator

    # Conditional Automation ------------------------------------------------------
    def _check_condition (self, was, key, func, interval, mtime_func):
        now = time.time ()
        with self._cond_check_lock:
            oldmtime, last_check = self._conditions [key]

        if not interval or not oldmtime or now - last_check > interval:
            mtime = mtime_func (key)
            if mtime > oldmtime:
                response = func (was, key)
                with self._cond_check_lock:
                    self._conditions [key] = [mtime, now]
                if response is not None:
                    return response

            elif interval:
                with self._cond_check_lock:
                    self._conditions [key][1] = now

    def if_state_updated (self, key, func, interval = 1):
        def decorator(f):
            self.save_function_spec (f)
            self._conditions [key] = [0, 0]
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = self._check_condition (was, key, func, interval, was.getlu)
                if response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
    if_updated = if_state_updated

    def if_file_modified (self, path, func, interval = 1):
        def decorator(f):
            self.save_function_spec (f)
            self._conditions [path] = [0, 0]
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                def _getmtime (path):
                    return os.path.getmtime (path)
                response = self._check_condition (was, path, func, interval, _getmtime)
                if response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator

    # Websocket ------------------------------------------------------
    def websocket (self, spec, timeout = 60, onopen = None, onclose = None, encoding = "text"):
        use_session = False
        if spec & skitai.WS_SESSION == skitai.WS_SESSION:
            use_session = True
            assert not onopen and not onclose, 'WS_SESSION cannot have onopen or onclose handler'

        def decorator(f):
            self._websocket_configs [self.get_func_id (f)] = (spec, timeout)

            self.save_function_spec (f)
            if spec == atila.WS_CHANNEL:
                assert not onopen and not onclose, 'WS_CHANNEL cannot have onopen or onclose handler'
                self.coroutine (f)
                self.input_stream (f)
                return f

            @wraps(f)
            def wrapper (was, *args, **kwargs):
                if not was.wshasevent ():
                    return f (was, *args, **kwargs)
                if was.wsinit ():
                    session = use_session and f (was, *args, **kwargs) or None
                    return was.wsconfig (spec, timeout, encoding, session)
                elif was.wsopened ():
                    return onopen and onopen (was) or ''
                elif was.wsclosed ():
                    return onclose and onclose (was) or ''
            return wrapper
        return decorator
    websocket_config = websocket

    def register_websocket (self, client_id, send):
        self._ws_channels [client_id] = send

    def remove_websocket (self, client_id):
        try: self._ws_channels [client_id]
        except KeyError: pass

    def websocket_send (self, client_id, msg):
        try:
            self._ws_channels [client_id] (msg)
        except KeyError:
            pass

    # Mainterinancing -------------------------------------------------------
    def maintain (self, per_maintaining = 1, threading = False):
        def check_duplicate (f):
            if not self._started:
                assert f.__name__ not in self._maintern_funcs, "maintain func {} is already exists".format (f.__name__)

        if not isinstance (per_maintaining, int):
            f = per_maintaining
            check_duplicate (f)
            self._maintern_funcs [f.__name__] = (f, 1, False)
            return f

        def decorator(f):
            check_duplicate (f)
            self._maintern_funcs [f.__name__] = (f, per_maintaining, threading)
            return f
        return decorator

    # Error handling ------------------------------------------------------
    def add_error_handler (self, errcode, f, **k):
        self.handlers [errcode] = (f, k)

    def error_handler (self, errcode, **k):
        def decorator(f):
            self.add_error_handler (errcode, f, **k)
            @wraps(f)
            def wrapper (*args, **kwargs):
                return f (*args, **kwargs)
            return wrapper
        return decorator

    def default_error_handler (self, f):
        self.add_error_handler (0, f)
        return f
    defaulterrorhandler = default_error_handler
    errorhandler = error_handler
