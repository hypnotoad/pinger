# coding: iso-8859-15

global time
import time
global threading
import threading
global subprocess
import subprocess
global re
import re


##!!!!##################################################################################################
#### Own written code can be placed above this commentblock . Do not change or delete commentblock! ####
########################################################################################################
##** Code created by generator - DO NOT CHANGE! **##

class Pinger14046(hsl20_4.BaseModule):

    def __init__(self, homeserver_context):
        hsl20_4.BaseModule.__init__(self, homeserver_context, "rd_pinger")
        self.FRAMEWORK = self._get_framework()
        self.LOGGER = self._get_logger(hsl20_4.LOGGING_NONE,())
        self.PIN_I_HOSTNAME=1
        self.PIN_I_INTERVAL=2
        self.PIN_O_HOST_UP=1
        self.PIN_O_HOST_DELAY=2
        self.PIN_O_PINGING=3

########################################################################################################
#### Own written code can be placed after this commentblock . Do not change or delete commentblock! ####
###################################################################################################!!!##

    def on_init(self):
        # protecting host, interval, proc for write access
        self.lock = threading.Lock()

        #self.LOGGER.set_level(10)
        self.LOGGER.info("on_init")

        self.proc = None
        self.start_proc()
        

    def on_input_value(self, index, value):
        self.LOGGER.info("on_input_value %d %s" % (index, value))
        self.stop_proc()
        self.start_proc()

    def start_proc(self):
        self.LOGGER.info("starting thread")
        
        self.exitThread = False
        self.host = self._get_input_value(self.PIN_I_HOSTNAME)
        self.interval = self._get_input_value(self.PIN_I_INTERVAL)
        self.ping_thread = threading.Thread(target=self.ping_thread_func)
        self.ping_thread.start()
        
        self.LOGGER.info("thread started")

    def stop_proc(self):
        self.LOGGER.info("stopping thread")
 
        # kill the proc which will terminate the thread
        with self.lock:
            self.LOGGER.info("killing")
            self.exitThread = True
            if self.proc:
                self.proc.kill()
        self.ping_thread.join()
        self.ping_thread = None
        
        self.LOGGER.info("thread stopped")
            
    def ping_thread_func(self):

        pattern = re.compile("time=([\d\.]+) ms")
        first = True

        while True:

            assert(self.proc is None)
            
            try:
                
                if first:
                    first = False
                else:
                    duration = min(60, 10*self.interval)
                    self.LOGGER.info("Restarting ping process after %ds" % duration)
                    time.sleep(duration)

                with self.lock:
                    if self.exitThread:
                        break

                with self.lock:
                    DEVNULL = open(os.devnull, 'w')
                    self.proc = subprocess.Popen(['/usr/bin/ping', '-i', "%d" % self.interval, self.host],
                                                 stdout=subprocess.PIPE, stderr=DEVNULL)
                    self.proc.stdout.readline()
                    
                self._set_output_value(self.PIN_O_PINGING, 1)

                while True:
                    line = None
                    with self.lock:
                        if self.exitThread:
                            break

                    line = self.proc.stdout.readline()
                        
                    if line:
                        match = pattern.search(line)

                        if match:
                            val = float(match.group(1))
                            self._set_output_value(self.PIN_O_HOST_DELAY, val)
                            self._set_output_value(self.PIN_O_HOST_UP, 1)
                            self.LOGGER.info("%s up with %.1f ms" % (self.host, val))
                        else:
                            self._set_output_value(self.PIN_O_HOST_DELAY, 1000*self.interval)
                            self._set_output_value(self.PIN_O_HOST_UP, 0)
                            self.LOGGER.info("%s down" % self.host)
 
                    else:
                        self.LOGGER.info("Could not read result.")

                        # check if the process finished. If yes, break. Otherwise, continue.
                        if self.proc.poll() != None:
                            break

            except Exception as e:
                self.LOGGER.info("Exception. %s" % str(e))
                pass

            # clean up and prepare for a restart or exiting the thread
            
            self._set_output_value(self.PIN_O_HOST_DELAY, 1000*self.interval)
            self._set_output_value(self.PIN_O_HOST_UP, 0)
            self._set_output_value(self.PIN_O_PINGING, 0)

            if self.proc.poll() == None:
                self.proc.kill()

            with self.lock:
                self.proc = None
                
                if self.exitThread:
                    break
                
        self.LOGGER.info("exiting thread")
            
