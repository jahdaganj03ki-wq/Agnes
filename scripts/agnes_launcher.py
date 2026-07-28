import sys
import os
import threading
import time
import webbrowser
import uvicorn


if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://localhost:8000")


if __name__ == "__main__":
    if not os.environ.get("AGNES_API_KEY"):
        print("[ERROR] AGNES_API_KEY nicht gesetzt!")
        sys.exit(1)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)