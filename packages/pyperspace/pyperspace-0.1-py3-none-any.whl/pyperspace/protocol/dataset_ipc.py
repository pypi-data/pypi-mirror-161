from typing import Tuple, Iterable
import struct

FLAG_NONE = 0
FLAG_FLUSH = 1
FLAG_ACK = 2
FLAG_EOF = 4
FLAG_NOT_FOUND = 8
FLAG_ERROR = 16
REQUEST_EXIT = 0
REQUEST_INSERT_ONE = 1
REQUEST_SELECT = 2
REQUEST_INSERT_MANY = 3
REQUEST_CREATE = 4
REQUEST_DELETE = 5
REQUEST_DROP = 6
REQUEST_SELECT_ALL = 7

_request = struct.Struct('BB')
_request_size = _request.size
_request_pack = _request.pack
_request_pack_into = _request.pack_into
_request_unpack = _request.unpack
_request_unpack_from = _request.unpack_from


# request_type: int, flags: int
request_pack = _request_pack

# request_type: int, flags: int
request_pack_into = _request_pack_into

# request_type, flags
request_unpack = _request_unpack

def request_unpack_size(src: memoryview) -> Tuple[int, int, int]:
    request_type, flags = _request_unpack_from(src, 0)
    return request_type, flags, 2

# request_type, flags
request_unpack_from = _request_unpack_from

def request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, int, int]:
    request_type, flags = _request_unpack_from(src, offset)
    return request_type, flags, 2

def request_calc_size_from(src: memoryview, offset: int) -> int:
    return 2

def iter_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_request(payload: memoryview) -> Iterable[Tuple[int, int]]:
    i = 0
    x = len(payload)
    while i < x:
        request_type, flags, s = request_unpack_from_size(payload, i)
        yield request_type, flags
        i += s

_select_request = struct.Struct('BBBqq')
_select_request_size = _select_request.size
_select_request_pack = _select_request.pack
_select_request_pack_into = _select_request.pack_into
_select_request_unpack = _select_request.unpack
_select_request_unpack_from = _select_request.unpack_from


def select_request_pack(flags: int, name: memoryview, begin_time: int, end_time: int) -> bytearray:
    return _select_request_pack(2, flags, len(name), begin_time, end_time) + name

def select_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview, begin_time: int, end_time: int) -> None:
    _select_request_pack_into(dst, offset, 2, flags, len(name), begin_time, end_time)
    dst[24:24+len(name)] = name[:]

def select_request_unpack(src: memoryview) -> Tuple[int, memoryview, int, int]:
    _, flags, s_name, begin_time, end_time = _select_request_unpack_from(src, 0)
    name = src[24:24+s_name]
    return flags, name, begin_time, end_time

def select_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int, int, int]:
    _, flags, s_name, begin_time, end_time = _select_request_unpack_from(src, 0)
    name = src[24:24+s_name]
    return flags, name, begin_time, end_time, 24+s_name

def select_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview, int, int]:
    _, flags, s_name, begin_time, end_time = _select_request_unpack_from(src, offset)
    name = src[24+offset:24+offset+s_name]
    return flags, name, begin_time, end_time

def select_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int, int, int]:
    _, flags, s_name, begin_time, end_time = _select_request_unpack_from(src, offset)
    name = src[24+offset:24+offset+s_name]
    return flags, name, begin_time, end_time, 24+s_name

def select_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name, _, _ = _select_request_unpack_from(src, offset)
    return 24+s_name

def iter_select_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = select_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_select_request(payload: memoryview) -> Iterable[Tuple[int, memoryview, int, int]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, begin_time, end_time, s = select_request_unpack_from_size(payload, i)
        name = payload[24+i:24+i+s_name]
        yield flags, name, begin_time, end_time
        i += s

_select_all_request = struct.Struct('BBB')
_select_all_request_size = _select_all_request.size
_select_all_request_pack = _select_all_request.pack
_select_all_request_pack_into = _select_all_request.pack_into
_select_all_request_unpack = _select_all_request.unpack
_select_all_request_unpack_from = _select_all_request.unpack_from


def select_all_request_pack(flags: int, name: memoryview) -> bytearray:
    return _select_all_request_pack(7, flags, len(name)) + name

def select_all_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview) -> None:
    _select_all_request_pack_into(dst, offset, 7, flags, len(name))
    dst[3:3+len(name)] = name[:]

def select_all_request_unpack(src: memoryview) -> Tuple[int, memoryview]:
    _, flags, s_name = _select_all_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name

def select_all_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _select_all_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name, 3+s_name

def select_all_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview]:
    _, flags, s_name = _select_all_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name

def select_all_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _select_all_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name, 3+s_name

def select_all_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name = _select_all_request_unpack_from(src, offset)
    return 3+s_name

def iter_select_all_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = select_all_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_select_all_request(payload: memoryview) -> Iterable[Tuple[int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, s = select_all_request_unpack_from_size(payload, i)
        name = payload[3+i:3+i+s_name]
        yield flags, name
        i += s

_entry = struct.Struct('qH')
_entry_size = _entry.size
_entry_pack = _entry.pack
_entry_pack_into = _entry.pack_into
_entry_unpack = _entry.unpack
_entry_unpack_from = _entry.unpack_from


def entry_pack(time: int, data: memoryview) -> bytearray:
    return _entry_pack(time, len(data)) + data

def entry_pack_into(dst: bytearray, offset: int, time: int, data: memoryview) -> None:
    _entry_pack_into(dst, offset, time, len(data))
    dst[10:10+len(data)] = data[:]

def entry_unpack(src: memoryview) -> Tuple[int, memoryview]:
    time, s_data = _entry_unpack_from(src, 0)
    data = src[10:10+s_data]
    return time, data

def entry_unpack_size(src: memoryview) -> Tuple[int, memoryview, int]:
    time, s_data = _entry_unpack_from(src, 0)
    data = src[10:10+s_data]
    return time, data, 10+s_data

def entry_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview]:
    time, s_data = _entry_unpack_from(src, offset)
    data = src[10+offset:10+offset+s_data]
    return time, data

def entry_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int]:
    time, s_data = _entry_unpack_from(src, offset)
    data = src[10+offset:10+offset+s_data]
    return time, data, 10+s_data

def entry_calc_size_from(src: memoryview, offset: int) -> int:
    _, s_data = _entry_unpack_from(src, offset)
    return 10+s_data

def iter_entry_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = entry_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_entry(payload: memoryview) -> Iterable[Tuple[int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        time, s_data, s = entry_unpack_from_size(payload, i)
        data = payload[10+i:10+i+s_data]
        yield time, data
        i += s

_delete_request = struct.Struct('BBBqq')
_delete_request_size = _delete_request.size
_delete_request_pack = _delete_request.pack
_delete_request_pack_into = _delete_request.pack_into
_delete_request_unpack = _delete_request.unpack
_delete_request_unpack_from = _delete_request.unpack_from


def delete_request_pack(flags: int, name: memoryview, begin_time: int, end_time: int) -> bytearray:
    return _delete_request_pack(5, flags, len(name), begin_time, end_time) + name

def delete_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview, begin_time: int, end_time: int) -> None:
    _delete_request_pack_into(dst, offset, 5, flags, len(name), begin_time, end_time)
    dst[24:24+len(name)] = name[:]

def delete_request_unpack(src: memoryview) -> Tuple[int, memoryview, int, int]:
    _, flags, s_name, begin_time, end_time = _delete_request_unpack_from(src, 0)
    name = src[24:24+s_name]
    return flags, name, begin_time, end_time

def delete_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int, int, int]:
    _, flags, s_name, begin_time, end_time = _delete_request_unpack_from(src, 0)
    name = src[24:24+s_name]
    return flags, name, begin_time, end_time, 24+s_name

def delete_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview, int, int]:
    _, flags, s_name, begin_time, end_time = _delete_request_unpack_from(src, offset)
    name = src[24+offset:24+offset+s_name]
    return flags, name, begin_time, end_time

def delete_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int, int, int]:
    _, flags, s_name, begin_time, end_time = _delete_request_unpack_from(src, offset)
    name = src[24+offset:24+offset+s_name]
    return flags, name, begin_time, end_time, 24+s_name

def delete_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name, _, _ = _delete_request_unpack_from(src, offset)
    return 24+s_name

def iter_delete_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = delete_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_delete_request(payload: memoryview) -> Iterable[Tuple[int, memoryview, int, int]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, begin_time, end_time, s = delete_request_unpack_from_size(payload, i)
        name = payload[24+i:24+i+s_name]
        yield flags, name, begin_time, end_time
        i += s

_create_request = struct.Struct('BBB')
_create_request_size = _create_request.size
_create_request_pack = _create_request.pack
_create_request_pack_into = _create_request.pack_into
_create_request_unpack = _create_request.unpack
_create_request_unpack_from = _create_request.unpack_from


def create_request_pack(flags: int, name: memoryview) -> bytearray:
    return _create_request_pack(4, flags, len(name)) + name

def create_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview) -> None:
    _create_request_pack_into(dst, offset, 4, flags, len(name))
    dst[3:3+len(name)] = name[:]

def create_request_unpack(src: memoryview) -> Tuple[int, memoryview]:
    _, flags, s_name = _create_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name

def create_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _create_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name, 3+s_name

def create_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview]:
    _, flags, s_name = _create_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name

def create_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _create_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name, 3+s_name

def create_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name = _create_request_unpack_from(src, offset)
    return 3+s_name

def iter_create_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = create_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_create_request(payload: memoryview) -> Iterable[Tuple[int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, s = create_request_unpack_from_size(payload, i)
        name = payload[3+i:3+i+s_name]
        yield flags, name
        i += s

_drop_request = struct.Struct('BBB')
_drop_request_size = _drop_request.size
_drop_request_pack = _drop_request.pack
_drop_request_pack_into = _drop_request.pack_into
_drop_request_unpack = _drop_request.unpack
_drop_request_unpack_from = _drop_request.unpack_from


def drop_request_pack(flags: int, name: memoryview) -> bytearray:
    return _drop_request_pack(6, flags, len(name)) + name

def drop_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview) -> None:
    _drop_request_pack_into(dst, offset, 6, flags, len(name))
    dst[3:3+len(name)] = name[:]

def drop_request_unpack(src: memoryview) -> Tuple[int, memoryview]:
    _, flags, s_name = _drop_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name

def drop_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _drop_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name, 3+s_name

def drop_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview]:
    _, flags, s_name = _drop_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name

def drop_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _drop_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name, 3+s_name

def drop_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name = _drop_request_unpack_from(src, offset)
    return 3+s_name

def iter_drop_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = drop_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_drop_request(payload: memoryview) -> Iterable[Tuple[int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, s = drop_request_unpack_from_size(payload, i)
        name = payload[3+i:3+i+s_name]
        yield flags, name
        i += s

_insert_one_request = struct.Struct('BBBqH')
_insert_one_request_size = _insert_one_request.size
_insert_one_request_pack = _insert_one_request.pack
_insert_one_request_pack_into = _insert_one_request.pack_into
_insert_one_request_unpack = _insert_one_request.unpack
_insert_one_request_unpack_from = _insert_one_request.unpack_from


def insert_one_request_pack(flags: int, name: memoryview, time: int, data: memoryview) -> bytearray:
    dst = bytearray(18+len(name)+len(data))
    _insert_one_request_pack_into(dst, 0, 1, flags, len(name), time, len(data))
    dst[18:18+len(name)] = name[:]
    dst[18+len(name):18+len(name)+len(data)] = data[:]
    return dst

def insert_one_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview, time: int, data: memoryview) -> None:
    _insert_one_request_pack_into(dst, offset, 1, flags, len(name), time, len(data))
    dst[18:18+len(name)] = name[:]
    dst[18+len(name):18+len(name)+len(data)] = data[:]

def insert_one_request_unpack(src: memoryview) -> Tuple[int, memoryview, int, memoryview]:
    _, flags, s_name, time, s_data = _insert_one_request_unpack_from(src, 0)
    name = src[18:18+s_name]
    data = src[18+s_name:18+s_name+s_data]
    return flags, name, time, data

def insert_one_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int, memoryview, int]:
    _, flags, s_name, time, s_data = _insert_one_request_unpack_from(src, 0)
    name = src[18:18+s_name]
    data = src[18+s_name:18+s_name+s_data]
    return flags, name, time, data, 18+s_name+s_data

def insert_one_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview, int, memoryview]:
    _, flags, s_name, time, s_data = _insert_one_request_unpack_from(src, offset)
    name = src[18+offset:18+offset+s_name]
    data = src[18+offset+s_name:18+offset+s_name+s_data]
    return flags, name, time, data

def insert_one_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int, memoryview, int]:
    _, flags, s_name, time, s_data = _insert_one_request_unpack_from(src, offset)
    name = src[18+offset:18+offset+s_name]
    data = src[18+offset+s_name:18+offset+s_name+s_data]
    return flags, name, time, data, 18+s_name+s_data

def insert_one_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name, _, s_data = _insert_one_request_unpack_from(src, offset)
    return 18+s_name+s_data

def iter_insert_one_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = insert_one_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_insert_one_request(payload: memoryview) -> Iterable[Tuple[int, memoryview, int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, time, s_data, s = insert_one_request_unpack_from_size(payload, i)
        name = payload[18+i:18+i+s_name]
        data = payload[18+i+s_name:18+i+s_name+s_data]
        yield flags, name, time, data
        i += s

_insert_many_request = struct.Struct('BBB')
_insert_many_request_size = _insert_many_request.size
_insert_many_request_pack = _insert_many_request.pack
_insert_many_request_pack_into = _insert_many_request.pack_into
_insert_many_request_unpack = _insert_many_request.unpack
_insert_many_request_unpack_from = _insert_many_request.unpack_from


def insert_many_request_pack(flags: int, name: memoryview) -> bytearray:
    return _insert_many_request_pack(3, flags, len(name)) + name

def insert_many_request_pack_into(dst: bytearray, offset: int, flags: int, name: memoryview) -> None:
    _insert_many_request_pack_into(dst, offset, 3, flags, len(name))
    dst[3:3+len(name)] = name[:]

def insert_many_request_unpack(src: memoryview) -> Tuple[int, memoryview]:
    _, flags, s_name = _insert_many_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name

def insert_many_request_unpack_size(src: memoryview) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _insert_many_request_unpack_from(src, 0)
    name = src[3:3+s_name]
    return flags, name, 3+s_name

def insert_many_request_unpack_from(src: memoryview, offset: int) -> Tuple[int, memoryview]:
    _, flags, s_name = _insert_many_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name

def insert_many_request_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, memoryview, int]:
    _, flags, s_name = _insert_many_request_unpack_from(src, offset)
    name = src[3+offset:3+offset+s_name]
    return flags, name, 3+s_name

def insert_many_request_calc_size_from(src: memoryview, offset: int) -> int:
    _, _, s_name = _insert_many_request_unpack_from(src, offset)
    return 3+s_name

def iter_insert_many_request_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = insert_many_request_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_insert_many_request(payload: memoryview) -> Iterable[Tuple[int, memoryview]]:
    i = 0
    x = len(payload)
    while i < x:
        _, flags, s_name, s = insert_many_request_unpack_from_size(payload, i)
        name = payload[3+i:3+i+s_name]
        yield flags, name
        i += s

_response = struct.Struct('BB')
_response_size = _response.size
_response_pack = _response.pack
_response_pack_into = _response.pack_into
_response_unpack = _response.unpack
_response_unpack_from = _response.unpack_from


# request_type: int, flags: int
response_pack = _response_pack

# request_type: int, flags: int
response_pack_into = _response_pack_into

# request_type, flags
response_unpack = _response_unpack

def response_unpack_size(src: memoryview) -> Tuple[int, int, int]:
    request_type, flags = _response_unpack_from(src, 0)
    return request_type, flags, 2

# request_type, flags
response_unpack_from = _response_unpack_from

def response_unpack_from_size(src: memoryview, offset: int) -> Tuple[int, int, int]:
    request_type, flags = _response_unpack_from(src, offset)
    return request_type, flags, 2

def response_calc_size_from(src: memoryview, offset: int) -> int:
    return 2

def iter_response_raw(payload: memoryview) -> Iterable[memoryview]:
    i = 0
    x = len(payload)
    while i < x:
        s = response_calc_size_from(payload, i)
        yield payload[i:i+s]
        i += s

def iter_response(payload: memoryview) -> Iterable[Tuple[int, int]]:
    i = 0
    x = len(payload)
    while i < x:
        request_type, flags, s = response_unpack_from_size(payload, i)
        yield request_type, flags
        i += s

