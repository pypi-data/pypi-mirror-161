from .map import RangeMap

from pyperspace.protocol.dataset_ipc import _entry_unpack_from, _entry_size

from typing import Iterable, Iterator
from heapq import heappop, heappush

class Entry:
    __slots__ = ('time', 'data')
    def __init__(self, time: int, data: bytes):
        self.time = time
        self.data = data

    def __lt__(self, e) -> bool:
        return self.time < e.time
    
    def __le__(self, e) -> bool:
        return self.time <= e.time

    def __eq__(self, e) -> bool:
        return self.time == e.time

    def __str__(self) -> str:
        return f"Entry(time={self.time},data={self.data})"

    def __repr__(self) -> str:
        return str(self)


class RawEntry:
    __slots__ = ('time', 'entry_len', 'raw_data', 'deleted')
    def __init__(self, raw_data: bytes):
        self.time, self.entry_len = _entry_unpack_from(raw_data, 0)
        self.deleted = False
        self.raw_data = raw_data

    @property
    def data(self) -> bytes:
        return self.raw_data[_entry_size:_entry_size+self.entry_len]

    def __lt__(self, e) -> bool:
        return self.time < e.time
    
    def __le__(self, e) -> bool:
        return self.time <= e.time

    def __eq__(self, e) -> bool:
        return self.time == e.time

    def __str__(self) -> str:
        return f"RawEntry(time={self.time},data={self.data},header={self.header})"

    def __repr__(self) -> str:
        return str(self)


class EntryNode:
    __slots__ = ('entry', 'iter')
    def __init__(self, e: Entry, rd: Iterable[Entry]):
        self.entry = e
        self.iter = rd

    def __lt__(self, n) -> bool:
        return self.entry < n.entry


def sort_readers(rd: Iterable[Iterable[Entry]]) -> Iterable[Entry]:
    if len(rd) == 1: yield from rd[0]
    pq = []
    for r in rd:
        try:
            heappush(pq, EntryNode(next(r), r))
        except StopIteration:
            pass
    while pq:
        e = heappop(pq)
        yield e.entry
        try:
            _iter = e.iter
            heappush(pq, EntryNode(next(_iter), _iter))
        except StopIteration:
            pass

def filter_deleted(data: Iterable[RawEntry]) -> Iterable[RawEntry]:
    return filter(lambda e: not e.deleted, data)

def subtract(data: Iterator[Entry], exclude: RangeMap) -> Iterable[Entry]:
    iter_data = iter(data)
    for t1, t2 in exclude:
        # Before filter
        for e in iter_data:
            if e.time < t1:
                yield e
            else:
                break
        # Skip filter data
        for e in iter_data:
            if e.time > t2:
                yield e
                break
    # Remainder (beyond filter)
    yield from iter_data
