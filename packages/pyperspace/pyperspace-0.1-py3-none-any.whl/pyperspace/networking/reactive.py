from .socket import TCPMessageSocket
from select import epoll, EPOLLIN, EPOLLOUT
from collections import deque
from typing import Callable
import socket
import struct
import threading

class Reaction:
    __slots__ = ('epoll_in',)
    def __init__(self):
        self.epoll_in = deque()

class ReactiveSocket:
    def __init__(self, s: TCPMessageSocket):
        self._s = s
        self._reaction = Reaction()

    def fileno(self) -> int:
        return self._s.socket.fileno()

    def recv_msg_async(self, on_read: Callable[[bytes], None] = None) -> None:
        if on_read: self._reaction.epoll_in.append(on_read)

    def send_msg(self, data: bytes) -> None:
        self._s.send_msg(data)

class TCPReactor:
    def __init__(self):
        self._epoll = epoll()
        self._sockets = {}
        self._in_buf = 1024
        self._event = None
        self._worker_thread = None

    def _worker(self, timeout: float, process_forever: bool) -> None:
        _event_is_set = self._event.is_set
        _process = self.process
        if process_forever:
            while not _event_is_set():
                _process(timeout)
        else:
            self.process_until_complete(timeout)

    def start(self, timeout: float = 0.1, process_forever: bool = True) -> None:
        if self._worker_thread:
            raise RuntimeError("worker thread already running")
        t = threading.Thread(target=self._worker, args=(timeout, process_forever))
        self._worker_thread = t
        self._event = threading.Event()
        t.start()

    def stop(self) -> None:
        if not self._worker_thread:
            raise RuntimeError("worker thread already stopped")
        self._event.set()
        self._worker_thread.join()
        self._worker_thread = None
        self._event = None

    def join(self) -> None:
        if self._worker_thread:
            self._worker_thread.join()

    def close(self) -> None:
        self._epoll.close()
        for s in self._sockets.values(): s._s.close()
        self._sockets.clear()

    def open_socket(self, host: str, port: int) -> ReactiveSocket:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
        s.setblocking(0)
        ms = TCPMessageSocket(s)
        rs = ReactiveSocket(ms)
        self._sockets[s.fileno()] = rs
        self._epoll.register(s.fileno(), EPOLLIN | EPOLLOUT)
        return rs

    def close_socket(self, s: ReactiveSocket) -> None:
        fd = s.fileno()
        if fd in self._sockets:
            self._epoll.unregister(fd)
            del self._sockets[fd]
        s._s.close()

    def process_until_complete(self, timeout: float = 0) -> None:
        _sockets = self._sockets
        _process = self.process
        while _sockets:
            _process(timeout)
        while _process(timeout): pass

    def process(self, timeout: float = 0) -> bool:
        events = self._epoll.poll(timeout)
        for fd, op in events:
            s = self._sockets.get(fd)
            if not s: continue
            r = s._reaction
            if op & EPOLLIN and r.epoll_in:
                rd = r.epoll_in.popleft()
                d = s._s.recv_msg()
                rd(d)
        return len(events) != 0
