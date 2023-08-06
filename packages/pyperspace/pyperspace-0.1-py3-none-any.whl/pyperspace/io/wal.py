from pyperspace.data import Entry, RawEntry

import fcntl
import struct
import os
from typing import Tuple, Callable, Any

import mmap

_hdr = struct.Struct('lH')
_hdr_pack = _hdr.pack
_hdr_unpack = _hdr.unpack
_hdr_unpack_from = _hdr.unpack_from
_hdr_size = _hdr.size

_delete_entry = struct.Struct('ll')
_delete_entry_size = _delete_entry.size
_delete_entry_pack = _delete_entry.pack
_delete_entry_unpack_from = _delete_entry.unpack_from

WAL_DELETE = 1
WAL_INSERT = 2

B_WAL_DELETE = b'\x01'
B_WAL_INSERT = b'\x02'

class FastWriteAheadLog:
    def __init__(self, filename: str):
        self._fd = open(filename, "r+b")
        size = self._fd.seek(0, 2)
        self._mem = mmap.mmap(self._fd.fileno(), size)
        self._idx = 0
        self._max = size

    @property
    def eof(self) -> bool:
        return self._idx >= self._max
    
    def _read_insert(self, mem: mmap.mmap, idx: int) -> RawEntry:
        timestamp, data_len = _hdr_unpack_from(mem, idx)
        self._idx = idx + _hdr_size + data_len
        return RawEntry(mem[idx:idx+_hdr_size+data_len])
    
    def read_one(self) -> Tuple[int, Any]:
        _idx = self._idx
        _mem = self._mem

        entry_type = _mem[_idx]
        if entry_type == WAL_INSERT:
            return entry_type, self._read_insert(_mem, _idx+1)
        elif entry_type == WAL_DELETE:
            self._idx = _idx + 1 + _delete_entry_size
            return entry_type, _delete_entry_unpack_from(_mem, _idx+1)
        else:
            raise IOError(f"invalid entry type (type_id={entry_type})")

    def close(self) -> None:
        self._mem.close()
        self._fd.close()


class WriteAheadLog:
    __slots__ = ('_fd', '_fd_peek', '_fd_read', '_fd_write', '_filename', 'flush')
    def __init__(self, filename: str):
        self._fd = open(filename, 'a+b')
        self._fd_peek = self._fd.peek
        self._fd_read = self._fd.read
        self._fd_write = self._fd.write
        self._filename = filename
        self.flush = self._fd.flush
        self._fd.seek(0)
        #try:
        #    fcntl.lockf(self._fd.fileno(), fcntl.LOCK_EX)
        #except:
        #    print(f"******** RESOURCE DEADLOCK: {filename}")
        #    raise

    @property
    def filename(self) -> str:
        return self._filename

    def unlink(self) -> None:
        self.close()
        try:
            os.unlink(self._filename)
        except:
            pass

    def close(self) -> None:
        self._fd.close()

    @property
    def eof(self) -> bool:
        return len(self._fd_peek()) == 0

    def _read_insert(self, read_func: Callable[[int], bytes]) -> RawEntry:
        hdr_data = read_func(_hdr_size)
        if len(hdr_data) != _hdr_size:
            raise EOFError(f"end-of-file reached (read {len(hdr_data)} of {_hdr_size} bytes)")
        _, entry_len = _hdr_unpack_from(hdr_data, 0)
        entry_data = read_func(entry_len)
        if len(entry_data) != entry_len:
            raise EOFError(f"end-of-file reached (read {len(entry_data)} of {entry_len} bytes)")
        return RawEntry(hdr_data + entry_data)

    def read_one(self) -> Tuple[int, Any]:
        _fd_read = self._fd_read
        entry_type = _fd_read(1)
        if entry_type == B_WAL_INSERT:
            return WAL_INSERT, self._read_insert(_fd_read)
        elif entry_type == B_WAL_DELETE:
            return WAL_DELETE, _delete_entry_unpack_from(_fd_read(_delete_entry_size), 0)
        else:
            raise IOError(f"invalid entry type (type_id={int(entry_type[0])})")

    def write_delete(self, begin_time: int, end_time: int, flush: bool) -> None:
        buf_size = 1 + _delete_entry_size
        bytes_written = self._fd_write(B_WAL_DELETE + _delete_entry_pack(begin_time, end_time))
        if bytes_written != buf_size:
            raise IOError(f"storage exhausted (wrote {bytes_written} of {buf_size} bytes)")
        if flush: self.flush()
    
    def write_insert(self, e: RawEntry, flush: bool) -> None:
        # e.raw_data includes time + data length
        raw_data = e.raw_data
        buf_size = 1 + len(raw_data)
        bytes_written = self._fd_write(B_WAL_INSERT + raw_data)
        if bytes_written != buf_size:
            raise IOError(f"storage exhausted (wrote {bytes_written} of {buf_size} bytes)")
        if flush: self.flush()

    def truncate(self) -> None:
        self._fd.truncate(0)
