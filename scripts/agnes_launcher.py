#!/usr/bin/env python3
"""
Agnes AI Launcher — PyInstaller Entrypoint mit WebView2 GUI.

Features:
- Prüft API-Key (Env > config.json neben .exe)
- Tkinter-Dialog bei fehlendem Key
- Startet uvicorn im Hintergrund
- Öffnet React-UI in WebView2-Fenster (pywebview)
"""

import sys
import os
import json
import logging
import threading
import time
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import messagebox
import uvicorn
import webview


if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)

CONFIG_FILE = "config.json"
LOG_FILE = "agnes.log"


def setup_logging():
    """Loggt in Datei neben der .exe (oder CWD)."""
    if getattr(sys, 'frozen', False):
        log_dir = os.path.dirname(sys.executable)
    else:
        log_dir = os.getcwd()
    log_path = os.path.join(log_dir, LOG_FILE)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        force=True,
    )
    logging.info("=== Agnes AI Launcher gestartet ===")


def get_config_path() -> str:
    """Pfad zur config.json neben der .exe (oder im Working Dir)."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), CONFIG_FILE)
    return os.path.join(os.getcwd(), CONFIG_FILE)


def load_key() -> str | None:
    """Lädt API-Key aus config.json."""
    path = get_config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("agnes_api_key")
        except Exception:
            pass
    return None


def save_key(key: str) -> None:
    """Speichert API-Key in config.json und setzt beide Env-Vars."""
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"agnes_api_key": key}, f)
    os.environ["AGNES_API_KEY"] = key
    os.environ["OPENAI_API_KEY"] = key


def show_key_dialog() -> str | None:
    """Tkinter-Dialog für API-Key-Eingabe (läuft VOR webview.start())."""
    root = tk.Tk()
    root.title("Agnes AI — API Key")
    root.geometry("460x220")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')

    tk.Label(root, text="Agnes AI API Key eingeben:", font=("Segoe UI", 10)).pack(pady=(20, 5))
    tk.Label(root, text="Format: sk-...", font=("Segoe UI", 8), fg="gray").pack()

    entry = tk.Entry(root, width=55, show="•")
    entry.pack(pady=10, padx=20)
    entry.focus()

    result = {"key": None}

    def on_save():
        key = entry.get().strip()
        if not key.startswith("sk-"):
            messagebox.showerror("Ungültiger Key", "API-Key muss mit 'sk-' beginnen.")
            return
        save_key(key)
        result["key"] = key
        root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Speichern & Starten", command=on_save, width=18, bg="#0078d4", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Abbrechen", command=on_cancel, width=18).pack(side=tk.LEFT, padx=5)

    root.protocol("WM_DELETE_WINDOW", on_cancel)
    root.mainloop()
    return result["key"]


def run_server():
    """Startet uvicorn (blockiert bis Programmende)."""
    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=False,
        )
    except Exception:
        logging.exception("Server abgestürzt")


def wait_for_server(url: str, timeout: float = 15.0, interval: float = 0.3) -> bool:
    """Wartet bis der Server antwortet. Gibt True zurück wenn ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(url, timeout=2)
            if resp.status == 200:
                logging.info("Server ist bereit (%s)", url)
                return True
        except (urllib.error.URLError, ConnectionError, OSError):
            pass
        time.sleep(interval)
    logging.error("Server wurde nicht rechtzeitig bereit (%ds)", timeout)
    return False


def main():
    # Logging initialisieren
    setup_logging()

    # 1. Key laden (Env > config.json)
    api_key = os.environ.get("AGNES_API_KEY") or load_key()

    # 2. Falls kein Key → Dialog zeigen
    if not api_key:
        api_key = show_key_dialog()
        if not api_key:
            logging.info("User hat Abbrechen geklickt")
            return  # User hat Abbrechen geklickt

    # 3. Env-Vars immer setzen (auch wenn aus config.json geladen)
    os.environ["AGNES_API_KEY"] = api_key
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["AGNES_CONFIG_DIR"] = os.path.dirname(get_config_path())

    # 4. Server im Hintergrund starten
    logging.info("Starte Agnes AI Server auf http://localhost:8000")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 5. Warten bis Server ready (poll HTTP, max 15s)
    if not wait_for_server("http://localhost:8000"):
        messagebox.showerror(
            "Server Error",
            "Der Backend-Server konnte nicht gestartet werden.\n"
            "Bitte prüfe die Logdatei 'agnes.log' und starte die App neu.",
        )
        return

    # 6. WebView2-Fenster erstellen und UI laden
    window = webview.create_window(
        "Agnes AI — Edit Image",
        "http://localhost:8000",
        width=1200,
        height=800,
        min_size=(900, 600),
        text_select=True,
    )
    webview.start(debug=False)  # Blockiert bis Fenster geschlossen


if __name__ == "__main__":
    main()