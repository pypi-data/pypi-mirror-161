from pyperspace.io.wal import FastWriteAheadLog, WAL_INSERT, WAL_DELETE
import sys
import csv

def main():
    w = FastWriteAheadLog(sys.argv[1])
    wr = csv.writer(sys.stdout)
    wr.writerow(["timestamp", "data"])
    while not w.eof:
        e_type, e = w.read_one()
        if e_type == WAL_INSERT:
            wr.writerow(["INSERT", str(e.time), e.data.decode()])
        elif e_type == WAL_DELETE:
            wr.writerow(["DELETE", str(e[0]), str(e[1])])
        else:
            raise IOError(f"unsupported entry type ({e_type}) decoded from write-ahead log")
    w.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
