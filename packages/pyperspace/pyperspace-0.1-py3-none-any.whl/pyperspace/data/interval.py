from bisect import bisect_left, insort_left, bisect_right
from typing import Any, Optional, Set, Iterable, Hashable

class IntervalNode:
    __slots__ = ('time', 'values')

    def __init__(self, time: int, values: Optional[Set[Any]] = None):
        self.time = time
        self.values = values

    def __str__(self) -> str:
        return f"({self.time}: {self.values})"

    def __repr__(self) -> str:
        return str(self)

    def __lt__(self, n) -> bool:
        return self.time < n.time

class IntervalMap:
    def __init__(self):
        self._data = [] # IntervalNode

    def values(self) -> Iterable[Any]:
        for item in self._data:
            yield from item.values

    def remove(self, begin_time: int, end_time: int, value: Hashable) -> None:
        _data = self._data
        b_idx = bisect_left(_data, IntervalNode(begin_time))
        e_idx = bisect_right(_data, IntervalNode(end_time))
        for node in _data[b_idx:e_idx]:
            node.values.remove(value)

    def insert(self, begin_time: int, end_time: int, value: Hashable) -> None:
        _data = self._data
        b_idx = bisect_left(_data, IntervalNode(begin_time))
        e_idx = bisect_right(_data, IntervalNode(end_time))
        for v in _data[b_idx:e_idx]:
            v.values.add(value)
        if e_idx == 0 or end_time > _data[e_idx-1].time:
            values = set([value])
            left = _data[e_idx].values if 0 <= e_idx < len(_data) else set()
            right = _data[e_idx-1].values if 0 <= e_idx-1 < len(_data) else set()
            values.update(left & right)
            _data.insert(e_idx, IntervalNode(end_time, values))
        if begin_time < _data[b_idx].time:
            values = set([value])
            left = _data[b_idx].values if 0 <= b_idx < len(_data) else set()
            right = _data[b_idx-1].values if 0 <= b_idx-1 < len(_data) else set()
            values.update(left & right)
            _data.insert(b_idx, IntervalNode(begin_time, values))

    def __getitem__(self, key) -> Iterable[Any]:
        _data = self._data
        if isinstance(key, slice):
            b_idx, e_idx = bisect_left(_data, IntervalNode(key.start)), bisect_left(_data, IntervalNode(key.stop))
            res = set([])
            for e in _data[b_idx:e_idx+1]:
                res.update(e.values)
            return iter(res)
        else:
            idx = bisect_left(_data, IntervalNode(key))
            left = _data[idx-1].values if 0 <= idx-1 < len(_data) else set()
            right = _data[idx].values if 0 <= idx < len(_data) else set()
            return iter(left & right)

    def __iter__(self) -> Iterable[IntervalNode]:
        return iter(self._data)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        s = ", ".join(str(i) for i in self._data)
        return f"IntervalMap([{s}])"
