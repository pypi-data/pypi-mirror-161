from ctypes import CDLL

_libc = CDLL('libc.so.6')
_write = _libc.write
_fread = _libc.fread
_fwrite = _libc.fwrite
_fopen = _libc.fopen
_fclose = _libc.fclose
_fflush = _libc.fflush
_fdatasync = _libc.fdatasync
_fileno = _libc.fileno

class CFile:
    def __init__(self, fn: str, mode: str):
        self._fd = _fopen(bytes(fn, "utf-8"), mode)

    def fileno(self) -> int:
        return _fileno(self._fd)

    def read(self, size: int) -> bytes:
        buf = ctypes.create_string_buffer(size)
        s = _fread(buf, 1, len(buf), self._fd)
        return buf.raw[0:s]

    def write(self, data: bytes) -> int:
        return _fwrite(data, 1, len(data), self._fd)

    def flush(self) -> None:
        #_fdatasync(self._fd)
        _fflush(self._fd)

    def close(self) -> None:
        _fclose(self._fd)
