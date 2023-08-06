import mmap

class MMapFile:
    def __init__(self, fn: str, buf_sz: int = 4096):
        self._fd = open(fn, 'w+b')
        self._buf_sz = buf_sz
        self._offset = 0
        self._next = 0
        self._fileno = self._fd.fileno()
        self._max_fsz = self._fd.seek(0, 2)
        self._mem = self._mmap(0)

    def fileno(self) -> int:
        return self._fd.fileno()

    def close(self) -> None:
        self._mem.close()
        self._fd.truncate((self._buf_sz*self._offset)+self._next)
        self._fd.close()

    def read(self, size: int) -> bytes:
        # TODO: check _max_fsz
        _buf_sz = self._buf_sz
        _next = self._next
        _mem = self._mem
        _offset = self._offset
        res = bytes(size)
        i = 0
        while i != size:
            max_to_copy = min(_buf_sz - _next, size-i)
            res[i:i+max_to_copy] = _mem[_next:_next+max_to_copy]
            _next += max_to_copy
            i += max_to_copy
            if _next == _buf_sz:
                _next = 0
                _offset += 1

        return res[:i]

    def write(self, data: bytes) -> int:
        i = 0
        _buf_sz = self._buf_sz
        _next = self._next
        _mem = self._mem
        _offset = self._offset
        while i != len(data):
            max_to_copy = min(_buf_sz - _next, len(data)-i)
            _mem[_next:_next+max_to_copy] = data[i:i+max_to_copy]
            _next += max_to_copy
            i += max_to_copy
            if _next == _buf_sz:
                _next = 0
                _offset += 1
                _mem.close()
                _mem = self._mmap(_offset)
                self._offset = _offset
                self._mem = _mem

        self._next = _next
        return len(data)

    def flush(self) -> None:
        self._mem.flush()

    def _mmap(self, offset: int) -> any:
        _buf_sz = self._buf_sz
        o = offset*_buf_sz
        if o+_buf_sz > self._max_fsz:
            self._fd.truncate(o+_buf_sz)
            self._max_fsz = o+_buf_sz
        return mmap.mmap(self._fileno, _buf_sz, offset=o)
