#!/bin/env python
import os
import sys

PORT = 8000
HOST = "127.0.0.1"
SIMPLE = os.environ.get('FG', False)

if len(sys.argv) > 1:
    if sys.argv[1] in {"create", "new"}:
        if len(sys.argv) > 2:
            import wirikiki
            import shutil

            ROOT = os.path.dirname(wirikiki.__file__)
            dst = sys.argv[2]
            shutil.copytree(os.path.join(ROOT, "config"), dst)
            for path in ("web", "myKB"):
                shutil.copytree(os.path.join(ROOT, path), os.path.join(dst, path))

            settings = os.path.join(dst, "settings.toml")
            data = open(settings).read()
            with open(settings, "w") as f:
                for line in data.split("\n"):
                    if line.startswith("base_dir"):
                        f.write("base_dir = %r\n" % os.path.join(os.getcwd(), dst))
                    else:
                        f.write(line + "\n")

            raise SystemExit(0)
        else:
            print("Syntax: %s %s <name>" % (os.path.basename(sys.argv[0]), sys.argv[1]))
            raise SystemExit(1)


def run():
    import os

    pid = 0 if SIMPLE else os.fork()

    if pid > 0:  # main process, launch browser
        import time
        import webbrowser

        time.sleep(1)
        webbrowser.open(f"http://{HOST}:{PORT}")
    else:  # daemon (children) process
        import sys
        import uvicorn

        try:
            from setproctitle import setproctitle
        except ImportError:
            pass
        else:
            setproctitle(sys.argv[0])
        if not SIMPLE:
            os.setsid()  # detach
        uvicorn.run("wirikiki.routes:app", host=HOST, port=PORT, log_level="warning")


if __name__ == "__main__":
    run()
