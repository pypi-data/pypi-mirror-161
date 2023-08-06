from pyperspace.data import RangeMap
from pyperspace.io import WriteAheadLog, WAL_DELETE

import os

class DeletionMap:
    def __init__(self, wal_path: str):
        self._deletes = RangeMap()
        self._path = wal_path
        self._counter = 0
        wal_file = None
        for fn in os.listdir(wal_path):
            if fn.startswith("delete_") and fn.endswith(".wal"):
                if wal_file is not None:
                    raise IOError(f"multiple deletion write-ahead logs in \"{wal_path}\"")
                wal_file = os.path.join(wal_path, fn)
        wal = WriteAheadLog(wal_file or os.path.join(wal_path, f"delete_{self._counter:06d}.wal"))
        self._wal = wal
        while not wal.eof:
            e_type, e_data = wal.read_one()
            if e_type == WAL_DELETE:
                self._deletes.insert(*e_data)

    @property
    def empty(self) -> bool:
        return self._deletes.empty

    @property
    def filename(self) -> str:
        return self._wal.filename

    def reset(self) -> None:
        self._wal.close()
        self._deletes = RangeMap()
        _counter = self._counter
        _path = self._path
        fn = os.path.join(_path, f"delete_{_counter:06d}.wal")
        while os.path.isfile(fn):
            _counter += 1
            fn = os.path.join(_path, f"delete_{_counter:06d}.wal")
        self._wal = WriteAheadLog(fn)
        self._counter = _counter

    @property
    def map(self) -> RangeMap:
        return self._deletes

    def close(self) -> None:
        self._wal.close()

    def insert(self, begin_time: int, end_time: int, flush: bool) -> None:
        self._wal.write_delete(begin_time, end_time, flush)
        self._deletes.insert(begin_time, end_time)

    def flush(self) -> None:
        self._wal.flush()
