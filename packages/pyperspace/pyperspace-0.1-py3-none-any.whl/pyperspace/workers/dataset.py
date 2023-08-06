from pyperspace.data import RawEntry, Entry
from pyperspace.storage import DataSet, StorageManagerClient
from pyperspace.networking import MessageSocket, TCPMessageSocket, TCPListener, open_tcp_socket, PipeMessageSocket
from pyperspace.protocol.dataset_ipc import REQUEST_EXIT, REQUEST_INSERT_MANY, REQUEST_SELECT, REQUEST_DELETE, REQUEST_CREATE, REQUEST_DROP, \
                                            REQUEST_SELECT_ALL, FLAG_NONE, FLAG_FLUSH, FLAG_ACK, FLAG_EOF, FLAG_NOT_FOUND, FLAG_ERROR, \
                                            insert_many_request_pack, insert_many_request_unpack_size, entry_pack, entry_calc_size_from, \
                                            response_pack, iter_entry_raw, create_request_pack, drop_request_pack, delete_request_pack, select_request_pack, \
                                            select_request_unpack_from, response_unpack_from_size, create_request_unpack_from, drop_request_unpack_from, \
                                            delete_request_unpack_from, request_pack, select_all_request_unpack_from, select_all_request_pack

from typing import List, Iterable
from datetime import datetime
import multiprocessing
import os

# Selector modes
PIPE_MODE = 0
TCP_MODE = 1
TCP_FAST_MODE = 2

class MessageQueue:
    __slots__ = ('_insert_buf', '_insert_buf_extend', '_sock', '_send_msg', '_recv_msg', '_name', '_insert_buf_size', '_insert_count', '_insert_ack', '_insert_flags')
    def __init__(self, socket: MessageSocket, name: str, insert_buf_size: int, insert_ack: bool, insert_flush: bool):
        self._insert_buf = bytearray()
        self._insert_buf_extend = self._insert_buf.extend
        self._sock = socket
        self._send_msg = socket.send_msg
        self._recv_msg = socket.recv_msg
        self._name = bytes(name, 'utf-8')
        self._insert_buf_size = insert_buf_size
        self._insert_count = 0
        self._insert_ack = insert_ack
        flags = FLAG_NONE
        if insert_ack: flags |= FLAG_ACK
        if insert_flush: flags |= FLAG_FLUSH
        self._insert_flags = flags

    def close(self) -> None:
        self._sock.close()

    def flush(self) -> None:
        if self._insert_count != 0:
            _name = self._name
            _insert_buf = self._insert_buf
            self._send_msg(insert_many_request_pack(self._insert_flags, _name) + _insert_buf)
            _insert_buf.clear()

            if self._insert_ack: self._recv_msg()
            self._insert_count = 0
    
    def send_delete(self, begin_time: int, end_time: int) -> None:
        self._send_msg(delete_request_pack(self._insert_flags, self._name, begin_time, end_time))
        if self._insert_ack: self._recv_msg()
    
    def send_create(self) -> None:
        self._send_msg(create_request_pack(self._insert_flags, self._name))
        if self._insert_ack: self._recv_msg()
    
    def send_drop(self) -> None:
        self._send_msg(drop_request_pack(self._insert_flags, self._name))
        if self._insert_ack: self._recv_msg()

    def send_select(self, begin_time: int, end_time: int) -> Iterable[RawEntry]:
        _recv_msg = self._recv_msg
        self._send_msg(select_request_pack(FLAG_NONE, self._name, begin_time, end_time))
        msg = memoryview(_recv_msg())
        _, flags, offset = response_unpack_from_size(msg, 0)
        while (flags & FLAG_EOF) == 0:
            for data in iter_entry_raw(msg[offset:]):
                yield RawEntry(data)
            msg = memoryview(_recv_msg())
            _, flags, offset = response_unpack_from_size(msg, 0)
    
    def send_select_all(self) -> Iterable[RawEntry]:
        _recv_msg = self._recv_msg
        self._send_msg(select_all_request_pack(FLAG_NONE, self._name))
        msg = memoryview(_recv_msg())
        _, flags, offset = response_unpack_from_size(msg, 0)
        while (flags & FLAG_EOF) == 0:
            for data in iter_entry_raw(msg[offset:]):
                yield RawEntry(data)
            msg = memoryview(_recv_msg())
            _, flags, offset = response_unpack_from_size(msg, 0)

    def send_insert(self, time: int, entry: bytes) -> None:
        _insert_buf_size = self._insert_buf_size
        if _insert_buf_size:
            _insert_count = self._insert_count + 1
            self._insert_buf_extend(entry_pack(time, entry))

            if _insert_count != _insert_buf_size:
                self._insert_count = _insert_count
            else:
                _insert_buf = self._insert_buf
                self._send_msg(insert_many_request_pack(self._insert_flags, self._name) + _insert_buf)
                _insert_buf.clear()
                if self._insert_ack: self._recv_msg()
                self._insert_count = 0
        else:
            _name = self._name

            self._send_msg(insert_many_request_pack(self._insert_flags, self._name) + entry_pack(time, entry))
            if self._insert_ack: self._recv_msg()
    
    def send_insert_many(self, entries: Iterable[Entry]) -> None:
        self._send_msg(insert_many_request_pack(self._insert_flags, self._name) + b''.join(entry_pack(e.time, e.data) for e in entries))
        if self._insert_ack: self._recv_msg()


class DataSetNodeMap:
    __slots__ = ('_sockets', '_next', '_insert_buf_size', '_insert_ack', '_insert_flush', '_mqueues')
    def __init__(self, sockets: List[MessageSocket], insert_buf_size: int, insert_ack: bool, insert_flush: bool):
        self._sockets = sockets
        self._next = 0
        self._insert_buf_size = insert_buf_size
        self._insert_ack = insert_ack
        self._insert_flush = insert_flush
        self._mqueues = {}

    @property
    def names(self) -> List[str]:
        return list(self._mqueues.keys())

    def __getitem__(self, name: str) -> MessageQueue:
        _mqueues = self._mqueues
        mq = _mqueues.get(name)
        if mq is None:
            _sockets = self._sockets
            _next = self._next
            sock = _sockets[_next]
            self._next = (_next + 1) % len(_sockets)
            mq = MessageQueue(sock, name, self._insert_buf_size, self._insert_ack, self._insert_flush)
            _mqueues[name] = mq
        return mq

    def close(self) -> None:
        for mq in self._mqueues.values():
            mq.close()
    
    def flush(self) -> None:
        for mq in self._mqueues.values():
            mq.flush()

class DataSetWorker:
    __slots__ = ('_node_id', '_data_dir', '_admin_queue', '_datasets', '_select_buffer_size', '_get_dataset', '_sm_port', '_max_entries', '_sm')
    def __init__(self, sm_port: int, node_id: int, data_dir: str, admin_queue: multiprocessing.Queue, sel_buffer: int, max_entries: int):
        self._node_id = node_id
        self._data_dir = data_dir
        self._admin_queue = admin_queue
        self._datasets = {}
        self._select_buffer_size = sel_buffer
        self._get_dataset = self._datasets.get
        self._sm_port = sm_port
        self._max_entries = max_entries

    def load_datasets(self, ds_dir_names: Iterable[str]) -> None:
        _datasets = self._datasets
        node_id = self._node_id
        data_dir = self._data_dir
        for fn in ds_dir_names:
            ds_dir = os.path.join(data_dir, fn)
            name_fn = os.path.join(ds_dir, "name.dat")
            if not os.path.isfile(name_fn): continue
            with open(name_fn, "r") as fd:
                name = fd.readline().strip()
                b_name = name.encode()
                print(f"LOADING DATASET: {name} -- node={node_id}, dir={fn}")
                _datasets[b_name] = DataSet(ds_dir, self._max_entries)

    def _close_datasets(self) -> None:
        for sym, ds in self._datasets.items():
            ds.close()
            try:
                # Convert to LSM
                if ds.count != 0:
                    wal_file = ds.wal_file
                    self._sm.send_persist(sym.decode('utf-8'), wal_file, lambda err, ds=ds, wal_file=wal_file: self._process_persist_ack(err, ds, wal_file))
            except Exception as e:
                print(f"_close_datasets(FATAL): {e}")
                pass
    
    def _process_create(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        flags, sym = create_request_unpack_from(msg, 0)
        sym = sym.tobytes()
        try:
            self._create_dataset(sym)
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_CREATE, FLAG_ACK))
        except KeyError:
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_CREATE, FLAG_ACK | FLAG_NOT_FOUND))
        except:
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_CREATE, FLAG_ACK | FLAG_ERROR))
        return True

    def _process_drop(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        flags, sym = drop_request_unpack_from(msg, 0)
        sym = sym.tobytes()
        try:
            self._drop_dataset(sym)
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_DROP, FLAG_ACK))
        except KeyError:
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_DROP, FLAG_ACK | FLAG_NOT_FOUND))
        except:
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_DROP, FLAG_ACK | FLAG_ERROR))
        return True

    def _process_select(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        _, name, begin_time, end_time = select_request_unpack_from(msg, 0)
        _send_msg = msg_sock.send_msg

        ds = self._get_dataset(name.tobytes())
        header = response_pack(REQUEST_SELECT, FLAG_ACK)
        if ds is not None:
            _select_buffer_size = self._select_buffer_size
            t1 = datetime.now()
            find_res = ds.find_range(begin_time, end_time)
            if _select_buffer_size == 0:
                for e in find_res:
                    _send_msg(header + e.raw_data)
            else:
                buf = bytearray(header)
                msgs = 0
                
                for e in find_res:
                    buf += e.raw_data
                    msgs += 1
                    if msgs == _select_buffer_size:
                        _send_msg(buf)
                        buf = bytearray(header)
                        msgs = 0
                if msgs != 0: _send_msg(buf)

            # Send EOF control
            _send_msg(response_pack(REQUEST_SELECT, FLAG_ACK | FLAG_EOF))
            t2 = datetime.now()
            print(f"SELECT TIME: {t2-t1} (~ entries)")
        else:
            _send_msg(response_pack(REQUEST_SELECT, FLAG_ACK | FLAG_EOF | FLAG_NOT_FOUND))
        return True
    
    def _process_select_all(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        _, name = select_all_request_unpack_from(msg, 0)
        _send_msg = msg_sock.send_msg

        ds = self._get_dataset(name.tobytes())
        header = response_pack(REQUEST_SELECT_ALL, FLAG_ACK)
        if ds is not None:
            _select_buffer_size = self._select_buffer_size
            t1 = datetime.now()
            find_res = ds.find_all()
            if _select_buffer_size == 0:
                for e in find_res:
                    _send_msg(header + e.raw_data)
            else:
                buf = bytearray(header)
                msgs = 0
                
                for e in find_res:
                    buf += e.raw_data
                    msgs += 1
                    if msgs == _select_buffer_size:
                        _send_msg(buf)
                        buf = bytearray(header)
                        msgs = 0
                if msgs != 0: _send_msg(buf)

            # Send EOF control
            _send_msg(response_pack(REQUEST_SELECT_ALL, FLAG_ACK | FLAG_EOF))
            t2 = datetime.now()
            print(f"SELECT TIME: {t2-t1} (~ entries)")
        else:
            _send_msg(response_pack(REQUEST_SELECT_ALL, FLAG_ACK | FLAG_EOF | FLAG_NOT_FOUND))
        return True

    def _process_delete(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        flags, name, begin_time, end_time = delete_request_unpack_from(msg, 0)
        ds = self._get_dataset(name.tobytes())
        if ds is not None:
            ds.delete(begin_time, end_time, flush=bool(flags & FLAG_FLUSH))
            # Acknowledge if applicable
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_DELETE, FLAG_ACK))
        elif flags & FLAG_ACK:
            msg_sock.send_msg(response_pack(REQUEST_DELETE, FLAG_ACK | FLAG_NOT_FOUND))
        return True

    def _create_dataset(self, name: bytes) -> DataSet:
        _datasets = self._datasets
        if name in _datasets:
            raise KeyError(f"dataset \"{name.decode('utf-8')}\" already exists")
        ds_dir = os.path.join(self._data_dir, f"ds_{self._node_id}_{len(_datasets)}")
        ds = DataSet(ds_dir, self._max_entries)
        with open(os.path.join(ds_dir, "name.dat"), "w") as fd:
            fd.write(name.decode())
        _datasets[name] = ds
        return ds
    
    def _drop_dataset(self, name: bytes) -> None:
        _datasets = self._datasets
        ds = _datasets.get(name)
        if ds is None:
            raise KeyError(f"dataset \"{name.decode('utf-8')}\" does not exist")
        ds.drop()
        del _datasets[name]

    def _process_persist_ack(self, err: int, ds: DataSet, wal_file: str) -> None:
        if err == StorageManagerClient.ERR_NONE:
            ds.kill(wal_file)
            os.unlink(wal_file)
        else:
            # TODO: What if there's a failure?
            print(f"_process_persist_ack(FATAL): {resp}")

    def _handle_insert_many(self, msg: memoryview, msg_sock: MessageSocket) -> bool:
        # Multi-row insert
        flags, sym, o = insert_many_request_unpack_size(msg)
        sym = sym.tobytes()
        
        # TODO: throw if not exists
        ds = self._get_dataset(sym)
        if ds:
            # Consume rows and insert into DataSet
            persist = False
            for e in iter_entry_raw(msg[o:]):
                persist = not ds.insert_raw(RawEntry(e), flush=False)
            if persist:
                wal_file = ds.freeze()
                self._sm.send_persist(sym.decode('utf-8'), wal_file, lambda err, ds=ds, wal_file=wal_file: self._process_persist_ack(err, ds, wal_file))

            # Flush and acknowledge if applicable
            if flags & FLAG_FLUSH: ds.flush()
            if flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_INSERT_MANY, FLAG_ACK))
        elif flags & FLAG_ACK: msg_sock.send_msg(response_pack(REQUEST_INSERT_MANY, FLAG_ACK | FLAG_NOT_FOUND))
        return True
    
    def _run_selector(self, msg_sock: MessageSocket) -> None:
        actions = {REQUEST_SELECT: self._process_select,
                   REQUEST_SELECT_ALL: self._process_select_all,
                   REQUEST_INSERT_MANY: self._handle_insert_many,
                   REQUEST_DELETE: self._process_delete,
                   REQUEST_CREATE: self._process_create,
                   REQUEST_DROP: self._process_drop,
                   REQUEST_EXIT: lambda x, y: False}
        # Main processing loop
        while True:
            msg = memoryview(msg_sock.recv_msg())

            if not actions[msg[0]](msg, msg_sock):
                msg_sock.close()
                break

    def run(self, mode: int) -> None:
        self._sm = StorageManagerClient(self._sm_port)
        if mode == PIPE_MODE:
            runner = lambda: self._run_pipe()
        elif mode == TCP_MODE:
            runner = lambda: self._run_tcp(False)
        elif mode == TCP_FAST_MODE:
            runner = lambda: self._run_tcp(True)
        else:
            raise ValueError("invalid worker run mode specified")
        try:
            runner()
        finally:
            try:
                self._close_datasets()
                self._sm.close()
            except Exception as e:
                print(f"run~prologue(FATAL): {e}")
    
    def _run_pipe(self) -> None:
        # Get pipe info
        ip, op = self._admin_queue.get()

        msg_sock = PipeMessageSocket(op, ip)
        self._run_selector(msg_sock)

    def _run_tcp(self, no_delay: bool) -> None:
        with TCPListener(no_delay) as listener:
            listener.open()
            
            # Send ephemeral port back to admin node
            self._admin_queue.put(listener.port)
            # Acknowledgement from client
            self._admin_queue.get()
        
            # Accept connection from admin node
            msg_sock = listener.accept()
            self._run_selector(msg_sock)

class DataSetWorkerPool:
    __slots__ = ('_admin_queues', '_data_dir', '_num_workers', '_workers', '_clients', '_dsmap', '_insert_buf_size', '_select_buffer_size', '_insert_ack', '_insert_flush', '_mode', '_sm_port','_max_entries')
    def __init__(self, storage_mgr_port: int, mode: int, data_dir: str, num_workers: int, send_buf_size: int = 0, recv_buf_size: int = 0, max_entries: int = 100000, insert_ack: bool = False, insert_flush: bool = True):
        self._admin_queues = []
        self._data_dir = data_dir
        self._num_workers = num_workers
        self._workers = []
        self._clients = []
        self._dsmap = None
        self._insert_buf_size = send_buf_size
        self._select_buffer_size = recv_buf_size
        self._insert_ack = insert_ack
        self._insert_flush = insert_flush
        self._mode = mode
        self._sm_port = storage_mgr_port
        self._max_entries = max_entries

    def _worker(self, node_id: int, ds_dirs: List[str], admin_queue: multiprocessing.Queue) -> None:
        w = DataSetWorker(self._sm_port, node_id, self._data_dir, admin_queue, self._select_buffer_size, self._max_entries)
        w.load_datasets(ds_dirs)
        w.run(self._mode)

    def _get_dataset_dirs(self) -> List[str]:
        res = []
        _data_dir = self._data_dir
        for fn in os.listdir(_data_dir):
            ds_dir = os.path.join(_data_dir, fn)
            if not os.path.isdir(ds_dir): continue
            name_fn = os.path.join(ds_dir, "name.dat")
            if not os.path.isfile(name_fn): continue
            res.append(fn)
        return res

    def start(self) -> None:
        os.makedirs(self._data_dir, 0o744, exist_ok=True)
        self._clients.clear()
        self._admin_queues = [multiprocessing.Queue() for _ in range(self._num_workers)]
        ds_dirs = self._get_dataset_dirs()
        datasets_per_node = len(ds_dirs) // self._num_workers
        self._workers = [multiprocessing.Process(target=self._worker, args=(node_id, ds_dirs[node_id*datasets_per_node:(node_id+1)*datasets_per_node], admin_queue)) for node_id, admin_queue in enumerate(self._admin_queues)]
        if self._mode == PIPE_MODE:
            self._start_pipes()
        elif self._mode == TCP_MODE:
            self._start_tcp(False)
        elif self._mode == TCP_FAST_MODE:
            self._start_tcp(True)
        else:
            raise ValueError("invalid worker mode specified")
        self._dsmap = DataSetNodeMap(self._clients, self._insert_buf_size, self._insert_ack, self._insert_flush)
    
    def _start_pipes(self) -> None:
        for admin_queue, w in zip(self._admin_queues, self._workers):
            ip, op = os.pipe(), os.pipe()
            w.start()
            admin_queue.put((ip[1], op[0]))

            self._clients.append(PipeMessageSocket(ip[0], op[1]))

    def _start_tcp(self, no_delay: bool) -> None:
        for admin_queue, w in zip(self._admin_queues, self._workers):
            w.start()

            port = admin_queue.get()
            self._clients.append(TCPMessageSocket(open_tcp_socket(port, no_delay)))
            admin_queue.put(True)
    
    def stop(self) -> None:
        self._dsmap.flush()

        for c in self._clients:
            c.send_msg(request_pack(REQUEST_EXIT, FLAG_NONE))

    def close(self) -> None:
        self._dsmap.close()
        for w in self._workers: w.close()
        for q in self._admin_queues: q.close()
    
    def join(self) -> None:
        for w in self._workers: w.join(timeout=None)
    
    def flush(self) -> None:
        self._dsmap.flush()
    
    @property
    def datasets(self) -> List[str]:
        return self._dsmap.names

    def send_insert(self, name: str, time: int, data: bytes) -> None:
        self._dsmap[name].send_insert(time, data)
    
    def send_insert_many(self, name: str, entries: Iterable[Entry]) -> None:
        self._dsmap[name].send_insert_many(entries)

    def send_select(self, name: str, begin_time: int, end_time: int) -> Iterable[RawEntry]:
        return self._dsmap[name].send_select(begin_time, end_time)
    
    def send_select_all(self, name: str) -> Iterable[RawEntry]:
        return self._dsmap[name].send_select_all()
    
    def send_delete(self, name: str, begin_time: int, end_time: int) -> None:
        self._dsmap[name].send_delete(begin_time, end_time)
    
    def send_create(self, name: str) -> None:
        self._dsmap[name].send_create()
    
    def send_drop(self, name: str) -> None:
        self._dsmap[name].send_drop()
