from pyperspace.io.wal import FastWriteAheadLog, WAL_INSERT, WAL_DELETE
from pyperspace.storage import LSMFileMerger, MemTable
import sys

def main():
    w = FastWriteAheadLog(sys.argv[1])
    mt = MemTable()
    try:
        mt.load_from_wal(w)
    finally:
        w.close()
    m = LSMFileMerger(sys.argv[2])
    try:
        m.add_memtable(mt)
        m.merge()
    finally:
        m.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
