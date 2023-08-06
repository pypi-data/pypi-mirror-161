from pyperspace.storage import LSMFileMerger, MemTable
from pyperspace.io import FastWriteAheadLog
from pyperspace.data import RangeMap

from typing import Iterable

def wal_to_lsm(wal_file: str, lsm_file: str) -> None:
    m = LSMFileMerger(lsm_file)
    try:
        mt = MemTable()
        wal = FastWriteAheadLog(wal_file)
        try:
            mt.load_from_wal(wal)
        finally:
            wal.close()
        m.add_memtable(mt)
        m.merge()
    finally:
        m.close()
