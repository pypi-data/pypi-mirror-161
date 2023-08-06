from .storage_mgr import StorageManagerClient
from .lsm import LSMFileReader
from pyperspace.data import Entry, RangeMap, sort_readers, subtract
from typing import Iterable

class LSMDataSet:
    def __init__(self, name: str, sm_port: int):
        self._name = name
        self._sm_client = StorageManagerClient(sm_port)

    def close(self) -> None:
        self._sm_client.close()

    def delete(self, begin_time: int, end_time: int) -> None:
        self._sm_client.delete(self._name, begin_time, end_time)
    
    def find_range(self, begin_time: int, end_time: int) -> Iterable[Entry]:
        res = self._sm_client.select(self._name, begin_time, end_time)
        if res.WhichOneof('ResponseType') != 'Select':
            raise RuntimeError('find_range() returned invalid response', res)
        self._sm_client.open_files(res.Select.files)
        dr = RangeMap()
        for t in res.Select.deletion_ranges:
            dr.insert(t.begin_time, t.end_time)
        rd = [LSMFileReader(f) for f in res.Select.files]
        try:
            yield from subtract(sort_readers([r.find_range(begin_time, end_time) for r in rd]), dr)
        finally:
            for r in rd: r.close()
            self._sm_client.close_files(res.Select.files)

    def find_all(self) -> Iterable[Entry]:
        res = self._sm_client.select_all(self._name)
        if res.WhichOneof('ResponseType') != 'Select':
            raise RuntimeError('find_all() returned invalid response', res)
        self._sm_client.open_files(res.Select.files)
        dr = RangeMap()
        for t in res.Select.deletion_ranges:
            dr.insert(t.begin_time, t.end_time)
        rd = [LSMFileReader(f) for f in res.Select.files]
        try:
            yield from subtract(sort_readers([r.find_all() for r in rd]), dr)
        finally:
            for r in rd: r.close()
            self._sm_client.close_files(res.Select.files)
