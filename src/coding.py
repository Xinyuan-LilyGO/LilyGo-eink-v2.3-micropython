# 编码工具类
def url_decode(url):
    pos = 0
    byts = b''
    while pos < len(url):
        ch = url[pos]
        if ch != '%':
            # ascii code
            byts = byts+ch.encode('utf-8')
            pos = pos + 1
            continue
        else:
            # no ascii code
            hex = url[pos+1:pos+3]
            byts = byts + bytes([int(hex, 16)])
            pos = pos + 3
            continue
    return byts.decode('utf-8')


class UTF_8():
    @staticmethod
    def u8len(first_byte):
        pat = 0x01 << 7  # 1000000
        byt = first_byte  # first byte
        l = 0  # length
        while byt & pat != 0:
            l = l + 1
            pat = pat >> 1
        if l == 0:
            l = 1  # for ascii
        return l

    @staticmethod
    def u82unicode(u8):
        l = UTF_8.u8len(u8[0])
        value = 0x00
        if l == 1:
            value = value + u8[0]
        else:
            # head
            pat = 0xFF >> (l+1)
            value = value | (u8[0] & pat)  # head byte
            for i in range(1, l):
                value = value << 6
                value = value | (u8[i] & 0x3F)  # following byte
        return value

    @staticmethod
    def unicode2u8(value):
        u8 = None
        if value <= 0x7F:
            # 1 byte utf-8
            u8 = bytearray([value])
            pass
        elif value <= 0x07FF:
            # 2 bytes utf-8
            u8 = bytearray([0]*2)
            u8[0] = 0xC0  # 110 xxxxx
            u8[0] = u8[0] | (value >> 6)  # xxxxx|
            u8[1] = 0x80  # 10 xxxxxx
            u8[1] = u8[1] | (value & 0x3F)  # 00000 xxxxxx
            pass
        elif value <= 0xFFFF:
            # 3 bytes utf-8
            u8 = bytearray([0]*3)
            u8[0] = 0xE0  # 1110 xxxx
            u8[0] = u8[0] | (value >> 12)  # xxxx|
            u8[1] = 0x80  # 10 xxxxxx
            u8[1] = u8[1] | ((value >> 6) & 0x3F)  # 0000 xxxxxx 000000
            u8[2] = 0x80  # 10 xxxxxx
            u8[2] = u8[2] | (value & 0x3F)  # 0000 000000 xxxxxx
            pass
        elif value <= 0x1FFFF:
            # 4 bytes utf-8
            u8 = bytearray([0]*4)
            u8[0] = 0xF0  # 11110 xxx
            u8[0] = u8[0] | (value >> 18)  # xxx|
            u8[1] = 0x80  # 10 xxxxxx
            u8[1] = u8[1] | ((value >> 12) & 0x3F)  # 000 xxxxxx 000000 000000
            u8[2] = 0x80  # 10 xxxxxx
            u8[2] = u8[2] | ((value >> 6) & 0x3F)  # 000 000000 xxxxxx 000000
            u8[3] = 0x80  # 10 xxxxxx
            u8[3] = u8[3] | (value & 0x3F)  # 000 000000 000000 xxxxxx
            pass
        elif value <= 0x7FFFFFF:
            # 5 bytes utf-8
            u8 = bytearray([0]*5)
            u8[0] = 0xF8  # 111110 xx
            u8[0] = u8[0] | (value >> 24)  # xx|
            u8[1] = 0x80  # 10 xxxxxx
            # 000 xxxxxx 000000 000000 000000
            u8[1] = u8[1] | ((value >> 18) & 0x3F)
            u8[2] = 0x80  # 10 xxxxxx
            # 000 000000 xxxxxx 000000 000000
            u8[2] = u8[2] | ((value >> 12) & 0x3F)
            u8[3] = 0x80  # 10 xxxxxx
            # 000 000000 000000 xxxxxx 000000
            u8[3] = u8[3] | ((value >> 6) & 0x3F)
            u8[4] = 0x80  # 10 xxxxxx
            u8[4] = u8[4] | (value & 0x3F)  # 000 000000 000000 000000 xxxxxx
            pass
        elif value <= 0x7FFFFFF:
            # 6 bytes utf-8
            u8 = bytearray([0]*6)
            u8[0] = 0xFC  # 1111110 x
            u8[0] = u8[0] | (value >> 30)  # x|
            u8[1] = 0x80  # 10 xxxxxx
            # 000 xxxxxx 000000 000000 000000 000000
            u8[1] = u8[1] | ((value >> 24) & 0x3F)
            u8[2] = 0x80  # 10 xxxxxx
            # 000 000000 xxxxxx 000000 000000 000000
            u8[2] = u8[2] | ((value >> 18) & 0x3F)
            u8[3] = 0x80  # 10 xxxxxx
            # 000 000000 000000 xxxxxx 000000 000000
            u8[3] = u8[3] | ((value >> 12) & 0x3F)
            u8[4] = 0x80  # 10 xxxxxx
            # 000 000000 000000 000000 xxxxxx 000000
            u8[4] = u8[4] | ((value >> 6) & 0x3F)
            u8[5] = 0x80  # 10 xxxxxx
            # 000 000000 000000 000000 000000 xxxxxx
            u8[5] = u8[5] | (value & 0x3F)
            pass
        else:
            # and more ...
            pass
        return u8


class GB2312():
    @staticmethod
    def is_unavailable_position(area,posi):
        '''GB2312中，不可用区域'''
        # 01-09区收录除汉字外的682(846)个字符。
        # 10-15区为空白区，没有使用。
        # 16-55区收录3755(3760)个一级汉字，按拼音排序。
        # 56-87区收录3008个二级汉字，按部首/笔画排序。
        # 88-94区为空白区，没有使用。
        # 其他中间空白区域
        if (area < 1) or (area > 87) or (area > 9 and area < 16):
            return True
        if area==2 and ((posi>=1 and posi<=16) or (posi>=67 and posi<=68) or (posi>=79 and posi<=80) or (posi>=93 and posi<=94)):
            return True
        if area==4 and posi>=84 and posi<=94:
            return True
        if area==5 and posi>=87 and posi<=94:
            return True
        if area==6 and ((posi>=25 and posi<=32) or (posi>=57 and posi<=94)):
            return True
        if area==7 and ((posi>=34 and posi<=48) or (posi>=82 and posi<=94)):
            return True
        if area==8 and ((posi>=27 and posi<=36) or (posi>=74 and posi<=94)):
            return True
        if area==9 and ((posi>=1 and posi<=3) or (posi>=80 and posi<=94)):
            return True
        if area==55 and posi>=90 and posi<=94:
            return True
        return False
    @staticmethod
    def pos2gb2312(area, posi):
        return bytes([area+0xA0, posi+0xA0])

    @staticmethod
    def gb23122pos(byts):
        return (byts[0]-0XA0, byts[1]-0XA0)

    @staticmethod
    def ascii2gb2312(ascii_value):
        # 非字母符号，使用空格代替
        if ascii_value < b"!"[0] or ascii_value > b"~"[0]:
            area = 1
            pos = 1
        elif ascii_value == b"~"[0]:
            area = 1
            pos = 11
        else:
            area = 3
            pos = ascii_value - b"!"[0] + 1
        return GB2312.pos2gb2312(area, pos)

    @staticmethod
    def gb23122ascii(byts):
        area, posi = GB2312.gb23122pos(byts)
        if area == 1 and posi == 11:
            return b"~"[0]
        if area == 3 and posi >= 1 and posi <= 93:
            return posi + b"!"[0] - 1
        return b" "[0]

    @staticmethod
    def all_available_pos():
        poses = []
        for area in range(1, 94+1):
            for posi in range(1, 94+1):
                if GB2312.is_unavailable_position(area, posi):
                    continue
                poses.append((area, posi))
        return poses

    @staticmethod
    def gb2312_in_available_pos(byts):
        area, posi = GB2312.gb23122pos(byts)
        if GB2312.is_unavailable_position(area, posi):
            return False
        return True

    @staticmethod
    def pos2available_pos(area, posi):
        '''快速将区位码转换成绝对位置，生成字库用'''
        if posi < 1 or posi > 94:
            return -1
        if (area < 1) or (area > 87) or (area > 9 and area < 16):
            return -1
        # 1~9区
        if area >= 1 and area <= 9:
            return (area-1)*94 + (posi-1)
        # 16~87区
        if area >= 16 and area <= 87:
            return 846 + (area-16)*94 + (posi-1)

    @staticmethod
    def available_pos2pos(a_pos):
        '''快速将绝对位置转换成区位码，生成字库用'''
        if a_pos >= 0 and a_pos < 846:
            return (a_pos//94+1, a_pos % 94+1)
        elif a_pos >= 846 and a_pos < 7614:
            return ((a_pos-846)//94+16, a_pos % 94+1)
        return (0, 0)
