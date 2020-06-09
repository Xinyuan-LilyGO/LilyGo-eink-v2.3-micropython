# This file is executed on every boot (including wake-boot from deepsleep)
import esp,machine
esp.osdebug(None)
machine.freq(80000000)
del esp,machine
#import webrepl
#webrepl.start()
