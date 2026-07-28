#!/usr/bin/env python3
"""
PyInstaller Build-Script für Agnes AI Windows .exe

Erzeugt: dist/AgnesAI.exe (onefile, console)
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path


def run_pyinstaller():
    """PyInstaller via API aufrufen."""
    import PyInstaller.__main__

    # Pfade relativ zum Projekt-Root
    project_root = Path(__file__).parent.parent
    launcher = project_root / "scripts" / "agnes_launcher.py"

    # --add-data Syntax: "src;dst" (Windows: Semikolon)
    # Format: "source_path;destination_in_bundle"
    args = [
        str(launcher),
        "--onefile",
        "--windowed",
        "--name", "AgnesAI",
        "--clean",
        "--noconfirm",
        # Backend-Module
        "--add-data", f"{project_root / 'backend'};backend",
        # Frontend Dist
        "--add-data", f"{project_root / 'frontend' / 'dist'};frontend/dist",
        # Skills (extracted)
        "--add-data", f"{project_root / 'backend' / 'skills'};skills",
        # Force bundle FastAPI and all its submodules/data
        "--collect-all", "fastapi",
        "--hidden-import", "fastapi",
        # Hidden imports für Module, die PyInstaller evtl. nicht findet
        "--hidden-import", "backend.app.config",
        "--hidden-import", "backend.app.main",
        "--hidden-import", "backend.app.routers.edit_image",
        "--hidden-import", "backend.app.routers.settings",
        "--hidden-import", "backend.app.services.pipeline",
        "--hidden-import", "backend.app.services.prompt_enhancer",
        "--hidden-import", "backend.app.services.image_generator",
        "--hidden-import", "backend.app.services.skill_loader",
        "--hidden-import", "backend.app.services.skill_extractor",
        "--hidden-import", "backend.app.models.schemas",
        "--hidden-import", "backend.app.logging_config",
        # FastAPI/Starlette/Uvicorn dependencies
        "--hidden-import", "uvicorn.logging",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.protocols.websockets.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "starlette.middleware.cors",
        "--hidden-import", "starlette",
        # Pydantic v2 + settings
        "--hidden-import", "pydantic",
        "--hidden-import", "pydantic_core",
        "--hidden-import", "pydantic_settings",
        "--collect-all", "pydantic_settings",
        # OpenAI SDK
        "--hidden-import", "openai",
        "--hidden-import", "httpx",
        # GUI dependencies
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.messagebox",
        # WebView2 / pywebview
        "--hidden-import", "webview",
        "--hidden-import", "webview.platforms.edgechromium",
        "--hidden-import", "webview.js.css",
        "--hidden-import", "webview.js.api",
    ]

    print("[BUILD] Starte PyInstaller...")
    print(f"[BUILD] Launcher: {launcher}")
    print(f"[BUILD] Args: {' '.join(args[:4])} ...")

    try:
        PyInstaller.__main__.run(args)
        print("[BUILD] [OK] Build erfolgreich!")
    except SystemExit as e:
        if e.code != 0:
            raise RuntimeError(f"PyInstaller exited with code {e.code}")
    except Exception as e:
        raise RuntimeError(f"PyInstaller failed: {e}")


def verify_build():
    """Prüfe ob .exe erstellt wurde."""
    project_root = Path(__file__).parent.parent
    exe_path = project_root / "dist" / "AgnesAI.exe"
    if exe_path.is_file():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[BUILD] [OK] AgnesAI.exe erstellt ({size_mb:.1f} MB)")
        return True
    else:
        print("[BUILD] [FAIL] AgnesAI.exe NICHT gefunden!")
        return False


def main():
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("=" * 50)
    print("Agnes AI — Windows .exe Build")
    print("=" * 50)

    # Alten Build löschen
    for d in ["dist", "build"]:
        p = project_root / d
        if p.exists():
            shutil.rmtree(p)
            print(f"[CLEAN] {d}/ entfernt")

    # PyInstaller prüfen
    try:
        import PyInstaller
        print(f"[BUILD] PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("[BUILD] PyInstaller nicht installiert, installiere...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Build ausführen
    run_pyinstaller()

    # Verifizieren
    if verify_build():
        print("\n[SUCCESS] Build abgeschlossen!")
        print(f"  Output: {project_root / 'dist' / 'AgnesAI.exe'}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()