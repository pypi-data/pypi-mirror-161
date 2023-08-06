from rs4.psutil import piped_process

class PipedProcess (piped_process.PipedProcess):
    def __init__ (self, fp, command):
        self.fp = fp
        super ().__init__ (command)

    def log (self, line, *args):
        if not self.fp:
            return
        self.fp.write (line.strip ())

