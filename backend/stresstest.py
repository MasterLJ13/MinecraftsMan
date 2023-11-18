import os
import requests as r

if __name__ == "__main__":
    if os.fork() == 0:
        with r.Session() as s:
            s.get("")
