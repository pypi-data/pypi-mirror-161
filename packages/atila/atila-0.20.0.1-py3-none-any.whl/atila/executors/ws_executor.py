from . import wsgi_executor
from skitai.backbone.http_response import catch
import asyncio
from skitai.utility import deallocate_was

class Executor (wsgi_executor.Executor):
    def respond_async (self, was, task):
        try:
            content = task.fetch ()
            if type (content) is not tuple:
                content = (content,)
            was.websocket.send (*content)
        except:
            was.traceback ()
            was.websocket.channel and was.websocket.channel.close ()
        finally:
            was.async_executor.done ()
            deallocate_was (was)

    def __call__ (self):
        self.was = self.env ["skitai.was"]
        current_app, wsfunc = self.env.get ("websocket.handler")
        content = wsfunc (self.was, **self.env.get ("websocket.params", {}))
        if not asyncio.iscoroutine (content):
            return content

        assert hasattr (self.was, "async_executor"), "async is not enabled"
        self.add_async_task (content)

