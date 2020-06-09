'''
Screen Module
'''
from machine import SPI, Pin
import framebuf
from gdeh0213b73 import EPD, ROTATION_0, ROTATION_90, ROTATION_180, ROTATION_270
import coding, use_codecs

FNT_ASC16 = '/ASC16' # 8x16 16bytes
FNT_ASC48 = '/ASC48' # 24x48 144bytes
FNT_HZK16 = '/HZK16X' # 16x16 32bytes
__UNI2GB2312 = '/unicode2gb2312.codec'
__SCREEN = None

def __get_gb2312_bytes(text):
    return use_codecs.convert_u8_gb2312(
        text.encode("utf8"),
        __UNI2GB2312,
    )

def __get_pure_ascii_bytes(text):
    byts = bytearray()
    for char in text.encode("utf8"):
        if char <= 126 and char >= 32: #32~126, all 94 character
            byts.append(char - 32)
        else:
            byts.append(0x0)
    return byts
    

def init(rotation=ROTATION_0):
    '''init built-in epaper screen'''
    global __SCREEN
    espi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23)
               , polarity=0, phase=0, firstbit=SPI.MSB)
    rst = Pin(16, Pin.OUT, value=1) # default: 1
    dc = Pin(17, Pin.OUT, value=1) # default: 1,
    cs = Pin(5, Pin.OUT, value=1) # default: 1
    busy = Pin(4, Pin.IN, value=0)
    __SCREEN = EPD(espi, cs, dc, rst, busy, rotation=rotation, invert=True)
    __SCREEN.fill(0) # clear

def get_framebuf():
    return __SCREEN

def update_fast():
    __SCREEN.hard_reset()
    __SCREEN.update_fast()
    __SCREEN.deep_sleep()
def update():
    __SCREEN.hard_reset()
    __SCREEN.update()
    __SCREEN.deep_sleep()

def clear():
    __SCREEN.fill(0)

def draw_text(text,x,y,font):
    assert font in [FNT_ASC16, FNT_ASC48, FNT_HZK16]
    if font == FNT_HZK16:
        byts = __get_gb2312_bytes(text)
        assert len(byts) % 2 == 0
        p = 0
        pf = open(FNT_HZK16, "rb")
        while x < __SCREEN.width and p < len(byts):
            char = byts[p:p+2]
            area, posi = coding.GB2312.gb23122pos(char)
            offset = (94 * (area - 1) + posi - 1) * 32
            pf.seek(offset)
            data_buf = memoryview(bytearray(pf.read(32)))
            img = framebuf.FrameBuffer(data_buf, 16, 16, framebuf.MONO_HLSB)
            __SCREEN.blit(img, x, y, 0)
            x += 16
            p += 2
        pf.close()
    if font == FNT_ASC16:
        byts = text.encode("utf8")
        p = 0
        pf = open(FNT_ASC16, "rb")
        while x < __SCREEN.width and p < len(byts):
            char = byts[p]
            pf.seek(char * 16)
            data_buf = memoryview(bytearray(pf.read(16)))
            img = framebuf.FrameBuffer(data_buf, 8, 16, framebuf.MONO_HLSB)
            __SCREEN.blit(img, x, y, 0)
            x += 8
            p += 1
        pf.close()
    if font == FNT_ASC48:
        byts = __get_pure_ascii_bytes(text)
        p = 0
        pf = open(FNT_ASC48, "rb")
        while x < __SCREEN.width and p < len(byts):
            char = byts[p]
            pf.seek(char * 144)
            data_buf = memoryview(bytearray(pf.read(144)))
            img = framebuf.FrameBuffer(data_buf, 24, 48, framebuf.MONO_HLSB)
            __SCREEN.blit(img, x, y, 0)
            x += 24
            p += 1
        pf.close()
