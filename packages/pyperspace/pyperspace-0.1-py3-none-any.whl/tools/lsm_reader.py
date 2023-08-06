from pyperspace.storage import LSMFileReader
import csv
import sys

def main():
    rd = LSMFileReader(sys.argv[1])
    try:
        wr = csv.writer(sys.stdout)
        wr.writerow(["timestamp", "data"])
        for e in rd:
            #wr.writerow([str(e.time), e.data.decode()])
            wr.writerow([str(e.time), e.data])
    except BrokenPipeError:
        pass
    finally:
        rd.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
