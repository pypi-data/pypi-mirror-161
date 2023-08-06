from pyperspace.data import count
from typing import Any

def select_count(rd: Any, begin_time: int, end_time: int) -> int:
    return count(rd.find_range(begin_time, end_time))
