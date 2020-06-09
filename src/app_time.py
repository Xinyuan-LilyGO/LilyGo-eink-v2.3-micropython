import network
import utime
import machine
import ntptime
import screen
import mainloop
from micropython import const

CONFIG_WIFI = {
    "SSID": "PASSWORD",
}

last_time = (0, 0)
btn = None
width = const(122)
height = const(250)


def __show_info(text):
    screen.clear()
    screen.draw_text(text, 0, 32, screen.FNT_HZK16)
    screen.update_fast()
    return


def init():
    global btn
    # init btn
    btn = machine.Pin(39, machine.Pin.IN)
    # init time
    sync_time()
    # show time
    show_time(force=True)


def sync_time():
    # init network
    __show_info('初始化网络……')
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    not_found = True
    for winfo in sta_if.scan():
        name = winfo[0].decode()
        if name in CONFIG_WIFI:
            not_found = False
            sta_if.connect(name, CONFIG_WIFI[name])
            break
    count = 0
    while not sta_if.isconnected() and count < 30 and not not_found:
        utime.sleep_ms(1000)
    if count >= 30 or not_found:
        __show_info('初始化网络失败')
        utime.sleep_ms(1000)
        return
    # sync time
    __show_info('正在对时……')
    try:
        utime.sleep_ms(1000)
        ntptime.settime()
    except:
        __show_info('对时失败')
        utime.sleep_ms(1000)
        return
    # deinit network
    sta_if.disconnect()
    sta_if.active(False)
    # update timezone
    time = utime.time()
    time = time + 8*3600
    rtc = machine.RTC()
    (year, month, mday, hour, minute, second,
     weekday, yearday) = utime.localtime(time)
    rtc.datetime((year, month, mday, 0, hour, minute, second, 0))


def show_time(force=False):
    global last_time
    (year, month, mday, hour, minute, second, weekday, yearday) = utime.localtime()
    if last_time[0] != minute or (last_time[1] != second and second % 60 == 0) or force:
        last_time = (minute, second)
        # show time
        screen.clear()
        screen.draw_text('当前时间', (width - 64) // 2, 32, screen.FNT_HZK16)  # 48
        screen.draw_text('{:02d}:{:02d}'.format(
            hour, minute), 0, 48, screen.FNT_ASC48)  # 96
#        screen.draw_text('{:02d}'.format(second), width - 32, 96, screen.FNT_ASC16) #112
#        screen.draw_text('秒', width - 16, 96, screen.FNT_HZK16)
        offset = (width - 112) // 2
        screen.draw_text('{:04d}'.format(year), 0 +
                         offset, 112, screen.FNT_ASC16)
        screen.draw_text('年', 32 + offset, 112, screen.FNT_HZK16)
        screen.draw_text('{:02d}'.format(month), 48 +
                         offset, 112, screen.FNT_ASC16)
        screen.draw_text('月', 64 + offset, 112, screen.FNT_HZK16)
        screen.draw_text('{:02d}'.format(mday), 80 +
                         offset, 112, screen.FNT_ASC16)
        screen.draw_text('日', 96 + offset, 112, screen.FNT_HZK16)
        # 112 + 16 + 8 = 136
        offset = (width - 48) // 2
        screen.draw_text('星期', 0 + offset, 136, screen.FNT_HZK16)
        screen.draw_text(['一', '二', '三', '四', '五', '六', '日', ]
                         [weekday], 32 + offset, 136, screen.FNT_HZK16)
        if force:
            screen.update()
        else:
            screen.update_fast()
            screen.update_fast()


def btn_event():
    if btn.value() == 0:
        utime.sleep_ms(10)
        count = 0
        # hold
        while btn.value() == 0:
            count += 1
            utime.sleep_ms(10)
            if count >= 500:
                screen.clear()
                screen.update()
                mainloop.stop()
                return
        # click
        if count > 100:
            __show_info('开发模式')
            mainloop.stop()
            return
        if count > 0:
            sync_time()
            show_time(force=True)
