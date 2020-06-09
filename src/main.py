#from machine import SPI, Pin
#from sdcard import SDCard
#import os
#sd = SDCard(SPI(1,sck=Pina(14), mosi=Pin(15), miso=Pin(2)), Pin(13))
#os.mount(sd,"/sd")
#os.listdir()
#del sd,SDCard,SPI,Pin,os
def timed_function(f, *args, **kwargs):
    myname = str(f).split(' ')[1]
    def new_func(*args, **kwargs):
        import utime
        t = utime.ticks_us()
        result = f(*args, **kwargs)
        delta = utime.ticks_diff(utime.ticks_us(), t)
        print('Function {} Time = {:6.3f}ms'.format(myname, delta/1000))
        return result
    return new_func

def free():
    import gc
    gc.collect()
    print(gc.mem_free())
    del gc

# init screen
import screen
screen.init()

# init mainloop and application
import mainloop, app_time


@timed_function
def refresh_time():
    screen.draw_text('Hello Dragon',14,8,screen.FNT_ASC16)
    screen.draw_text('当前时间',0,32,screen.FNT_HZK16)
    screen.draw_text('13:18',0,48,screen.FNT_ASC48)
    screen.update_fast()
    return

def main():
    app_time.init()
    mainloop.add_task("show_time",app_time.show_time)
    mainloop.add_task("btn_event",app_time.btn_event)
    mainloop.start()

main()