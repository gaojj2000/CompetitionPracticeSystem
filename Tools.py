# _*_ coding:utf-8 _*_

import re
import ctypes


# chinese yes -> format table
def dump(data: list):
    rows = 0
    all_string = ''
    chinese = [0] * len(data[0])
    length = [0] * len(data[0])
    assert len(set([len(r) for r in data])) == 1, print('list格式不正确！')
    for row in data:
        if rows < len(row):
            rows = len(row)
        for col in range(len(row)):
            for r in str(row[col]).split('\n'):
                if length[col] < len(r):
                    length[col] = len(r)
                if chinese[col] < len(''.join(re.findall(r'[\u4e00-\u9fa5，。！？（）【】《》]+', r))):
                    chinese[col] = len(''.join(re.findall(r'[\u4e00-\u9fa5，。！？（）【】《》]+', r)))
    length = [l + c for l, c in zip(length, chinese)]
    temp = ''
    for l in range(len(length)):
        temp += '+' + '-' * (length[l] + 2)
    all_string += temp + '+\n'
    for row in data:
        string = '|'
        for l in range(len(length)):
            string += '{: ^' + str(length[l] + 2 - len(''.join(re.findall(r'[\u4e00-\u9fa5，。！？（）【】《》]+', row[l])))) + '}|'
        all_string += string.format(*row) + '\n' + temp + '+\n'
    return all_string.strip('\n')


# make 32 length filled with 0
def get_bin(num: int) -> str:
    num = bin(num).split('b')[-1]
    string = '{:0>' + str(32) + '}'
    return string.format(num)


# c_int32 >> calc
def sign_bin_right(num: int, offset: int) -> int:
    return ctypes.c_int32(num >> offset).value


# sign calc -> same with javascript
def get_sign(te: str) -> str:
    te = len(te) > 30 and te[0:10] + te[int(len(te) / 2) - 5: int(len(te) / 2) + 5] + te[-10:] or te
    m = 320305
    pass_go = False
    s = []
    for v in range(len(te)):
        if pass_go:
            pass_go = False
            continue
        a = ord(te[v])
        if a < 128:
            s.append(a)
        else:
            if a < 2048:
                s.append(sign_bin_right(a, 6) | 192)
            else:
                if 64512 & a is 55296 and v + 1 < len(te) and 64512 & ord(te[v + 1]) is 56320:
                    v += 1
                    pass_go = True
                    a = 65536 + ((1023 & a) << 10) + (1023 & ord(te[v]))
                    s.append(sign_bin_right(a, 18) | 240)
                    s.append(sign_bin_right(a, 12) & 63 | 128)
                else:
                    s.append(sign_bin_right(a, 12) | 224)
                    s.append(sign_bin_right(a, 6) & 63 | 128)
                s.append(63 & a | 128)
    p = m
    for b in range(len(s)):
        p += s[b]
        p = ctypes.c_int32(p + ctypes.c_int32(p << 10).value).value
        p ^= int(get_bin(ctypes.c_int32(ctypes.c_uint32(p).value >> 6).value)[6:], 2)
    p = ctypes.c_int32(p + ctypes.c_int32(p << 3).value).value
    p ^= int(get_bin(ctypes.c_int32(ctypes.c_uint32(p).value >> 11).value)[11:], 2)
    p = ctypes.c_int32(p + ctypes.c_int32(p << 15).value).value
    p ^= 131321201
    p = p < 0 and (2147483647 & p) + 2147483648 or p
    p %= 1e6
    return f'{int(p)}.{int(p) ^ m}'
