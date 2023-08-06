#!/bin/env python
import os
import sys
from wirikiki.authentication import make_password


def run():
    if len(sys.argv) == 1:
        print(
            "To generate a hash suitable for the user database, provide the clear password"
        )
        print("Syntax: %s <password>" % (os.path.basename(sys.argv[0])))
        raise SystemExit(-1)
    else:
        print(make_password(sys.argv[1]))


if __name__ == "__main__":
    run()
