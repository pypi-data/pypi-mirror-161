import skitai
import time

class TestUtils:
    def test_client (self, point = "/", approot = ".", numthreads = 1, enable_async = False):
        # 2021. 4. 16
        # removed officially, this is used by only unittest
        from skitai.testutil import offline
        from skitai.testutil.offline import client
        app = self

        class Client (client.Client):
            def __init__ (self):
                self.wasc = offline.activate (enable_async = enable_async)
                offline.install_vhost_handler ()
                offline.mount (point, (app, approot))

            def make_request (self, *args, **karg):
                request = client.Client.make_request (self, *args, **karg)
                return self.handle_request (request)

            def close (self):
                app.life_cycle ('before_umount', self.wasc ())
                self.wasc.cleanup (1)
                app.life_cycle ('umounted', self.wasc)
                self.wasc.cleanup (2)
                offline.wasc = None

            def __enter__ (self):
                app.life_cycle ('before_mount', self.wasc)
                app.life_cycle ('mounted', self.wasc ())
                return self

            def __exit__ (self, type, value, tb):
                self.close ()

        return Client ()

    def run (self, address = '127.0.0.1', port = 5000, mount = '/', pref = None):
        skitai.mount (mount, self, pref)
        skitai.run (address = address, port = port)
