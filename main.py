import numpy as np
from typing import Dict, List


MASK = [0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F, 0xFF]


class CompressedBuffer():
    def __init__(self, N: int):
        """
        Implements a compression buffer of size N bytes.
        """
        self.buf = np.zeros(N, dtype=np.uint8)
        self.N = N
        self.byte_ptr = 0
        self.bit_ptr = 0

    def reset(self):
        self.byte_ptr = 0
        self.bit_ptr = 0

    def __str__(self):
        pl = [f"{i:02x}" for i in self.buf]
        return f"byte-ptr:{self.byte_ptr}, bit-ptr: {self.bit_ptr}, buff:" + "".join(pl[:self.byte_ptr + 1])

    def add(self, x, nbits):
        """
        Adds value x of size nbits to the buffer.
        """
        while nbits:
            shift_by = min(nbits, 8 - self.bit_ptr)
            assert shift_by > 0
            y = np.uint8(x & MASK[shift_by - 1])
            y <<= self.bit_ptr
            self.buf[self.byte_ptr] |= y
            nbits -= shift_by
            x >>= shift_by

            if (8 - self.bit_ptr) > shift_by:
                self.bit_ptr += shift_by
            else:
                self.bit_ptr = 0
                self.byte_ptr += 1

    def add_with_sign(self, x, nbits):
        if x < 0:
            self.add(1, 1)
        else:
            self.add(0, 1)
        self.add(abs(x), nbits)


class DecompressApp():
    def __init__(self, buf, size, vars: List[Dict]):
        self.buf = buf
        self.vars = vars
        self.byte_ptr = 0
        self.bit_ptr = 0
        self.size = size

    def _read(self, nbits, signed=False):
        sign = 0
        if signed:
            sign = (self.buf[self.byte_ptr] >> self.bit_ptr) & 0x1
            if self.bit_ptr < 7:
                self.bit_ptr += 1
            else:
                self.bit_ptr = 0
                self.byte_ptr += 1
        res = np.int64(0)
        shift_by = 0
        while nbits:
            x = self.buf[self.byte_ptr]
            x >>= self.bit_ptr
            masked_bits = min(8 - self.bit_ptr, nbits)
            res |= (x & MASK[masked_bits - 1]) << shift_by
            shift_by += masked_bits
            nbits -= masked_bits
            if (8 - self.bit_ptr) > masked_bits:
                self.bit_ptr += masked_bits
            else:
                self.bit_ptr = 0
                self.byte_ptr += 1
        return -res if sign else res

    def decompress(self):
        vars_list = []
        while self.byte_ptr < self.size:
            _vars = []
            for v in self.vars:
                signed, bit_size = v['signed'], v['nbits']
                _vars.append(self._read(bit_size, signed))
            vars_list.append(_vars)
        return vars_list


if __name__ == "__main__":

    # define vars to store in the buffer
    vars = [
        {'value': np.int32(-1730), 'nbits': 14, 'signed': True},
        {'value': np.int32(65), 'nbits': 7, 'signed': False},
        {'value': np.int32(355), 'nbits': 17, 'signed': False},
        {'value': np.int32(1425), 'nbits': 12, 'signed': False},
    ]

    print(f"Ready to compress vars: {[v['value'] for v in vars]}")

    # Add vars to buffer
    cb = CompressedBuffer(20)

    for v in vars:
        if v['signed']:
            cb.add_with_sign(v['value'], v['nbits'])
        else:
            cb.add(v['value'], v['nbits'])

    print(f"Compressed buffer: {cb}")

    # add a second batch of variables
    for v in vars:
        v['value'] = np.int32(v['value'] // 2)

    print(f"Ready to compress vars: {[v['value'] for v in vars]}")

    for v in vars:
        if v['signed']:
            cb.add_with_sign(v['value'], v['nbits'])
        else:
            cb.add(v['value'], v['nbits'])

    print(f"Compressed buffer: {cb}")

    # The application needs to know the bit-size and whether
    # the value is signed or not
    vars_info = [{'nbits': v['nbits'], 'signed': v['signed']} for v in vars]
    d = DecompressApp(cb.buf, cb.byte_ptr, vars_info)
    dv = d.decompress()
    print(f"Decompressed vars: {dv}")
