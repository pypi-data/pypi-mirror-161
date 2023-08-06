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

class Deprecated:
    # app life cycling -------------------------------------------
    # 2021. 5. 8, integrate into evbus. use app.on ('before_mount') etc
    # 2022. 3. 27 these methods are used only by simple app mount mode
    # 2022. 4. 1 deprecated
    LIFE_CYCLE_HOOKS = [
        EVT_BEFORE_MOUNT,
        EVT_RELOADED,
        EVT_UMOUNTED,
        EVT_MOUNTED,
        EVT_BEFORE_UMOUNT,
        EVT_BEFORE_RELOAD,
        EVT_MOUNTED_RELOADED
    ]
    def _add_hook (self, index, func):
        self.bus.add_event (func, self.LIFE_CYCLE_HOOKS [index])

    @deprecated ("use __setup__ or __mount__ (app, mntopt)")
    def before_mount (self, f):
        self._add_hook (0, f)
        return f
    start_up = before_mount
    startup = before_mount

    @deprecated ("use __mounted__ (app, mntopt)")
    def mounted (self, f):
        self._add_hook (3, f)
        return f

    @deprecated ("removed and no other replacement")
    def mounted_or_reloaded (self, f):
        self._add_hook (6, f)
        return f

    @deprecated ("use __reload__ (app)")
    def before_reload (self, f):
        self._add_hook (5, f)
        return f
    onreload = before_reload
    reload = before_reload

    @deprecated ("use __reloaded__ (app)")
    def reloaded (self, f):
        self._add_hook (1, f)
        return f

    @deprecated ("use __umount__ (app)")
    def before_umount (self, f):
        self._add_hook (4, f)
        return f

    @deprecated ("use __umounted__ (app)")
    def umounted (self, f):
        self._add_hook (2, f)
        return f
    shutdown = umounted

    # Automation ------------------------------------------------------
    @deprecated ("use @app.depends (on_request, on_response)")
    def run_before (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                for func in funcs:
                    response = func (was)
                    if response is not None:
                        return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator

    @deprecated ("use @app.depends (on_request, on_response)")
    def run_after (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = f (was, *args, **kwargs)
                for func in funcs:
                    func (was)
                return response
            return wrapper
        return decorator

    @deprecated ('use permission_required ([MEMBER_TYPE])')
    def staff_member_required (self, f):
        return self.permission_required (['staff']) (f)
