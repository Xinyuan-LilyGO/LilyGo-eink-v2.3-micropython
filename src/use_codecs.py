'''
编码转换辅助文件，文件开头：|2 b"CO"|4记录的编码数量，即 文件大小=数量*(源长度+目标长度)+8|1源长度|1目标长度|
之后 |源编码|目标编码| 为一组，按照源编码从小到大排列，使用时二分搜索查找对应的编码转换
'''
try:
    from . import coding
except:
    import coding

def __bin_search_in_file(file_handle,target,start,end,s_size,t_size,buffer_size=0,buffer=None):
    if end <= start:
        # not found
        return False
    block_size = s_size + t_size
    # use buffer speedup search
    if (end - start <= buffer_size//block_size):
        if (buffer == None):
            # first time, create buffer
            file_handle.seek(start*block_size + 8) #要跳过文件头8字节
            data = file_handle.read((end-start)*block_size)
            buffer = memoryview(data)
            end = end - start
            start = 0
        center = (end + start) // 2
        pos = center * block_size
        value = int.from_bytes(buffer[pos:pos+s_size],"big")
        # print('buff',start,center,end,"0x{:X}".format(value))
    else:
        # read from file
        center = (end + start) // 2
        pos = center * (s_size + t_size) + 8 #要跳过文件头8字节
        file_handle.seek(pos)
        value = int.from_bytes(file_handle.read(s_size),"big")
        # print('file',start,end,end-start,"0x{:X}".format(value))
    # compare
    # print("0x{:X} {} {} {}".format(value,start,center,end))
    if value < target:
        return __bin_search_in_file(file_handle,target,center+1,end,s_size,t_size,buffer_size=buffer_size,buffer=buffer)
    if value > target:
        return __bin_search_in_file(file_handle,target,start,center,s_size,t_size,buffer_size=buffer_size,buffer=buffer)
    # find!
    if (end - start <= buffer_size//block_size):
        # find in buffer
        data = bytes(buffer[pos+s_size:pos+block_size])
        return data
    else:
        # find in file
        return file_handle.read(t_size)

def convert(target,codec_file,buffer_size=0):
    '''使用文件辅助转换编码。
        byts:字符的字节序列
        codec_file:编码转换文件
        buffer_size:文件读取buffer大小，可以减少文件读取次数从而加速转换
        返回转换后的字节序列或False'''
    with open(codec_file,"rb") as f:
        magic = f.read(2)
        assert magic == b"CO"
        count = int.from_bytes(f.read(4),"big")
        s_size = int.from_bytes(f.read(1),"big")
        t_size = int.from_bytes(f.read(1),"big")
        resault = __bin_search_in_file(f,target,0,count,s_size,t_size,buffer_size=buffer_size)
        return resault

def convert_u8_gb2312(byts,codec_file,buffer_size=0):
    index = 0
    res = bytearray()
    while index < len(byts):
        fb = byts[index]
        l = coding.UTF_8.u8len(fb)
        if l == 1:
            index += 1
            res.extend(coding.GB2312.ascii2gb2312(fb))
            continue
        unic = coding.UTF_8.u82unicode(byts[index:index+l])
        bs = convert(unic,codec_file,buffer_size=buffer_size)
        if not bs:
            index += l
            res.extend(coding.GB2312.ascii2gb2312(32))
            continue
        res.extend(bs)
        index += l
    return res

def __main():
    byts = convert_u8_gb2312("你好x啊aXSA+_生僻字蘃还好咯".encode("utf8"),"unicode2gb2312.codec",buffer_size=8)
    # for b in byts:
    #     print("0x{:X}".format(b),end=" ")
    # print()
    print(byts.decode('gb2312'))
    pass

if __name__ == "__main__":
    __main()