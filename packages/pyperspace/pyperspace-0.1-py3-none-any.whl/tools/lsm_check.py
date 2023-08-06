from pyperspace.storage import LSMFileReader
import sys

def main():
    ret = 0
    for fn in sys.argv[1:]:
        try:
            rd = LSMFileReader(fn)
            c = 0
            try:
                last_time = None
                for e in rd:
                    if last_time is not None and e.time < last_time:
                        print(f"ERROR [{fn}]: entry #{c} -- out of time order (prev={last_time}, curr={e.time})")
                        ret = 1
                        break
                    last_time = e.time
                    c += 1
            except BrokenPipeError:
                pass
            except Exception as e:
                print(f"ERROR [{fn}]: entry #{c} -- {e}")
            finally:
                rd.close()
        except Exception as e:
            print(f"ERROR [{fn}]: {e}")
    return ret

if __name__ == '__main__':
    sys.exit(main())
