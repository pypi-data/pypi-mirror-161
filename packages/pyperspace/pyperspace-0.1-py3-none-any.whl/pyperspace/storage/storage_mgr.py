from pyperspace.networking import TCPMessageSocket, open_tcp_socket 
from pyperspace.protocol.storage import Request, Response

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Optional, List
import threading

CallbackType = Callable[[int], None]
ResponseCallbackType = Callable[[Response], None]
ErrorCallbackType = Callable[[Exception], None]

class StorageManagerClient:
    __slots__ = ('_port', '_workers')
    ERR_NONE = 0
    ERR_UNKNOWN = 1
    ERR_FATAL = 2

    def __init__(self, port: int, num_threads: int = 4):
        self._port = port
        self._workers = ThreadPoolExecutor(max_workers=num_threads)

    def _send_and_recv(self, req: Request, on_data: Optional[CallbackType]) -> None:
        sock = TCPMessageSocket(open_tcp_socket(self._port, False))
        resp_code = self.ERR_UNKNOWN
        try:
            sock.send_msg(req.SerializeToString())
            msg = Response.FromString(sock.recv_msg())
            if msg.WhichOneof('ResponseType') == 'Ack':
                resp_code = self.ERR_NONE
        except:
            resp_code = self.ERR_FATAL
        finally:
            sock.close()
            # Send response
            if on_data: on_data(resp_code)
    
    def _send_and_recv_msg(self, req: Request, on_data: Optional[ResponseCallbackType], on_error: Optional[ErrorCallbackType]) -> None:
        sock = TCPMessageSocket(open_tcp_socket(self._port, False))
        try:
            sock.send_msg(req.SerializeToString())
            msg = Response.FromString(sock.recv_msg())
            if on_data: on_data(msg)
        except Exception as e:
            if on_error: on_error(e)
        finally:
            sock.close()
    
    def _send_request(self, req: Request) -> Response:
        sock = TCPMessageSocket(open_tcp_socket(self._port, False))
        try:
            sock.send_msg(req.SerializeToString())
            return Response.FromString(sock.recv_msg())
        finally:
            sock.close()

    def send_shutdown(self, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Shutdown.SetInParent()
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def send_persist(self, name: str, wal_file: str, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Persist.name = name
        req.Persist.wal_file = wal_file
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def send_exit(self, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Exit.SetInParent()
        return self._workers.submit(self._send_and_recv, req, on_data)

    def send_delete(self, name: str, begin_time: int, end_time: int, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Delete.name = name
        req.Delete.begin_time = begin_time
        req.Delete.end_time = end_time
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def delete(self, name: str, begin_time: int, end_time: int) -> Response:
        req = Request()
        req.Delete.name = name
        req.Delete.begin_time = begin_time
        req.Delete.end_time = end_time
        return self._send_request(req)
    
    def send_list_datasets(self, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.ListDataSets.SetInParent()
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def list_datasets(self) -> Response:
        req = Request()
        req.ListDataSets.SetInParent()
        return self._send_request(req)
    
    def send_select(self, name: str, begin_time: int, end_time: int, on_data: Optional[ResponseCallbackType] = None, on_error: Optional[ErrorCallbackType] = None) -> Future:
        req = Request()
        req.SelectRange.name = name
        req.SelectRange.begin_time = begin_time
        req.SelectRange.end_time = end_time
        return self._workers.submit(self._send_and_recv_msg, req, on_data, on_error)
    
    def select(self, name: str, begin_time: int, end_time: int) -> Response:
        req = Request()
        req.SelectRange.name = name
        req.SelectRange.begin_time = begin_time
        req.SelectRange.end_time = end_time
        return self._send_request(req)
    
    def send_select_all(self, name: str, on_data: Optional[ResponseCallbackType] = None, on_error: Optional[ErrorCallbackType] = None) -> Future:
        req = Request()
        req.SelectAll.name = name
        return self._workers.submit(self._send_and_recv_msg, req, on_data, on_error)
    
    def select_all(self, name: str) -> Response:
        req = Request()
        req.SelectAll.name = name
        return self._send_request(req)
    
    def send_open(self, lsm_files: List[str], on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Open.lsm_names.extend(lsm_files)
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def send_close(self, lsm_files: List[str], on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Close.lsm_names.extend(lsm_files)
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def open_files(self, lsm_files: List[str]) -> Response:
        req = Request()
        req.Open.lsm_names.extend(lsm_files)
        return self._send_request(req)
    
    def close_files(self, lsm_files: List[str]) -> Response:
        req = Request()
        req.Close.lsm_names.extend(lsm_files)
        return self._send_request(req)
    
    def send_add(self, name: str, lsm_file: str, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Add.name = name
        req.Add.lsm_file = lsm_file
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def send_drop(self, name: str, lsm_file: str, delete_file: bool, on_data: Optional[CallbackType] = None) -> Future:
        req = Request()
        req.Drop.name = name
        req.Drop.lsm_file = lsm_file
        req.Drop.delete_file = delete_file
        return self._workers.submit(self._send_and_recv, req, on_data)
    
    def close(self) -> None:
        self._workers.shutdown(wait=True)
