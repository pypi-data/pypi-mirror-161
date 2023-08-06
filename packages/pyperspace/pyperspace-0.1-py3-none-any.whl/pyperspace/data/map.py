from bisect import bisect_left
from typing import Iterable, Tuple

class RangeMap:
    def __init__(self):
        self._lo = []
        self._hi = []

    def merge(self, m) -> None:
        for b, e in m:
            self.insert(b, e)

    @property
    def empty(self) -> bool:
        return len(self._lo) == 0

    def bisect_left(self, begin_time: int) -> Iterable[Tuple[int, int]]:
        _lo = self._lo
        idx = bisect_left(_lo, begin_time)
        return zip(_lo[idx:], self._hi[idx:])

    def range(self, begin_time: int, end_time: int) -> Iterable[Tuple[int, int]]:
        for b, e in self.bisect_left(begin_time):
            if b <= end_time:
                yield b, e
            else:
                break

    def __iter__(self) -> Iterable[Tuple[int, int]]:
        return zip(self._lo, self._hi)

    def insert(self, begin_time: int, end_time: int) -> None:
        _lo, _hi = self._lo, self._hi
        if _lo:
            # Find indices of begin time and end time
            i1 = bisect_left(_lo, begin_time)
            i2 = bisect_left(_hi, end_time)

            # Determine if overlap or potential overlap (offset by 1) exists
            o_l = i1-1 >= 0 and begin_time <= _hi[i1-1]+1
            o_r = i2 != len(_lo) and end_time >= _lo[i2]-1

            # Determine correct begin and end times with overlapping nodes
            t1, t2 = begin_time, end_time
            if o_l:
                t1 = min(_lo[i1-1], begin_time)
                if i1 != 0: i1 -= 1
            if o_r:
                t2 = max(_hi[i2], end_time)
                i2 += 1

            # Remove any overlapping nodes
            del _lo[i1:i2]
            del _hi[i1:i2]

            # Insert new node
            _lo.insert(i1, t1)
            _hi.insert(i1, t2)
        else:
            _lo.append(begin_time)
            _hi.append(end_time)
    
    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        s = ", ".join(f"({a}...{b})" for a, b in zip(self._lo, self._hi))
        return f"RangeMap([{s}])"
