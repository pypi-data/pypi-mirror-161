from .memtable import MemTable
from .lsm import LSMFileMerger 

from pyperspace.data import Entry, RangeMap, subtract, RawEntry, sort_readers
from pyperspace.io import WriteAheadLog
from typing import Iterable
import os
import threading

class SelectMap:
    __slots__ = ('_map', '_map_values')
    def __init__(self):
        self._map = {}
        self._map_values = self._map.values

    def add(self, key: str, m: MemTable) -> None:
        self._map[key] = m

    def drop(self, key: str) -> None:
        del self._map[key]
    
    def find_range(self, begin_time: int, end_time: int) -> Iterable[Entry]:
        return sort_readers([m.find_range(begin_time, end_time) for m in self._map_values()])

    def find_all(self) -> Iterable[Entry]:
        return sort_readers([m.find_all() for m in self._map_values()])

class DataSet:
    __slots__ = ('_max_entries', '_mtbl', '_wal', '_next_wal', '_dir', '_select', '_select_range', '_select_all', '_mut_lock')
    def __init__(self, data_dir: str, max_entries: int = 0):
        self._max_entries = max_entries

        self._mut_lock = threading.Lock()

        mtbl = MemTable()
        self._mtbl = mtbl
        self._next_wal = 0

        self._dir = data_dir
        os.makedirs(data_dir, 0o744, exist_ok=True)

        select = SelectMap()
        self._select = select
        self._select_range = select.find_range
        self._select_all = select.find_all

        self._setup_wal()

    def _setup_wal(self) -> None:
        wal_file = None
        for fn in os.listdir(self._dir):
            if fn.startswith("insert_") and fn.endswith(".wal"):
                if wal_file is not None:
                    raise IOError(f"multiple insert write-ahead logs found in \"{self._dir}\"")
                wal_file = os.path.join(self._dir, fn)
        wal = WriteAheadLog(wal_file or self._next_wal_file())
        self._mtbl.load_from_wal(wal)
        self._wal = wal
        self._select.add(wal.filename, self._mtbl)

    def drop(self) -> None:
        self.close()
        os.removedirs(self._dir)

    @property
    def wal_file(self) -> str:
        return self._wal.filename

    def kill(self, wal_file: str) -> None:
        self._select.drop(wal_file)

    def freeze(self) -> str:
        with self._mut_lock:
            fn = self._wal.filename
            self._wal.close()
            self._wal = WriteAheadLog(self._next_wal_file())

            self._mtbl = MemTable()
            self._select.add(self._wal.filename, self._mtbl)
            return fn
        
    def _next_wal_file(self) -> str:
        _next_wal = self._next_wal
        _dir = self._dir
        
        fn = os.path.join(_dir, f"insert_{_next_wal:06d}.wal")
        while os.path.isfile(fn):
            _next_wal += 1
            fn = os.path.join(_dir, f"insert_{_next_wal:06d}.wal")

        self._next_wal = _next_wal+1
        return fn

    def close(self) -> None:
        self._wal.close()

    def delete(self, begin_time: int, end_time: int, flush: bool = False) -> None:
        with self._mut_lock:
            self._wal.write_delete(begin_time, end_time, flush)
            self._mtbl.delete(begin_time, end_time)
    
    def insert_raw(self, e: RawEntry, flush: bool = False) -> bool:
        with self._mut_lock:
            self._wal.write_insert(e, flush)
            self._mtbl.insert_raw(e)
            _mtbl_count = self._mtbl.count
        _max_entries = self._max_entries
        # TODO: freeze after max count exceeded
        return _max_entries == 0 or _mtbl_count < _max_entries

    def flush(self) -> None:
        self._wal.flush()
    
    def find_range(self, begin_time: int, end_time: int) -> Iterable[Entry]:
        return self._select_range(begin_time, end_time)

    def find_all(self) -> Iterable[Entry]:
        return self._select_all()

    @property
    def count(self) -> int:
        return self._mtbl.count
