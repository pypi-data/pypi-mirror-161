from skitai.tasks import utils
import threading
import queue
from skitai.backbone.threaded import trigger
from rs4.misc import strutil

class OutputStream:
    def __init__ (self, was, handler, use_thread_pool = False):
        self.was = was
        self.handler = handler
        self.queue = queue.Queue ()
        self._rtype = utils.determine_response_type (self.was.request)
        if use_thread_pool:
            was.thread_executor.submit (self.run)
        else:
            threading.Thread (target = self.run).start ()

    def emit (self, item):
        if not item:
            self.close ()
            return ""
        self.queue.put_nowait (item)

    def run (self):
        response = self.was.response
        while 1:
            item = self.queue.get ()
            if item is None:
                break

            msgs = []
            for msg in self.handler (self.was, item):
                msg = utils.serialize (self._rtype, msg)
                if msg is None:
                    continue
                if strutil.is_encodable (msg):
                    msg = msg.encode ("utf8")
                msgs.append (msg)

            if msgs:
                response.current_producer.send (b''.join (msgs))
                trigger.wakeup ()

    def close (self):
        self.queue.put_nowait (None)
        self.was = None

