import os
import time
import threading
import subprocess
import re


class LogicModule:
    def __init__(self, hsl3):
        self.fw = hsl3
        self.debug = self.fw.create_debug_section()

    def on_init(self, inputs, store):
        # protecting member variables for concurrent access
        self.lock = threading.Lock()
        self.proc = None
        
        self.start_proc(inputs)

    def on_calc(self, inputs):
        self.stop_proc()
        self.start_proc(inputs)

    def on_timer(self, timer):
        pass
        
    def start_proc(self, inputs):
        if not inputs["enabled"].value:
            self.debug.log("disabled, not starting ping thread")
            return
        
        self.debug.log("starting thread")
        self.host = inputs["hostname"].value.decode('ascii')
        self.interval = inputs["interval"].value        
        
        self.exitThread = False
        self.ping_thread = threading.Thread(target=self.ping_thread_func)
        self.ping_thread.start()
        
        self.debug.log("thread started")

    def stop_proc(self):
 
        # kill the proc which will terminate the thread
        with self.lock:
            self.exitThread = True
            if self.proc:
                self.debug.log("killing ping")
                self.proc.kill()
                
        if self.ping_thread:
            self.debug.log("stopping thread")
            self.ping_thread.join()
            self.ping_thread = None
            self.debug.log("thread stopped")

    def set_output(self, key, value):
        self.fw.run_in_context(self.fw.set_output, (key, value))

    def ping_thread_func(self):

        pattern = re.compile(r"time=([\d\.]+) ms")
        first = True

        while True:

            assert(self.proc is None)
            
            try:
                
                if first:
                    first = False
                else:
                    duration = min(60, 10*self.interval)
                    self.debug.log("Restarting ping process after %ds" % duration)
                    time.sleep(duration)

                with self.lock:
                    if self.exitThread:
                        break

                with self.lock:
                    DEVNULL = open(os.devnull, 'w')
                    self.proc = subprocess.Popen(['/usr/bin/ping', '-i', "%d" % self.interval, self.host],
                                                 stdout=subprocess.PIPE, stderr=DEVNULL,
                                                 text=True, bufsize=1)
                    stdout = self.proc.stdout
                stdout.readline()
                    
                self.set_output("pinging", 1)

                while True:
                    line = None
                    with self.lock:
                        if self.exitThread:
                            break

                    line = stdout.readline()
                        
                    if line:
                        match = pattern.search(line)

                        if match:
                            val = float(match.group(1))
                            self.set_output("host_delay", val)
                            self.set_output("host_up", 1)
                            #self.debug.log("%s up with %.1f ms" % (self.host, val))
                        else:
                            self.set_output("host_delay", 1000*self.interval)
                            self.set_output("host_up", 0)
                            #self.debug.log("%s down" % self.host)
 
                    else:
                        # check if the process finished. If yes, break. Otherwise, continue.
                        if self.proc.poll() != None:
                            break

            except Exception as e:
                self.debug.log("Exception: %s" % str(e))
                pass

            # clean up and prepare for a restart or exiting the thread
            
            self.set_output("host_delay", 1000*self.interval)
            self.set_output("host_up", 0)
            self.set_output("pinging", 0)

            if self.proc.poll() == None:
                self.proc.kill()

            with self.lock:
                self.proc = None
                
                if self.exitThread:
                    break
                
        self.debug.log("exiting thread")
            
