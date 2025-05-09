#!/usr/bin/python
import subprocess
cmd = subprocess.Popen(['/bin/ping', '1.1.1.1'], stdout=subprocess.PIPE)
while True:
    line = cmd.stdout.readline()
    if not line:
        break
    print("ok")
    
