import mmap
import io
import struct
import pickle
from typing import Tuple
import time

"""
mmap-based interprocess ring buffer (Single Producer, Single Consumer)

File Format (NN file size):
  0x00 .. .. .. .. .. .. .. ..   .. .. .. .. .. .. .. ..  (buffer -- empty or occupied)
  .... .. .. .. .. .. .. .. ..   .. .. .. .. .. .. .. .. 
  .... RR RR RR RR RR RR RR RR   WW WW WW WW WW WW WW WW  (reader pointer, writer pointer)
  0xNN

  - buffer          -- contains any linearly-organized ring buffer data (or garbage if reader/writer pointers not setup)
  - reader pointer  -- file offset of reader pointer (points at next element to read)
  - writer pointer  -- file offset of writer pointer (points at next element to write)
"""

class RingBuffer:
    STATE_WAIT = 0
    STATE_READY = 1
    STATE_CHECK = 2

    def open_reader(self, fn: str, size: int) -> None:
        self._fd = io.open(fn, 'r+b')
        if self._fd.seek(0, 2) != size:
            self._fd.truncate(size)
        self._mem = mmap.mmap(self._fd.fileno(), size)
        self._size = size - 16 - 4 - 4

    def open_writer(self, fn: str, size: int) -> None:
        self._fd = io.open(fn, 'w+b')
        if self._fd.seek(0, 2) != size:
            self._fd.truncate(size)
        self._mem = mmap.mmap(self._fd.fileno(), size)
        self._size = size - 16 - 4 - 4
        self._reader = 0
        self._writer = 0
        self._rd_state = RingBuffer.STATE_WAIT
        self._wr_state = RingBuffer.STATE_READY

    @property
    def _reader(self) -> int:
        return struct.unpack_from('L', self._mem, self._size)[0]

    @_reader.setter
    def _reader(self, value: int) -> None:
        struct.pack_into('L', self._mem, self._size, value)

    @property
    def _writer(self) -> int:
        return struct.unpack_from('L', self._mem, self._size+8)[0]

    @_writer.setter
    def _writer(self, value: int) -> None:
        struct.pack_into('L', self._mem, self._size+8, value)
    
    @property
    def _rd_state(self) -> int:
        return self._mem[self._size+16]

    @_rd_state.setter
    def _rd_state(self, value: int) -> None:
        self._mem[self._size+16] = value
    
    @property
    def _wr_state(self) -> int:
        return self._mem[self._size+20]

    @_wr_state.setter
    def _wr_state(self, value: int) -> None:
        self._mem[self._size+20] = value

    def _read_available(self) -> int:
        d = self._writer - self._reader
        if d >= 0:
            return d
        else:
            return d+(self._size)

    def _write_available(self) -> int:
        d = self._reader - self._writer
        if d > 0:
            return d-1
        else:
            return d+(self._size)-1

    def _read_commit(self, size: int) -> None:
        self._wr_state = RingBuffer.STATE_WAIT
        p = self._reader + size
        if p >= self._size:
            self._reader = (p - self._size)
        else:
            self._reader = p
        self._wr_state = RingBuffer.STATE_READY
    
    def _write_commit(self, size: int) -> None:
        self._rd_state = RingBuffer.STATE_WAIT
        p = self._writer + size
        if p >= self._size:
            self._writer = (p - self._size)
        else:
            self._writer = p
        self._rd_state = RingBuffer.STATE_READY

    def _read(self, p: int, dst: bytes) -> None:
        if p >= self._size:
            p -= self._size
        if len(dst)+p <= self._size:
            # Copy entire segment
            dst[:] = self._mem[p:p+len(dst)]
        else:
            # Copy to end, copy beginning
            e = self._size
            dst[0:(e-p)] = self._mem[p:e]
            r = len(dst) - (e-p)
            dst[(e-p):] = self._mem[:r]
    
    def _write(self, p: int, src: bytes) -> None:
        if p >= self._size:
            p -= self._size
        if len(src)+p <= self._size:
            # Copy entire segment
            self._mem[p:p+len(src)] = src[:]
        else:
            # Copy to end, copy beginning
            e = self._size
            self._mem[p:e] = src[0:(e-p)]
            r = len(src) - (e-p)
            self._mem[:r] = src[(e-p):]
    
    def _read_spinwait(self, size: int) -> None:
        backoff = 0.0001
        while True:
            if self._rd_state != RingBuffer.STATE_WAIT:
                if self._read_available() >= size:
                    return
                self._rd_state = RingBuffer.STATE_WAIT
            time.sleep(backoff)
            if backoff < 0.1: backoff *= 10

    def _write_spinwait(self, size: int) -> None:
        backoff = 0.0001
        while True:
            if self._wr_state != RingBuffer.STATE_WAIT:
                if self._write_available() >= size:
                    return
                self._wr_state = RingBuffer.STATE_WAIT
            time.sleep(backoff)
            if backoff < 0.1: backoff *= 10
    
    def _put(self, data: bytes) -> None:
        if len(data) >= self._size:
            raise RuntimeError(f"cannot put() {len(data)} bytes into a {self._size}-byte ring buffer")
        buf = struct.pack('I', len(data))
        needed = len(data) + len(buf)
        self._write_spinwait(needed)

        p = self._writer
        self._write(p, buf)
        self._write(p+4, data)
        self._write_commit(needed)

    def _get(self) -> bytes:
        buf = bytearray(4)
        self._read_spinwait(len(buf))
        
        p = self._reader
        self._read(p, buf)

        datalen, = struct.unpack_from('I', buf, 0)
        if datalen >= self._size:
            raise RuntimeError(f"cannot get() {datalen} bytes out of a {self._size}-byte ring buffer")
        
        buf = bytearray(datalen)
        self._read_spinwait(len(buf))
        
        self._read(p+4, buf)
        self._read_commit(len(buf)+4)
        return bytes(buf)

    def put_raw(self, value: bytes) -> None:
        self._put(value)

    def get_raw(self) -> bytes:
        return self._get()

    def put(self, value: any) -> None:
        self._put(pickle.dumps(value))

    def get(self) -> any:
        e = self._get()
        try:
            return pickle.loads(e)
        except:
            raise IOError(f"bad entry -- {len(e)} bytes")
