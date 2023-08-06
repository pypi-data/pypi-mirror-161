from pyperspace.storage import LSMFileMerger
import sys

def main():
    m = LSMFileMerger(sys.argv[-1])
    try:
        for fn in sys.argv[1:-1]: m.add_lsm_file(fn)
        m.merge()
    finally:
        m.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
