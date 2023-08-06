import os
from . import cookie, session
from .collectors import multipart_collector, stream_collector, grpc_collector, websocket_collector
from .executors import wsgi_executor, xmlrpc_executor, grpc_executor, jsonrpc_executor, ws_executor
from rs4.protocols.sock.impl.grpc import discover
from skitai.wastuff.wsgi_apps import Config
import skitai
import sys
from .app import mixin
from urllib.parse import unquote
from rs4.annotations import deprecated

class Atila (mixin.MixIn):
    ATILA_THE_HUN = True
    PRESERVES_ON_RELOAD = ["reloadables", "service_roots", "subscribers", "mountables"]

    def __init__ (self, name, path = None, **meta):
        mixin.MixIn.__init__ (self)
        self.name = name
        self.path = path
        self.meta = meta
        self.home = None
        # for bus, set by wsgi_executor
        self.config = Config (preset = True)
        self.set_defulat_config ()
        self.config.MINIFY_HTML = False
        self.mountables = [] # == extensions
        self._aliases = []
        self._mro = {}
        self._wasc = None

    def set_wasc (self, wasc):
        self._wasc = wasc
        if hasattr (wasc, "async_executor"):
            self.bus.set_event_loop (wasc.async_executor.loop)

    def proto_was (self):
        return self._wasc ()

    def mount_later (self, *args, **kargs):
        self.mountables.append ((args, kargs))

    def mount (self, maybe_point = None, *modules, **kargs):
        if isinstance (maybe_point, str) and len (modules) == 1 and isinstance (modules [0], str):
            return skitai.mount (maybe_point, modules [0], **kargs)
        else:
            if kargs.get ('extends'):
                self._mro [modules [0].__name__] = 'extends'
            elif kargs.get ('overrides'):
                self._mro [modules [0].__name__] = 'overrides'
            return super ().mount (maybe_point, *modules, **kargs)

    def set_defulat_config (self):
        from . import version_info

        self.config.MEDIA_URL = '/media/'
        self.config.STATIC_URL = '/static/'
        self.config.TEMPLATE_DIRS = []
        self.config.MINIFY_HTML = False
        self.config.MAX_UPLOAD_SIZE = 256 * 1024 * 1024
        self.config.MAINTAIN_INTERVAL = 60

        if version_info [:2] >= (0, 8):
            self.config.JSON_ENCODER = 'utcoffset'
        else:
            self.config.JSON_ENCODER = 'utc'
        self.config.PRETTY_JSON = False

    # directory management ----------------------------------------------------------
    def set_home (self, path, module = None):
        def normpath (d):
            if d [-1] != "/":
                return d + "/"
            return d
        self.config.STATIC_URL = normpath (self.config.STATIC_URL)
        self.config.MEDIA_URL = normpath (self.config.MEDIA_URL)

        self.home = path
        # for backward competable
        if self.authenticate is True:
            try:
                self.authenticate = self.authorization
            except AttributeError:
                self.authenticate = "digest"

        # vaild packages --------------------------------------
        # first, app templates
        template_paths = [path]
        # second, user template
        for d in (self.config.TEMPLATE_DIRS or []):
            template_paths.append (d)

        for d in self.PACKAGE_DIRS:
            maybe_dir = os.path.join (path, d)
            if os.path.isdir (maybe_dir):
                self.add_package_dir (maybe_dir)
            if d in sys.modules:
                self.service_roots.append (sys.modules [d])

        # DEPRECATED on Apr 28, 2021
        # for mounting external package or module, use app.extends ()
        # and explicit add templates/static directories
        # external package templates
        # for d in self._package_dirs:
        #     if not d.endswith ('services'):
        #         continue
        #     additional = os.path.dirname (d)
        #     if additional not in template_paths:
        #         template_paths.append (os.path.dirname (d))

        self.setup_template_engines (template_paths)

        [ self.mount (*_args, **_karg) for _args, _karg in self.mountables if _karg.get ('extends') ]
        module and self.find_mountables (module)
        [ self.mount (*_args, **_karg) for _args, _karg in self.mountables if 'extends' not in _karg and 'overrides' not in _karg ]
        [ self.mount (*_args, **_karg) for _args, _karg in self.mountables if _karg.get ('overrides') ]
        self.mount_explicit ()

        self.mount_nested () # inner imported modules
        self.mount_funcs () # overrides
        self.have_mounted ()
        self.load_jinja_filters ()

    def get_collector (self, request, path_info):
        ct = request.get_header ("content-type", '')
        ws = request.get_header ("upgrade") == 'websocket'
        if not ct and not ws:
            return
        if ct.startswith ("multipart/form-data"):
            return multipart_collector.MultipartCollector
        if not ct.startswith ("application/grpc") and not ct.startswith ("application/octet-stream") and not ws:
            return

        request._method_cache = self.get_method (path_info, request)
        options = request._method_cache [3]
        if ct.startswith ("application/grpc"):
            try:
                i, o = discover.find_type (request.uri [1:])
            except KeyError:
                raise NotImplementedError
            if options.get ('input_stream'):
                return grpc_collector.GRPCStreamCollector
            return grpc_collector.GRPCCollector

        if options.get ('input_stream'):
            if ct.startswith ("application/octet-stream"):
                return stream_collector.StreamCollector
            if ws:
                request.channel.set_socket_timeout (options.get ('websocket_timeout', 60))
                return websocket_collector.WebsocketCollector

    # method search -------------------------------------------
    def get_method (self, path_info, request):
        command = request.command.upper ()
        content_type = request.get_header_noparam ('content-type')
        current_app, method, kargs = self, None, {}
        if self.use_reloader:
            with self.lock:
                self.maybe_reload ()
                current_app, method, kargs, options, status_code = self.find_method (path_info, command)
        else:
            current_app, method, kargs, options, status_code = self.find_method (path_info, command)

        if options and options.get ('subdomain'):
            if not request.get_header ('host', '').startswith (options ['subdomain'] + '.'):
                return current_app, None, None, None, 404

        if status_code:
            return current_app, method, kargs, options, status_code

        status_code = 0
        if options:
            allowed_types = options.get ("content_types", [])
            if allowed_types and content_type not in allowed_types:
                return current_app, None, None, options, 415 # unsupported media type

            if command == "OPTIONS":
                allowed_methods = options.get ("methods", [])
                request_method = request.get_header ("Access-Control-Request-Method")
                if request_method and request_method not in allowed_methods:
                    return current_app, None, None, options, 405 # method not allowed

                response = request.response
                response.set_header ("Access-Control-Allow-Methods", ", ".join (allowed_methods))
                access_control_max_age = options.get ("access_control_max_age", self.access_control_max_age)
                if access_control_max_age:
                    response.set_header ("Access-Control-Max-Age", str (access_control_max_age))

                requeste_headers = request.get_header ("Access-Control-Request-Headers", "")
                if requeste_headers:
                    response.set_header ("Access-Control-Allow-Headers", requeste_headers)
                status_code = 200

            elif not self.is_authorized (request, options.get ("authenticate", self.authenticate)):
                status_code =  401

            access_control_allow_origin = options.get ("access_control_allow_origin", self.access_control_allow_origin)

        else:
            access_control_allow_origin = self.access_control_allow_origin

        if access_control_allow_origin:
            if not self.is_allowed_origin (request, access_control_allow_origin):
                status_code =  403

            elif access_control_allow_origin != 'same':
                origin = request.get_header ('Origin')
                if origin:
                    request.response.set_header ("Access-Control-Allow-Origin", origin)
                    if "*" not in access_control_allow_origin:
                        request.response.set_header ("Access-Control-Allow-Credentials", "true")

        return current_app, method, kargs, options, status_code

    #------------------------------------------------------
    def create_on_demand (self, was, name):
        # create just in time objects
        if name == "cookie":
            return cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)

        elif name in ("session", "mbox"):
            if not was.in__dict__ ("cookie"):
                was.cookie = cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)
            if name == "session":
                return was.cookie.get_session ()
            if name == "mbox":
                return was.cookie.get_notices ()

    def cleanup_on_demands (self, was):
        if not was.in__dict__ ("cookie"):
            return
        for j in ("session", "mbox"):
            if was.in__dict__ (j):
                delattr (was, j)
        del was.cookie

    def __call__ (self, env, start_response):
        was = env ["skitai.was"]

        content_type = env.get ("CONTENT_TYPE", "")
        if content_type.startswith ("text/xml") or content_type.startswith ("application/xml"):
            result = xmlrpc_executor.Executor (env, self.get_method) ()
        elif content_type.startswith ("application/grpc"):
            result = grpc_executor.Executor (env, self.get_method) ()
        elif content_type.startswith ("application/json-rpc"):
            result = jsonrpc_executor.Executor (env, self.get_method) ()
        elif env.get ("websocket.params"):
            result = ws_executor.Executor (env, None) ()
        else:
            result = wsgi_executor.Executor (env, self.get_method) ()

        self.cleanup_on_demands (was) # del session, mbox, cookie, g
        return result
