from typing import Tuple, List, Iterable, Any
from bisect import bisect_left, bisect_right

class BasicTreeNode:
    __slots__ = ['values', 'leaf']
    def __init__(self, values: List[Any], leaf: bool):
        self.values = values
        self.leaf = leaf

    @property
    def depth(self) -> int:
        count = 1
        n = self
        while not n.leaf:
            count += 1
            n = n[0]
        return count

    def find_left(self, key: Any) -> Any:
        if self.leaf:
            return self.values[self.bisect_left(key)]
        else:
            idx = self.bisect_left(key)
            return self.values[idx].find_left(key)

    def split(self) -> Tuple[Any, Any]:
        _values = self.values
        _leaf = self.leaf

        p = len(_values) // 2
        return BasicTreeNode(_values[:p], _leaf), BasicTreeNode(_values[p:], _leaf)

    def pop(self, index: int) -> Any:
        return self.values.pop(index)

    def insert(self, value: Any) -> int:
        _values = self.values

        idx = bisect_right(_values, value)
        _values.insert(idx, value)
        return idx
    
    def bisect_left(self, value: Any) -> int:
        return bisect_left(self.values, value)
            
    def __iter__(self) -> Iterable[Any]:
        if self.leaf:
            for i in self.values:
                yield i
        else:
            for n in self.values:
                yield from iter(n)

    def __getitem__(self, index: int) -> Any:
        return self.values[index]

    def __lt__(self, n: Any) -> bool:
        return self.values[-1] < n.values[-1] if isinstance(n, BasicTreeNode) else self.values[-1] < n

    def __len__(self) -> int:
        return len(self.values)

class BasicTree:
    def __init__(self, cap: int):
        self._cap = cap
        self._root = BasicTreeNode([], True)
        self._count = 0

    @property
    def depth(self) -> int:
        return self._root.depth

    @property
    def first(self) -> Any:
        n = self._root
        while not n.leaf:
            n = n[0]
        return n[0]

    @property
    def last(self) -> Any:
        n = self._root
        while not n.leaf:
            n = n[-1]
        return n[-1]

    def find_left(self, key: Any) -> Any:
        return self._root.find_left(key)
    
    def insert(self, value: Any) -> Tuple[Any, Any]:
        _root = self._root
        _cap = self._cap

        # Walk down tree
        n = _root
        parents = []
        while not n.leaf:
            idx = n.bisect_left(value)
            if idx == len(n): idx -= 1
            parents.append((n, idx))
            n = n[idx]

        # Insert element
        idx = n.insert(value)
        self._count += 1

        # Find siblings
        prev_val, next_val = None, None
        if idx != 0:
            prev_val = n[idx-1]
        elif parents:
            p_node, p_idx = parents[-1]
            if p_idx != 0:
                prev_val = p_node[p_idx-1][-1]
        
        if idx+1 < len(n):
            next_val = n[idx+1]
        elif parents:
            p_node, p_idx = parents[-1]
            if p_idx+1 < len(p_node):
                next_val = p_node[p_idx+1][0]
        
        # Unwind tree stack, splitting and promoting
        while parents:
            needs_split = len(n) == _cap
            n, idx = parents.pop(-1)
            if needs_split:
                x = n.pop(idx)
                a, b = x.split()
                n.insert(a)
                n.insert(b)
        
        # Apply split + promotion to root
        if len(n) == _cap:
            a, b = _root.split()
            self._root = BasicTreeNode([a, b], False)
        return prev_val, next_val

    def __len__(self) -> int:
        return self._count

    def __iter__(self) -> Iterable[Any]:
        return iter(self._root)

    def __str__(self) -> str:
        s = ""
        for value in iter(self):
            if s: s += ", "
            s += str(value)
        return f"BasicTree([{s}])"

class FlatTree:
    __slots__ = ('_cap', '_root', '_max', '_count')
    def __init__(self, cap: int):
        self._cap = cap
        self._root = []
        self._max = []
        self._count = 0

    @property
    def first(self) -> Any:
        return self._root[0][0]

    @property
    def last(self) -> Any:
        return self._root[-1][-1]

    def find_left(self, key: Any) -> Any:
        _max = self._max
        _root = self._root
        if _root:
            n_idx = bisect_left(_max, key)
            if n_idx == len(_max): n_idx -= 1
            node = _root[n_idx]
            k_idx = bisect_left(node, key)
            return node[k_idx] if k_idx != len(node) else None
        else:
            return None

    def insert(self, value: Any) -> None:
        _root = self._root

        # Search for node and insert
        if _root:
            _max = self._max
            _cap = self._cap
            
            n_idx = bisect_left(_max, value)
            if n_idx == len(_max): n_idx -= 1
            n = _root[n_idx]

            idx = bisect_right(n, value)

            if idx == len(n):
                _max[n_idx] = value

            n.insert(idx, value)
            self._count += 1
            if len(n) == _cap:
                # Split and link
                p = len(n) // 2
                b = n[p:]
                del n[p:]
                
                _root.insert(n_idx+1, b)
                _max.insert(n_idx, n[-1])
        else:
            # Insert first value
            self._root = [[value]]
            self._max = [value]
            self._count = 1

    def insert_sibling(self, value: Any) -> Tuple[Any, Any]:
        _root = self._root

        # Search for node and insert
        if _root:
            _max = self._max
            _cap = self._cap
            
            n_idx = bisect_left(_max, value)
            if n_idx == len(_max): n_idx -= 1
            n = _root[n_idx]

            idx = bisect_left(n, value)

            # Find left and right siblings
            if 0 <= idx-1:
                prev_val = n[idx-1]
            elif n_idx != 0:
                prev_val = _root[n_idx-1][-1]
            else:
                prev_val = None
            if idx < len(n):
                next_val = n[idx]
            elif n_idx != len(_root)-1:
                next_val = _root[n_idx+1][0]
            else:
                _max[n_idx] = value
                next_val = None

            res = n.insert(idx, value)
            self._count += 1
            if len(n) == _cap:
                # Split and link
                p = len(n) // 2
                b = n[p:]
                del n[p:]
                
                _root.insert(n_idx+1, b)
                _max.insert(n_idx, n[-1])
            return prev_val, next_val
        else:
            # Insert first value
            self._root = [[value]]
            self._max = [value]
            self._count = 1
            return None, None

    def iter_after(self, key: Any) -> Iterable[Any]:
        _max = self._max
        _root = self._root
        if _root:
            n_idx = bisect_left(_max, key)
            if n_idx == len(_max): n_idx -= 1
            start = bisect_left(_root[n_idx], key)
            yield from _root[n_idx][start:]
            for node in _root[n_idx+1:]:
                yield from node
    
    def iter_range(self, begin_key: Any, end_key: Any) -> Iterable[Any]:
        for row in self.iter_after(begin_key):
            if row <= end_key:
                yield row
            else:
                break

    def __len__(self) -> int:
        return self._count

    def __iter__(self) -> Iterable[Any]:
        for e in self._root:
            yield from e

    def __str__(self) -> str:
        s = ""
        for value in iter(self):
            if s: s += ", "
            s += str(value)
        return f"FlatTree([{s}])"
