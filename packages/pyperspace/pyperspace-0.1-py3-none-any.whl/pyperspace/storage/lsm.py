from .select import select_count
from .memtable import MemTable
from pyperspace.data import Entry, sort_readers, RangeMap, subtract, RawEntry
from pyperspace.io import FileStorage, open_random
from pyperspace.protocol.dataset_ipc import _entry_pack, _entry_pack_into, _entry_unpack, _entry_size

import fcntl
import struct
import os
from collections import namedtuple
from typing import Iterable, Tuple, Callable, List


LSMFileHeader = namedtuple('LSMFileHeader', ['num_entries', 'begin_time', 'end_time'])
_lsm_header = struct.Struct('Lqq')
_index_header = struct.Struct('qL')
_index_header_size = _index_header.size
_pack_index_header = _index_header.pack
_unpack_index_header = _index_header.unpack
    
def persist(write_func: Callable[[bytes], int], data: bytes) -> int:
    bytes_written = write_func(data)
    if bytes_written != len(data):
        raise IOError(f"storage full (wrote {bytes_written} of {len(data)} bytes)")
    return bytes_written


class LSMFileReader(FileStorage):
    def __init__(self, fn: str):
        super().__init__(open_random(fn, "rb"))
        # Shared lock the file to prevent writing / deletion
        fcntl.lockf(self._fd.fileno(), fcntl.LOCK_SH)
        self._read_header()
        self._entry_start_offset = _lsm_header.size + (self.header.num_entries*_index_header_size)

    def __iter__(self) -> Iterable[Entry]:
        return self.find_all()

    def _iter_from_offset(self, offset: int, start_index: int, end_index: int) -> Iterable[Entry]:
        _pread = self._pread
        for _ in range(start_index, end_index+1):
            e_hdr = _pread(_entry_size, offset)
            time, e_size = _entry_unpack(e_hdr)
            if e_size > 300: raise IOError(f"bad data (size={e_size}, fn={self._fd.name})")
            e_data = _pread(e_size, offset+_entry_size)
            offset += _entry_size + e_size
            # TODO: replace with RawEntry
            yield Entry(time, e_data)
            #yield RawEntry(e_hdr + e_data)

    # TODO: merge FileStorage

    def find_all(self) -> Iterable[Entry]:
        return self._iter_from_offset(self._entry_start_offset, 0, self._header.num_entries-1)

    def find_range(self, begin_time: int, end_time: int) -> Iterable[Entry]:
        if begin_time <= self.header.end_time:
            # TODO: use LSMIndexListView wrapper
            offset, begin_idx = self._find_index_offset(begin_time)
            _, end_idx = self._find_index_offset(end_time)
            yield from self._iter_from_offset(offset, begin_idx, end_idx)

    @property
    def header(self) -> LSMFileHeader:
        return self._header

    def _read_header(self) -> None:
        data = self._pread(_lsm_header.size, 0)
        self._header = LSMFileHeader(*_lsm_header.unpack(data))

    def _find_index_offset(self, time: int) -> Tuple[int, int]:
        idx_start = _lsm_header.size
        lo = 0
        hi = self.header.num_entries
        f_offset = None
        _pread = self._pread
        while lo != hi:
            mid = (lo+hi)//2
            data = _pread(_index_header_size, (idx_start + (_index_header_size*mid)))
            i_time, f_offset = _unpack_index_header(data)
            if i_time > time:
                hi = mid
            else:
                lo = mid+1
        return f_offset, mid


class LSMFileWriter:
    """
    LSM File Format
    ---------------
      0x00  -- Header (size information)
            -- Index Data
                -- (Timestamp, File Offset)
            -- Entry Heap
                -- (Timestamp, Entry Length, Entry...)
    """
    def __init__(self, filename: str, validate: bool = False):
        self._fd = open(filename, 'wb')
        self._fd_write = self._fd.write
        self._fd_flush = self._fd.flush
        fcntl.lockf(self._fd.fileno(), fcntl.LOCK_EX)
        self._offset = 0
        self._hdr_written = False
        self._num_entries = 0
        self._indices_written = 0
        self._entries_written = 0
        self._validate = validate

    def close(self) -> None:
        fn = self._fd.name
        self._fd.close()
        if self._validate:
            rd = LSMFileReader(fn)
            last_time = -(1 << 64)
            try:
                for e in rd.find_all():
                    if e.time < last_time:
                        raise IOError(f"entries out of order (prev={last_time}, curr={e.time})")
                    last_time = e.time
            finally:
                rd.close()

        if self._indices_written != self._num_entries: raise IOError(f"{self._indices_written} / {self._num_entries} indices written")
        if self._entries_written != self._num_entries: raise IOError(f"{self._entries_written} / {self._num_entries} entries written")

    def flush(self) -> None:
        self._fd_flush()

    def write_header(self, num_entries: int, begin_time: int, end_time: int) -> None:
        if self._hdr_written: raise IOError("header already written")
        data = _lsm_header.pack(num_entries, begin_time, end_time)
        # Data offset = header + index section
        self._offset = persist(self._fd_write, data) + (num_entries * _index_header_size)
        self._hdr_written = True
        self._num_entries = num_entries

    def write_index(self, time: int, entry_size: int) -> None:
        _offset = self._offset
        persist(self._fd_write, _pack_index_header(time, _offset))

        # Move theoretical offset ahead
        self._offset = _offset + _entry_size+entry_size
        self._indices_written += 1

    def write_entry(self, time: int, data: bytes) -> None:
        buf = bytearray(_entry_size+len(data))
        _entry_pack_into(buf, 0, time, len(data))
        buf[_entry_size:] = data[:]
        persist(self._fd_write, buf)
        self._entries_written += 1


class LSMFileMerger:
    def __init__(self, output_fn: str):
        self._mem_tables = []
        self._lsm_files = []
        self._output_fn = output_fn
        self._count = 0
        self._begin_time = None
        self._end_time = None
        self._deletes = RangeMap()
        self._merge = False

    def add_memtable(self, mt: MemTable) -> None:
        self._count += mt.count
        if self._begin_time is None or mt.begin_time < self._begin_time:
            self._begin_time = mt.begin_time
        if self._end_time is None or mt.end_time > self._end_time:
            self._end_time = mt.end_time

        self._mem_tables.append(mt)

    def add_lsm_file(self, fn: str) -> None:
        self._lsm_files.append(fn)

    def add_deletion_range(self, r: RangeMap) -> None:
        self._deletes.merge(r)

    def _all_readers(self, readers: List[LSMFileReader]) -> Iterable[Entry]:
        return subtract(sort_readers([iter(m) for m in self._mem_tables] + [iter(rd) for rd in readers]), self._deletes)

    def _get_count(self, readers: List[LSMFileReader], total_count: int) -> int:
        for b, e in self._deletes:
            for m in self._mem_tables:
                total_count -= select_count(m, b, e)
            for r in readers:
                total_count -= select_count(r, b, e)
        return total_count

    def merge(self, validate: bool = False) -> int:
        if self._merge: raise RuntimeError("merge already called")
        self._merge = True
        fn_pending, fn_final = f"{self._output_fn}.tmp", self._output_fn
        output = LSMFileWriter(fn_pending, validate)
        readers = [LSMFileReader(fn) for fn in self._lsm_files]
        try:
            count = self._count + sum(rd.header.num_entries for rd in readers)
            b, e = [rd.header.begin_time for rd in readers], [rd.header.end_time for rd in readers]
            if self._begin_time is not None: b += [self._begin_time]
            if self._end_time is not None: e += [self._end_time]
            begin_time, end_time = min(b), max(e)
            
            total = self._get_count(readers, count)
            output.write_header(total, begin_time, end_time)
            output.flush()
            
            _output_write_index = output.write_index
            _output_write_entry = output.write_entry

            # Merge indices
            count = 0
            for e in self._all_readers(readers):
                _output_write_index(e.time, len(e.data))
                count += 1

            output.flush()
            if count != total: raise IOError(f"wrote {count} indices, expected {total}")

            # Merge entries
            count = 0
            for e in self._all_readers(readers):
                _output_write_entry(e.time, e.data)
                count += 1
            output.flush()
            if count != total: raise IOError(f"wrote {count} entries, expected {total}")

            return count
        finally:
            for i in readers: i.close()
            output.close()
            os.rename(fn_pending, fn_final)
            self._merge = False

    def close(self) -> None:
        pass
