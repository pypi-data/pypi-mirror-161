from typing import Iterable, Any

def count(g: Iterable[Any]) -> int:
    return sum(1 for _ in g)
