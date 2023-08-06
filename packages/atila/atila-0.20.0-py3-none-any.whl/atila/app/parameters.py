import os
import re
import sys
import inspect
from functools import wraps
import skitai
from ..collectors.multipart_collector import FileWrapper
import types as types_

class Parameters:
    RX_EMAIL = re.compile (r"[a-z0-9][-.a-z0-9]*@[-a-z0-9]+\.[-.a-z0-9]{2,}[a-z]$", re.I)
    RX_UUID = re.compile (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    RX_UNSAFE = re.compile (r"(<script[\s>]|['\"=]\s*javascript:|\son[:a-z]+\s*=\s*|&#x[0-9a-f]{2};|┻━┻)", re.I)
    PARAM_CUSTOM_TYPES = {'required', 'protected', 'manyof', 'oneof', 'emails', 'uuids'}
    PARAM_TYPES = {'ints', 'floats', 'lists', 'strings', 'dicts', 'booleans', 'bools', 'ranges', 'safes', 'notags', 'strs', 'files'}
    OPS = {
        "between": lambda val, fd, cond: not (cond [0] <= val <= cond [1]) and 'parameter {} should be between {} ~ {}'.format (fd, cond [0], cond [1]) or None,
        "in": lambda val, fd, cond: val not in cond and 'parameter {} should be one of {}'.format (fd, cond) or None,
        "notin": lambda val, fd, cond: val in cond and 'parameter {} should be not one of {}'.format (fd, cond) or None,
        "eq": lambda val, fd, cond: val != cond and 'parameter {} should be {}'.format (fd, cond) or None,
        "neq":  lambda val, fd, cond: val == cond and 'parameter {} should not be {}'.format (fd, cond) or None,
        "lte": lambda val, fd, cond: val > cond and 'parameter {} should less or equal than {}'.format (fd, cond) or None,
        "lt": lambda val, fd, cond: val >= cond and 'parameter {} should less than {}'.format (fd, cond) or None,
        "gte": lambda val, fd, cond: val < cond and 'parameter {} should greater or equal than {}'.format (fd, cond) or None,
        "gt": lambda val, fd, cond: val <= cond and 'parameter {} should greater than {}'.format (fd, cond) or None,
        "contains": lambda val, fd, cond: val.find (cond) == -1 and 'parameter {} should contain {}'.format (fd, cond) or None,
        "notcontain": lambda val, fd, cond: val.find (cond) != -1 and 'parameter {} should not contain {}'.format (fd, cond) or None,
        "startswith": lambda val, fd, cond: not val.startswith (cond) and 'parameter {} should start with {}'.format (fd, cond) or None,
        "notstartwith": lambda val, fd, cond: val.startswith (cond) and 'parameter {} should not start with {}'.format (fd, cond) or None,
        "endswith": lambda val, fd, cond: not val.endswith (cond) and 'parameter {} should end with {}'.format (fd, cond) or None,
        "notendwith": lambda val, fd, cond: val.endswith (cond) and 'parameter {} should not end with {}'.format (fd, cond) or None,
        "regex": lambda val, fd, cond: not re.compile (cond).search (val) and 'parameter {} should match with regular expression {}'.format (fd, cond) or None,
    }
    OPS ["exact"] = OPS ["eq"]
    OPS ["nstartswith"] = OPS ["notstartwith"]
    OPS ["ncontains"] = OPS ["notcontain"]
    OPS ["nendswith"] = OPS ["notendwith"]

    def _validate_param (self, params, **kargs):
        params = params or {}
        for k in list (kargs.keys ()):
            if k in self.PARAM_CUSTOM_TYPES:
                fields = kargs.pop (k)
                if k == 'required':
                    for each in fields:
                        try:
                            a, b = each.split (".")
                        except ValueError:
                            if not params.get (each):
                                return 'parameter {} required'.format (each)
                        else:
                            if not params [a] or a not in params or not params [a].get (b):
                                return 'parameter {} required'.format (each)

                elif k == 'protected':
                    for each in fields:
                        try:
                            a, b = each.split (".")
                        except ValueError:
                            if each in params:
                                return 'parameter {} invalid'.format (each)
                        else:
                            if a not in params:
                                break
                            if params [a] and b in params [a]:
                                return 'parameter {} invalid'.format (each)

                elif k in ('oneof', 'manyof'):
                    vals = []
                    for fd in fields:
                        vals.append (params.get (fd) is not None and 1 or 0)
                    if sum (vals) == 0:
                        if k == 'manyof':
                            return 'one or more parameters of {} are required'.format (', '.join (fields))
                        else:
                            return 'one parameter of {} are required'.format (', '.join (fields))
                    if k == 'one' and sum (vals) != 1:
                        return 'exactly one parameter of {} are required'.format (', '.join (fields))

                elif k == 'emails':
                    for fd in fields:
                        kargs [fd] = self.RX_EMAIL

                elif k == 'uuids':
                    for fd in fields:
                        kargs [fd] = self.RX_UUID

            elif k in self.PARAM_TYPES:
                types = kargs.pop (k)
                for each in types:
                    try:
                        val = params [each]
                    except KeyError:
                        continue

                    if val is None:
                        continue

                    try:
                        if k == 'ints':
                            val = int (val)
                        elif k in ('booleans', 'bools'):
                            if val in ('True', 'yes', 'true', 'y', 't'): val = True
                            elif val in ('False', 'no', 'false', 'n', 'f'): val = False
                            if val not in (True, False):
                                return 'parameter {} should be a boolean (one of yes, no, y, n, t, f, true or false)'.format (each)
                        elif k == 'files':
                            if not isinstance (val, FileWrapper):
                                return 'parameter {} should be a file'.format (each)
                        elif k == 'ranges':
                            try:
                                a, b = map (int, val.split ('~'))
                                val = (a, b)
                            except (AttributeError, ValueError):
                                return 'parameter {} should be `1~100` format'.format (each)
                        elif k == 'safes':
                            if self.RX_UNSAFE.search (val):
                                return 'parameter {} is unsafe'.format (each)
                        elif k == 'notags':
                            val = val.replace ('<', '&lt;').replace ('>', '&gt;')
                        elif k == 'floats':
                            val = float (val)
                        elif k == 'lists':
                            if not isinstance (val, (str, list, tuple)):
                                return 'parameter {} should be a list or bar delimtered string'.format (each)
                            if isinstance (val, str):
                                val = val.split ("|")
                        elif k in ('strings', 'strs'):
                            if not isinstance (val, str):
                                raise ValueError
                        elif k == 'dicts':
                            if not isinstance (val, dict):
                                raise ValueError
                        params [each] = val

                    except ValueError:
                        return 'parameter {} should be {} type'.format (each, k [:-1])

        for fd_, cond in kargs.items ():
            es = fd_.split ('___')
            if len (es) > 1: # inspect JSON
                tail = ''
                val = params.get (es [0])
                fds = [es [0]]
                for e in es [1:]:
                    e, *index = e.split ('__')
                    try:
                        val = val [e]
                    except KeyError:
                        return 'parameter {} has key related error'.format (fd_)
                    if not index:
                        index = None
                    else:
                        if index [0].isdigit ():
                            tail = index [1:] or ''
                            try:
                                val = val [int (index [0])]
                            except:
                                return 'parameter {} has index related error'.format (fd_)
                            fds.append (index [0])
                        else:
                            index, tail = None, index
                        if tail:
                            tail = '__{}'.format ('__'.join (tail))
                    fds.append (e)
                fd = '.'.join (fds)
                ops = '{}{}'.format (fd, tail).split ('__')

            else:
                ops = fd_.split ("__")
                fd = ops [0]
                val = params.get (fd)

            if val is None:
                continue

            if not (len (ops) <= 3 and fd):
                raise SyntaxError ("invalid require expression on {}".format (fd))

            if len (ops) == 1:
                if type (cond) is type:
                    cond = [cond]

                if isinstance (cond, (list, tuple)):
                    matched = False
                    for each in cond:
                        if each in (int, float, bool):
                            try:
                                params [fd] = val = each (val)
                            except:
                                pass

                        if isinstance (val, each):
                            matched = True
                            break

                    if not matched:
                        return 'parameter {} should be an instance of {}'.format (fd, cond)

                elif isinstance (cond, types_.FunctionType):
                    newval = cond (skitai.was, val)
                    if newval is not None:
                        params [fd] = val = newval

                elif hasattr (cond, "search"):
                    try:
                        if not cond.search (val):
                            return 'parameter {} is invalid'.format (fd)
                    except TypeError:
                        return 'parameter {} is not string'.format (fd)

                elif val != cond:
                    return 'parameter {} is invalid'.format (fd)

                continue

            if len (ops) == 3:
                if ops [1] == "len":
                    val = len (val)
                    fd = "length of {}".format (fd)
                else:
                    raise ValueError ("Unknown function: {}".format (ops [1]))

            op = ops [-1]
            try:
                val = (isinstance (cond, (list, tuple)) and type (cond [0]) or type (cond)) (val)
            except ValueError:
                return 'parameter {} is invalid'.format (fd)
            try:
                err = self.OPS [op] (val, fd, cond)
                if err:
                    return err
            except KeyError:
                raise ValueError ("Unknown operator: {}".format (op))

        if 'nones' in kargs: # must be None if not val
            nones = kargs ['nones']
            for each in nones:
                try:
                    if not params [each]:
                        params [each] = None
                except KeyError:
                    pass

    def _validate_container (self, request, kargs):
        querystring = request.split_uri () [2]
        if not querystring:
            return

        if request.method in {"POST", "PUT", "PATCH"}:
            if "url" not in kargs and querystring:
                return f"URL parameter not allowed"

        if "url" in kargs:
            query_fields = kargs ["url"]
            for k in query_fields:
                if k in request.DATA:
                    return f"parameter `{k}` should be URL parameter"
            body_fields = [k for k in (list (request.DATA.keys ()) + list (request.URL.keys ())) if k not in query_fields]
            for k in body_fields:
                if k in request.URL:
                    return f"parameter `{k}` should be in body"

    def spec (self, scope = 'ARGS', required = None, **kargs):
        # required, oneof, manyof,
        # ints, floats, uuids, emails, nones, lists, strings, booleans, dicts,
        # notags, safes, ranges,
        # **kargs
        def decorator (f):
            self.save_function_spec (f)
            func_id = self.get_func_id (f)
            if func_id not in self._parameter_caches:
                self._parameter_caches [func_id] = {}
            if required:
                kargs ['required'] = required

            for k, v in kargs.items ():
                if (k in self.PARAM_CUSTOM_TYPES or k in self.PARAM_TYPES) and isinstance (v, str):
                    kargs [k] = v.split ()
                else:
                    kargs [k] = v
            self._parameter_caches [func_id][scope] = kargs

            @wraps (f)
            def wrapper (was, *args, **kwargs):
                scope_ = scope
                if scope in ("FORM", "JSON", "DATA"):
                    if was.request.method not in {"POST", "PUT", "PATCH"}:
                        return f (was, *args, **kwargs)
                    if scope == "JSON" and not was.request.get_header ("content-type", '').startswith ("application/json"):
                        return f (was, *args, **kwargs)

                elif scope not in ("URL", "ARGS"):
                    if was.request.method != scope:
                        return f (was, *args, **kwargs)
                    if scope in {"GET", "DELETE"}:
                        scope_ = "URL"
                    elif scope in {"POST", "PUT", "PATCH"}:
                        if was.request.get_header ("content-type", '').startswith ("application/json"):
                            scope_ = "JSON"
                        else:
                            scope_ = "FORM"
                    else:
                        return f (was, *args, **kwargs)

                validatable_args = getattr (was.request, scope_)
                more_info = self._validate_container (was.request, kargs) or self._validate_param (validatable_args, **kargs)
                if more_info:
                    return was.response.adaptive_error ("400 Bad Request", 'missing or bad parameter in {}'.format (scope_), 40050, more_info)

                # syncing args --------------------------------------
                for k, v in validatable_args.items ():
                    if k in kwargs:
                        kwargs [k] = v
                    if scope_ in ("FORM", "JSON", "URL", "DATA"):
                        was.request.args [k] = v
                    if scope_ == "ARGS":
                        for other_ in ("DATA", "URL"):
                            target_ = getattr (was.request, other_)
                            if target_ and k in target_:
                                target_ [k] = v
                return f (was, *args, **kwargs)

            return wrapper
        return decorator
    require = parameters_required = params_required = test_params = inspect = spec

    def validate (self, request, **kargs):
        more_info = self._validate_param (request.ARGS, **kargs)
        if more_info:
            raise skitai.was.Error ("400 Bad Request", "missing or bad parameter in ARGS (code: 40050): {}".format (more_info), 40050)