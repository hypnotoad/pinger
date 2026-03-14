#!/usr/bin/python3

from hsl3_14046_pinger import LogicModule
from hsl3dummy import Hsl3Framework, Hsl3Slots
import time
import sys

fw = Hsl3Framework("config.json")
module = LogicModule(fw)


test_input = {"hostname": b'1.1.1.1',
              "interval": 2
              }
inputs=Hsl3Slots(test_input)
store=Hsl3Slots({})
module.on_init(inputs, store)

time.sleep(5)

if True:
    print("%%% Testing changing the interval")
    inputs=Hsl3Slots(test_input)
    inputs["interval"].value = 1
    inputs["interval"].changed = True
    module.on_calc(inputs)

    time.sleep(5)

if True:
    print("%%% Testing changing the host name")
    inputs=Hsl3Slots(test_input)
    inputs["hostname"].value = b"8.8.8.8"
    inputs["hostname"].changed = True
    module.on_calc(inputs)

    time.sleep(5)

if True:
    print("%%% Testing unpingable")
    inputs=Hsl3Slots(test_input)
    inputs["hostname"].value = b"1.2.3.4"
    inputs["hostname"].changed = True
    module.on_calc(inputs)

    time.sleep(5)

if True:
    print("%%% Testing name resolution")
    inputs=Hsl3Slots(test_input)
    inputs["hostname"].value = b"localhost"
    inputs["hostname"].changed = True
    module.on_calc(inputs)

    time.sleep(5)

if True:
    print("%%% Testing unresolvable")
    inputs=Hsl3Slots(test_input)
    inputs["hostname"].value = b"foo.bar.doesnotexist"
    inputs["hostname"].changed = True
    module.on_calc(inputs)

    time.sleep(5)
    
print("%%% Waiting")
time.sleep(10000)
