from rs4.protocols.sock.impl.http import http_util
import sys
from rs4.attrdict import AttrDict
from rs4.protocols.sock.impl.http import respcodes
from skitai.exceptions import HTTPError
from skitai.wastuff.api import API
import re
from types import GeneratorType
from ..events import *
try:
    from css_html_js_minify import html_minify
except ImportError:
    html_minify = None
import asyncio
import inspect
import skitai

RX_STRIP = re.compile ('^\s+', re.M)
def html_strip (html):
    return RX_STRIP.sub ('', html)

def traceback ():
    t, v, tb = sys.exc_info ()
    tbinfo = []
    assert tb # Must have a traceback
    while tb:
        tbinfo.append((
            tb.tb_frame.f_code.co_filename,
            tb.tb_frame.f_code.co_name,
            str(tb.tb_lineno)
            ))
        tb = tb.tb_next

    del tb
    file, function, line = tbinfo [-1]
    return (
        "%s %s, file %s at line %s, %s" % (
            t, v, file, line,
            function == "?" and "__main__" or "function " + function
        )
    )


def after_request_async (was, content, exc_info = None):
    def postprocess (was, content, exc_info, depends, hooks):
        success, failed, teardown = hooks
        try:
            try:
                if exc_info is None:
                    for func in depends:
                        content = was.execute_function (func, (was,)) or content
                    if success:
                        content = was.execute_function (success, (was, content)) or content
                    was.app.emit (EVT_REQ_SUCCESS, content)
                else:
                    if failed:
                        content = was.execute_function (failed, (was, exc_info)) or content
                    was.app.emit (EVT_REQ_FAILED, exc_info)

            finally:
                teardown and was.execute_function (teardown, (was,))
                was.app.emit (EVT_REQ_TEARDOWN)

        except:
            content = was.response.build_error_template (was.app.debug and sys.exc_info () or None, 0, was = was)
            was.traceback ()

        was.send_content_async (content, True)

    has_hooks = True
    try:
        hooks = was.request._hooks
    except AttributeError:
        hooks = (None, None, None)
        has_hooks = False

    try:
        depends = was.request._depends
    except AttributeError:
        depends = []

    if not has_hooks and not depends:
        return was.send_content_async (content)

    was.thread_executor.submit (postprocess, was, content, exc_info, depends, hooks)


class Executor:
    def __init__ (self, env, get_method):
        self.env = env
        self.get_method = get_method
        self.was = None

    def chained_exec (self, method, args, karg, make_list = True):
        # recursive before, after, teardown
        # [b, [b, [b, func, s, f, t], s, f, t], s, f, t]

        app, response, exc_info = self.was.app, None, None
        [before, func, success, failed, teardown] = method

        is_coroutine = asyncio.iscoroutinefunction (func) or inspect.isgeneratorfunction (func)
        if is_coroutine:
            self.was.request._hooks = (success, failed, teardown)

        try:
            try:
                if before:
                    response = self.was.execute_function (before, (self.was,))
                app.emit (EVT_REQ_STARTED)
                if response is None:
                    if type (func) is list:
                        response = self.chained_exec (func, args, karg, make_list)
                    else:
                        response = func (self.was, *args, **karg)
            except MemoryError:
                raise

            except Exception as expt:
                is_coroutine = False # IMP
                exc_info = sys.exc_info ()
                if failed:
                    response = self.was.execute_function (failed, (self.was, exc_info))
                app.emit (EVT_REQ_FAILED, exc_info)
                if response is None:
                    raise
                else:
                    # filed handle exception and contents, just log
                    self.was.traceback ()

            else:
                if not is_coroutine:
                    if success:
                        response = self.was.execute_function (success, (self.was, response)) or response
                    app.emit (EVT_REQ_SUCCESS, response)

        finally:
            if not is_coroutine:
                teardown and self.was.execute_function (teardown, (self.was))
                app.emit (EVT_REQ_TEARDOWN)

        return [response] if (make_list and type (response) is not list) else response

    def verify_args_lazy (self, karg):
        if self.was.request.PARAMS:
            uparams = self.was.request.routable.get ("args", [])[:self.was.request.routable.get ("urlargs", 0)]
            for arg in self.was.request.PARAMS:
                if arg not in uparams:
                    raise HTTPError ("530 Parameter Mismatch")

        args = self.was.request.routable.get ("args")
        if not args:
            raise HTTPError ("400 Bad Request", "no parameter need")
        defaults = self.was.request.routable.get ("defaults")
        urlargs = self.was.request.routable.get ("urlargs", 0)
        if urlargs:
            required = set (args [:urlargs])
            if defaults:
                required = required.difference (set (defaults.keys ()))
            for arg in required:
                if arg not in karg:
                    raise HTTPError ("400 Bad Request", "conflict url parameters")

        required = set (args)
        if defaults:
            required = required.difference (set (defaults.keys ()))

        for r in required:
            if r not in karg:
                raise HTTPError ("400 Bad Request", "parameter `{}` is missing".format (r))
        if self.was.request.routable.get ("keywords"):
            return

        for r in karg:
            if r not in args:
                raise HTTPError ("400 Bad Request", "parameter `{}` needn't".format (r))

    def generate_content (self, method, _args, karg):
        karg = self.parse_kargs (karg)
        try:
            response = self.chained_exec (method, _args, karg)
        except TypeError:
            self.was.traceback ()
            self.verify_args_lazy (karg) #lazy validating request parameters for respond 400
            raise
        return response

    def is_calling_args_group (self, data, forward = True):
        if self.was.request.routable.get ('keywords'):
            return True

        wanted_args = self.was.request.routable.get ('args') [self.was.request.routable.get ('urlargs', 0):]
        if not wanted_args:
            if self.was.app.restrict_parameter_count:
                raise HTTPError ("400 Bad Request", "too many parameter(s)")
            return False
        elif not data:
            raise HTTPError ("400 Bad Request", "some missing parameters")

        if self.was.app.restrict_parameter_count:
            return True

        if forward:
            if wanted_args:
                return True
            for k in wanted_args:
                if k in data:
                    return True
        else:
            for i in range (-1, -(len (wanted_args) + 1), -1):
                if wanted_args [i] in data:
                    return True
        return False

    def merge_args (self, s, n, overwrite = False):
        for k, v in list(n.items ()):
            if k in s:
                if overwrite:
                    s [k] = v
                    continue
                if type (s [k]) is not list:
                    s [k] = [s [k]]
                s [k].append (v)
            else:
                s [k] = v

    def parse_kargs (self, kargs):
        self.was.request.PARAMS = kargs.copy ()
        query = self.env.get ("QUERY_STRING")
        data = self.was.request.dict ()

        allkarg = AttrDict ()
        self.merge_args (allkarg, kargs)

        if not query and not data:
            self.was.request.set_args (allkarg)
            return kargs

        query_included = True
        if query:
            try:
                querydict = http_util.crack_query (query)
            except IndexError:
                raise HTTPError ("400 Error", 'invalid query string')
            self.was.request.URL = querydict

            self.merge_args (allkarg, querydict)
            if self.is_calling_args_group (querydict): # if takes URL params
                if not data:
                    self.was.request.set_args (allkarg)
                    return allkarg
                self.merge_args (kargs, querydict)
            else:
                query_included = False

        if data:
            self.merge_args (allkarg, data, overwrite = True)
            if query_included and self.is_calling_args_group (data, False): # if takes POST params
                self.was.request.set_args (allkarg)
                return allkarg

        self.was.request.set_args (allkarg)
        return kargs

    def commit (self):
        if self.was.app is None: # this is failed request
            return
        # keep commit order, session -> mbox -> cookie
        if not self.was.in__dict__ ("cookie"):
            return
        if self.was.in__dict__ ("session"):
            self.was.session and self.was.session.commit ()
        if self.was.in__dict__ ("mbox"):
            self.was.mbox and self.was.mbox.commit ()
        self.was.cookie.commit ()

    def rollback (self):
        if self.was.app is None: # this is failed request
            return
        if not self.was.in__dict__ ("cookie"):
            return
        # keep commit order, session -> mbox -> cookie
        if self.was.in__dict__ ("session"):
            self.was.session and self.was.session.rollback ()
        if self.was.in__dict__ ("mbox"):
            self.was.mbox and self.was.mbox.rollback ()
        self.was.cookie.rollback ()

    def find_method (self, request, path, handle_response = True):
        try:
            cached = request._method_cache
        except AttributeError:
            cached = self.get_method (path, request)
        current_app, thing, param, options, respcode = cached
        if respcode and handle_response:
            if respcode == 301:
                request.response ["Location"] = thing
                request.response.error (301, "Object Moved", why = 'Object Moved To <a href="%s">Here</a>' % thing)
            elif respcode != 200:
                request.response.error (respcode, respcodes.get (respcode, "Undefined Error"))

        if thing:
            self.env ["wsgi.app"] = current_app
            self.env ["wsgi.routed"] = current_app.get_routed (thing)
            self.env ["wsgi.route_options"] = options
            request.env = self.env

        current_app.maintern ()
        return current_app, thing, param, respcode

    # async/coroutine processing ------------------------------------------------
    def respond_async (self, was, task):
        try:
            content = task.fetch ()
        finally:
            was.async_executor.done ()
        return content

    def add_async_task (self, coro):
        return skitai.add_async_task (coro, after_request_async, self.respond_async)

    def add_coroutine_task (self, coro):
        return skitai.add_coroutine_task (coro, after_request_async)

    # request processing ------------------------------------------------
    def minify_html (self, content, current_app):
        try:
            is_html = self.was.response.get_header ('content-type') in ('text/html', None)
        except AttributeError:
            return content

        if not is_html:
            return content

        try:
            minify_level = current_app.config.get ('MINIFY_HTML')
            if minify_level == 'minify' and html_minify:
                content = [html_minify (content [0])]
            elif minify_level == 'strip':
                content = [html_strip (content [0])]
        except:
            self.was.traceback ()
        return content

    def __call__ (self):
        self.was = self.env ["skitai.was"]
        request = self.was.request
        current_app = self.was.app

        try:
            current_app, thing, param, respcode = self.find_method (request, self.env ["PATH_INFO"])
            if respcode:
                # unacceptable
                return b""

            if current_app.expose_spec and current_app.debug and request.channel and request.channel.addr [0].startswith ("127.0.0."):
                self.env ['ATILA_SET_SEPC'] = 'yes'

            try:
                content = self.generate_content (thing, (), param)

                if len (content) == 1 and isinstance (content [0], str):
                    content = self.minify_html (content, current_app)

                if self.env ['wsgi.route_options'].get ('coroutine'):
                    assert isinstance (content [0], GeneratorType), "coroutine expected"
                    content = self.add_coroutine_task (content [0])

                elif asyncio.iscoroutine (content [0]) and not isinstance (content [0], GeneratorType):
                    assert hasattr (self.was, "async_executor"), "async is not enabled"
                    content = self.add_async_task (content [0])

            except AssertionError as e:
                # transit AssertionError into HTTPError
                if e.args:
                    if isinstance (e.args [0], HTTPError):
                        raise e.args [0]
                    elif e.args [0].startswith ('HTTPError'):
                        raise eval (e.args [0].split ('\n')[0])
                raise e

        except MemoryError:
            raise

        except HTTPError as e:
            self.rollback ()
            content = [request.response.with_explain (e.status, e.explain or (self.was.app.debug and e.exc_info), e.errno)]

        except:
            self.was.traceback ()
            self.rollback ()
            content = [request.response ("502 Bad Gateway", exc_info = self.was.app.debug and sys.exc_info () or None)]

        else:
            self.commit ()

        # app global post processing ----------------------------
        try:
            settable = self.env.get ('ATILA_SET_SEPC') and len (content) == 1 and isinstance (content [0], API)
        except TypeError: # Coroutine
            pass
        else:
            settable and content [0].set_spec (current_app)

        # clean was
        current_app.emit ("request:finished")
        return content
