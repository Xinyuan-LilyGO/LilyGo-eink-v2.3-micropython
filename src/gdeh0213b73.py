# ========
# e-ink display GDEH0213B73, using 4-wire SPI
# ========
# import gdeh0213b73 as epaper
# screen = epaper.EPD(espi, cs, dc, rst, busy)
# screen.fill(1)
# screen.text('Hello Dragon!',6,32,0)
# screen.update()
# # screen.update_fast()
# ========
from micropython import const
from time import sleep_ms
import framebuf

# Rotaion
ROTATION_0 = const(0)
ROTATION_90 = const(1)
ROTATION_180 = const(2)
ROTATION_270 = const(3)
# Display resolution
EPD_WIDTH = const(128)
EPD_HEIGHT = const(250)
# datasheet says 122x250 (increased to 128 to be multiples of 8)
# lut define, refer to SSD1675B
LUT_FULL_UPDATE = memoryview(bytes([
    0xA0,   0x90,   0x50,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x50,   0x90,   0xA0,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0xA0,   0x90,   0x50,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x50,   0x90,   0xA0,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,

    0x0F,   0x0F,   0x00,   0x00,   0x00,
    0x0F,   0x0F,   0x00,   0x00,   0x03,
    0x0F,   0x0F,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,

    0x17,   0x41,   0xA8,   0x32,   0x50, 0x0A, 0x09,
]))
LUT_PART_UPDATE = memoryview(bytes([
    0x40,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x80,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x40,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x80,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,   0x00,

    0x0A,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x00,   0x00,   0x00,   0x00,   0x00,
    0x15,   0x41,   0xA8,   0x32,   0x50,   0x2C, 0x0B,
]))
# Display commands
DRIVER_OUTPUT_CONTROL = b'\x01'
GATE_DRIVING_VOLTAGE_CONTROL = b'\x03'
SOURCE_DRIVING_VOLTAGE_CONTROL = b'\x04'
BOOSTER_SOFT_START_CONTROL = b'\x0C'  # not in datasheet
# GATE_SCAN_START_POSITION             = b'\x0F' # not in datasheet
DEEP_SLEEP_MODE = b'\x10'
DATA_ENTRY_MODE_SETTING = b'\x11'
SW_RESET = b'\x12'
#TEMPERATURE_SENSOR_CONTROL           = b'\x1A'
MASTER_ACTIVATION = b'\x20'
DISPLAY_UPDATE_CONTROL_1 = b'\x21'
DISPLAY_UPDATE_CONTROL_2 = b'\x22'
# Panel Break Detection              b'\x23'
WRITE_RAM = b'\x24'
WRITE_VCOM_REGISTER = b'\x2C'
# Status Bit Read                    b'\x2F'
WRITE_LUT_REGISTER = b'\x32'
SET_DUMMY_LINE_PERIOD = b'\x3A'
SET_GATE_TIME = b'\x3B'
BORDER_WAVEFORM_CONTROL = b'\x3C'
SET_RAM_X_ADDRESS_START_END_POSITION = b'\x44'
SET_RAM_Y_ADDRESS_START_END_POSITION = b'\x45'
SET_RAM_X_ADDRESS_COUNTER = b'\x4E'
SET_RAM_Y_ADDRESS_COUNTER = b'\x4F'
SET_ANALOG_BLOCK_CONTROL = b'\x74'
SET_DIGITAL_BLOCK_CONTROL = b'\x7E'
TERMINATE_FRAME_READ_WRITE = b'\xFF'  # not in datasheet, aka NOOP


class EPD(framebuf.FrameBuffer):
    def __init__(self, spi, cs, dc, rst, busy, rotation=ROTATION_0, invert=False):
        #self.spi = espi = SPI(2, baudrate=20000000, sck=Pin(18), mosi=Pin(23), polarity=0, phase=0, firstbit=SPI.MSB)
        #self.spi = SPI(1, 10000000, sck=Pin(14), mosi=Pin(13), miso=Pin(12))
        self.spi = spi
        self.spi.init()
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN, value=0)
        self.__rotation = rotation  # can`t be changed later
        self.__invert = invert
        # init framebuf
        if self.__rotation == ROTATION_0 or self.__rotation == ROTATION_180:
            self.__width = EPD_WIDTH
            self.__height = EPD_HEIGHT
        else:
            self.__width = EPD_HEIGHT
            self.__height = EPD_WIDTH
        size = self.__width * self.__height // 8
        self.buffer = memoryview(bytearray(size))
        super().__init__(self.buffer, self.__width, self.__height, framebuf.MONO_HLSB)
        self.hard_reset()

    @property
    def rotation(self):
        return self.__rotation

    @property
    def height(self):
        return self.__height

    @property
    def width(self):
        return self.__width

    def _command(self, command, data=None):
        self.cs(1)  # according to LOLIN_EPD
        self.dc(0)
        self.cs(0)
        self.spi.write(command)
        self.cs(1)
        if data is not None:
            self._data(data)

    def _data(self, data):
        self.cs(1)  # according to LOLIN_EPD
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def _init(self):
        self._wait_until_idle()
        self._command(SW_RESET)  # soft reset
        self._wait_until_idle()
        # set analog block control
        self._command(SET_ANALOG_BLOCK_CONTROL, b'\x54')
        # set digital block control
        self._command(SET_DIGITAL_BLOCK_CONTROL, b'\x3B')
        # Driver output control
        self._command(DRIVER_OUTPUT_CONTROL, b'\xF9\x00\x00')
        self._command(DATA_ENTRY_MODE_SETTING, b'\x03')  # data entry mode
        self._command(BORDER_WAVEFORM_CONTROL, b'\x00')  # BorderWavefrom
        self._command(WRITE_VCOM_REGISTER, b'\x50')  # VCOM Voltage
        self._command(GATE_DRIVING_VOLTAGE_CONTROL, LUT_FULL_UPDATE[100:101])
        self._command(SOURCE_DRIVING_VOLTAGE_CONTROL, LUT_FULL_UPDATE[101:103])
        self._command(SET_DUMMY_LINE_PERIOD,
                      LUT_FULL_UPDATE[105:106])  # Dummy Line
        self._command(SET_GATE_TIME, LUT_FULL_UPDATE[106:107])  # Gate time
        self._set_lut(LUT_FULL_UPDATE[0:100])
        self.invert(self.__invert)
        self._wait_until_idle()

    def _power_on(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xC0')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

    def _power_off(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xC3')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

    def _init_full(self):
        self._init()
        self._set_lut(LUT_FULL_UPDATE)
        self._power_on()

    def _init_part(self):
        self._init()
        self._set_lut(LUT_PART_UPDATE)
        self._power_on()

    def _update_full(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\xC7')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()

    def _update_part(self):
        self._command(DISPLAY_UPDATE_CONTROL_2, b'\x04')
        self._command(MASTER_ACTIVATION)
        self._wait_until_idle()
        self._command(TERMINATE_FRAME_READ_WRITE)

    def _wait_until_idle(self):
        while self.busy.value() == 1:
            sleep_ms(10)

    def _set_lut(self, lut):
        self._command(WRITE_LUT_REGISTER, lut)

    @micropython.native
    def _get_rotated_buffer(self):
        # no need to rotate
        if self.__rotation == ROTATION_0:
            return self.buffer
        # create buffer and rotate
        size = EPD_WIDTH * EPD_HEIGHT // 8
        fbuffer = memoryview(bytearray(size))
        frame = framebuf.FrameBuffer(
            fbuffer, EPD_WIDTH, EPD_HEIGHT, framebuf.MONO_HLSB)
        # copy buffer
        if self.__rotation == ROTATION_270:
            for x in range(self.__width):
                for y in range(self.__height):
                    frame.pixel(y, EPD_HEIGHT-x-1, self.pixel(x, y))
        if self.__rotation == ROTATION_90:
            for x in range(self.__width):
                for y in range(self.__height):
                    frame.pixel(EPD_WIDTH-y-1, x, self.pixel(x, y))
            frame.scroll(-6, 0)
        if self.__rotation == ROTATION_180:
            for i in range(size):
                fbuffer[size-i-1] = self.buffer[i]
            frame.scroll(-6, 0)
        return fbuffer

    def deep_sleep(self):
        self._command(DEEP_SLEEP_MODE, b'\x01')

    def hard_reset(self):
        self.rst(1)
        sleep_ms(1)
        self.rst(0)
        sleep_ms(10)
        self.rst(1)

    def update(self):
        self._init_full()
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION,
                      b'\x00\x0F')  # 0x0F-->(15+1)*8=128
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION,
                      b'\x00\x00\xF9\x00')  # 0xF9-->(249+1)=250
        # set RAM x address count to 0
        self._command(SET_RAM_X_ADDRESS_COUNTER, b'\x00')
        # set RAM y address count to 249(0xF9)
        self._command(SET_RAM_Y_ADDRESS_COUNTER, b'\x00\x00')
        self._wait_until_idle()
        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._update_full()
        self._power_off()

    def update_fast(self):
        self._init_part()
        self._command(SET_RAM_X_ADDRESS_START_END_POSITION,
                      b'\x00\x0F')  # 0x0F-->(15+1)*8=128
        self._command(SET_RAM_Y_ADDRESS_START_END_POSITION,
                      b'\x00\x00\xF9\x00')  # 0xF9-->(249+1)=250
        # set RAM x address count to 0
        self._command(SET_RAM_X_ADDRESS_COUNTER, b'\x00')
        # set RAM y address count to 249(0xF9)
        self._command(SET_RAM_Y_ADDRESS_COUNTER, b'\x00\x00')
        self._wait_until_idle()
        self._command(WRITE_RAM, self._get_rotated_buffer())
        self._update_part()
        self._power_off()

    def invert(self, value=None):
        if value == None:
            return self.__invert
        if value:
            self._command(DISPLAY_UPDATE_CONTROL_1, b'\x08')
        else:
            self._command(DISPLAY_UPDATE_CONTROL_1, b'\x00')
        self.__invert = value
