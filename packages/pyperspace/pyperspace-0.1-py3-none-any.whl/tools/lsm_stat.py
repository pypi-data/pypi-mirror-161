from pyperspace.storage import LSMFileReader
import sys

def main():
    rd = LSMFileReader(sys.argv[1])
    print(rd.header)
    return 0

if __name__ == '__main__':
    sys.exit(main())
