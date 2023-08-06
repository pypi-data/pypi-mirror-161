import io
import os

class FileStorage:
    def __init__(self, fd: io.BufferedWriter):
        self._fd = fd
        self._fileno = fd.fileno()

    def close(self) -> None:
        self._fd.close()

    def _pread(self, size: int, offset: int) -> bytes:
        data = os.pread(self._fileno, size, offset)
        if len(data) != size:
            raise EOFError(f"end-of-file reached (read {len(data)} of {size} bytes) [file={self._fd.name}]")
        return data
