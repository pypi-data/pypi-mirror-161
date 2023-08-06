from typing import Callable, Union
from abc import ABC, abstractmethod
import io
import os

class RandomFile:
    def __init__(self, fn: str, mode: str):
        self._fd = io.open(fn, mode)
        self._fileno = self._fd.fileno()
        self._offset = 0

    def close(self) -> None:
        self._fd.close()

    def read(self, size: int) -> bytes:
        data = os.pread(self._fileno, size, self._offset)
        self._offset += len(data)
        return data

    def write(self, data: bytes) -> int:
        count = os.pwrite(self._fileno, data, self._offset)
        self._offset += count
        return count

    @property
    def name(self) -> str:
        return self._fd.name

    def fileno(self) -> int:
        return self._fileno

    def truncate(self, size: int) -> int:
        return self._fd.truncate(size)

    def flush(self) -> None:
        self._fd.flush()

    def seek(self, offset: int) -> int:
        # Use seek() just to get the correct simulated offset
        self._offset = self._fd.seek(offset)
        return self._offset

def open_buffered(fn: str, mode: str) -> io.BufferedIOBase:
    return io.open(fn, mode)

def open_random(fn: str, mode: str) -> RandomFile:
    return RandomFile(fn, mode)
