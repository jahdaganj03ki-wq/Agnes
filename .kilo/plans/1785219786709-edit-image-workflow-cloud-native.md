# Plan: Edit Image Workflow — Cloud-Native (Linux / Codespace / GitHub Actions)

## Tech-Stack (Entschieden)

| Schicht | Technologie | Begründung |
|---------|------------|------------|
| Frontend | React 19 + Vite + Tailwind CSS 4 | Pixel-perfekte UI nach Agnes AI Web-App Look |
| Backend | Python 3.12 + FastAPI | OpenAI SDK + SSE-Streaming + Single-Runtime |
| API-Clients | `openai` Python SDK | Offizielles Agnes SDK (`pip install openai`, base_url = `https://apihub.agnes-ai.com/v1`) |
| CI/CD | GitHub Actions (`ubuntu-latest`) | Linux-kompatibel, Codespace-identisch |
| Dev-Env | GitHub Codespace (`.devcontainer/`) | Node 22 + Python 3.12 + Port-Forwarding |

## Architektur-Entscheidungen

| Entscheidung | Gewählt | Begründung |
|-------------|---------|------------|
| Pipeline-Steuerung | Backend orchestriert (1 Endpoint + SSE) | Minimale Netzwerk-Latenz, progressive UI-Updates |
| Bild-Upload | Client-seitige Canvas-Kompression (max 2048px, JPEG 0.85) | Garantiert <4MB Base64, kein externer Host nötig |
| RetryState | Frontend-Cache (React State + localStorage) | Backend bleibt stateless |
| API-Key | `AGNES_API_KEY` Env-Var + **config.json** (App-Verzeichnis) | Fallback: Env → config.json → .env; Frontend nie Zugriff |
| Logging | `agnes.log` (Projektwurzel, Rotating 5MB×3, kein accent) | `RotatingFileHandler`, Format: `[Datum] [LEVEL] [Modul] Message` |
| Modelle | `agnes-2.0-flash` + `agnes-image-2.1-flash` | Über öffentliche API kostenlos nutzbar (Free: 20 RPM) |
| Settings-Storage | `config.json` neben Exe / im Projekt-Root | Einfaches JSON, funktioniert Dev + Prod + .exe |
| Settings-UI | Sidebar-Zahnrad → Modal | Kompakt, konsistent mit Agnes AI Look |
| Key-Validierung | `GET /v1/models` beim Speichern | Sofortiges Feedback, ob Key gültig |

## Projektstruktur

```
/workspaces/Agnes/
├── backend/                         # NEU: Python FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app, CORS, Lifespan
│   │   ├── config.py                # Settings (AGNES_API_KEY, LOG_LEVEL, etc.)
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py           # Pydantic models (EditRequest, SkillInfo, etc.)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── skill_loader.py      # Liest + cached extracted skills
│   │   │   ├── skill_extractor.py   # Python-Äquivalent von extract-skills.sh
│   │   │   ├── prompt_enhancer.py   # POST /v1/chat/completions (agnes-2.0-flash)
│   │   │   ├── image_generator.py   # POST /v1/images/generations (agnes-image-2.1-flash)
│   │   │   └── pipeline.py          # Orchestriert alle 3 Schritte + SSE-Generator
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── edit_image.py        # POST /api/edit-image (SSE)
│   │   │   └── settings.py          # GET/POST /api/settings (API-Key Management)
│   │   └── logging_config.py        # RotatingFileHandler Setup
│   ├── skills/
│   │   ├── raw/                     # [MIGRIERT] Bestehende .md-Skill-Dateien
│   │   │   ├── AgnesGenerationSkill.md
│   │   │   ├── AgnesCliSkill.md
│   │   │   └── VisionCraftPromptGuide.md
│   │   └── extracted/               # [GENERATED] git-ignored
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_skill_loader.py
│   │   ├── test_prompt_enhancer.py  # Mocked API-Calls
│   │   ├── test_image_generator.py
│   │   ├── test_pipeline.py
│   │   └── test_logging.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example                 # AGNES_API_KEY=sk-...
│
├── frontend/                        # NEU: React + Vite + Tailwind + Router
│   ├── src/
│   │   ├── main.tsx                  # BrowserRouter-Wrapper
│   │   ├── App.tsx                   # Routes: "/" → WelcomePage, "/edit" → EditImagePage
│   │   ├── index.css                # Tailwind imports + Dark-Theme CSS-Vars
│   │   ├── pages/
│   │   │   ├── WelcomePage.tsx      # / → Logo + Action-Buttons + Banner
│   │   │   └── EditImagePage.tsx    # /edit → Komplette Pipeline (Upload→Skills→Enhance→Generate)
│   │   ├── components/
│   │   │   ├── ImageUploader.tsx    # Drag & Drop, Canvas-Kompression
│   │   │   ├── SkillLoadCard.tsx    # Animierte Skill-Lade-Karten (3×)
│   │   │   ├── PromptPanel.tsx      # Original vs Enhanced Prompt
│   │   │   ├── ImageCompare.tsx     # Before/After Side-by-Side
│   │   │   ├── ActionToolbar.tsx    # Like, Dislike, Copy, Download
│   │   │   ├── AspectRatioSelect.tsx# 1:1, 16:9, 9:16, 4:3, 3:2, 21:9
│   │   │   └── ErrorBanner.tsx      # Fehleranzeige mit Retry-Button
│   │   ├── hooks/
│   │   │   ├── useEditImage.ts      # SSE-Stream + State-Machine
│   │   │   ├── useImageCompress.ts  # Canvas-Kompression
│   │   │   └── useRetryState.ts     # localStorage Cache
│   │   └── types/
│   │       └── index.ts
│   ├── tests/
│   │   ├── WelcomePage.test.tsx
│   │   ├── EditImagePage.test.tsx
│   │   ├── SkillLoadCard.test.tsx
│   │   ├── useEditImage.test.ts
│   │   ├── useImageCompress.test.ts
│   │   └── setup.ts                 # Vitest setup (mock fetch + ReadableStream)
│   ├── index.html
│   ├── vite.config.ts               # proxy /api → backend:8000 (dev) | backend-app (prod via mount)
│   ├── vitest.config.ts
│   ├── tailwind.config.ts
│   ├── package.json
│   └── tsconfig.json
│
├── frontend/public/
│   ├── favicon.ico                  # [ICON] Aus biglogo.png konvertiert
│   ├── favicon-32x32.png
│   ├── favicon-16x16.png
│   ├── apple-touch-icon.png
│   └── logo.png                     # [ICON] biglogo.png lokal kopiert
├── .devcontainer/
│   └── devcontainer.json            # NEU: Python 3.12 + Node 22 + Ports
│
├── .github/
│   └── workflows/
│       ├── ci.yml                   # NEU: ubuntu-latest, build+test
│       └── release.yml              # NEU: ubuntu-latest, publish artifacts
│
├── .env.example                     # AGNES_API_KEY
├── .gitignore                       # [ERWEITERT] __pycache__, node_modules, dist, .env
├── agnes.log                        # [GENERATED] git-ignored (KEIN accent)
└── README.md                        # [AKTUALISIERT]
```

## Workflow: Edit Image (Vollständig)

```
User öffnet App → Welcome Screen
  ↓ klickt "Edit Image" oder uploadet Bild
ImageUploader (Drag & Drop / File Picker) → Canvas-Kompression (2048px max)
  ↓
Prompt-Eingabe: "Recolor Clothes to red"
  ↓ klickt "Generate" → POST /api/edit-image (SSE-Stream)
  ↓
Backend:
  1. Skill Loading (3 Dateien → extracted.md → cache)
     → SSE: event=skill_loading, skill=AgnesGenerationSkill
     → SSE: event=skill_loaded,   skill=AgnesGenerationSkill, chars=1240
     → SSE: skill_loading/loaded für 3 Skills (50-200ms simuliert)
  2. Prompt Enhancement
     → System Prompt = extracted skill content + instructions
     → POST /v1/chat/completions (agnes-2.0-flash)
     → SSE: event=prompt_enhanced, {original, enhanced}
  3. Image Generation
     → POST /v1/images/generations (agnes-image-2.1-flash)
     → Body: enhanced_prompt, image_base64, ratio
     → SSE: event=generating
     → SSE: event=result, {image_url, revised_prompt}
  ↓
Frontend zeigt:
  - 3 SkillLoadCards (animiert: loading → loaded)
  - PromptPanel (Original links, Enhanced rechts)
  - ImageCompare (Original/Before links, Result/After rechts)
  - ActionToolbar (Like, Dislike, Copy, Download)
  ↓
Bei Fehler:
  - SSE: event=error, {message, retry_allowed}
  - ErrorBanner + Retry-Button
  - **Simple Retry:** Retry startet immer bei `skills_loading` (full pipeline restart). RetryState dient nur zum Vorausfüllen der Formularfelder, NICHT zum Skippen von Pipeline-Schritten.
```

## Production Serving (FastAPI served)

```
Dev-Modus:    Frontend (Vite, Port 5173) ──proxy /api──→ Backend (Uvicorn, Port 8000)
Prod-Modus:   Backend (Uvicorn, Port 8000) ──mount /──→ frontend/dist/ (StaticFiles)
```

**Backend `main.py` — Production Startup:**

```python
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# API-Routen (vor dem Static-Mount!)
app.include_router(edit_image_router, prefix="/api")

# Production: serve gebautes Frontend
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.isdir(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
```

**Start-Befehle:**

| Modus | Befehl |
|-------|--------|
| Dev (beide) | Terminal 1: `uvicorn backend.app.main:app --reload --port 8000` |
| | Terminal 2: `cd frontend && npm run dev` |
| Dev (combined) | `uvicorn backend.app.main:app --reload --port 8000` → http://localhost:8000 |
| CI | `cd frontend && npm run build && uvicorn backend.app.main:app --port 8000` |
| Prod | `cd frontend && npm run build && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` |

---

## Pipeline-Detail (Backend, `pipeline.py`)

```python
async def edit_image_pipeline(request: EditRequest) -> AsyncGenerator[SSEEvent, None]:
    # 1. Skills laden
    skills = await skill_loader.load_all()
    for s in skills:
        yield SSEEvent(event="skill_loading", data=s.name)
        await asyncio.sleep(random.uniform(0.05, 0.2))  # realistische I/O-Timing
        yield SSEEvent(event="skill_loaded", data=s.dict())
        logger.info(f"Skill loaded: {s.name} ({s.chars} chars)")
    
    # 2. Prompt Enhancement
    yield SSEEvent(event="enhancing", data={})
    enhanced = await prompt_enhancer.enhance(
        system_prompt=build_system_prompt(skills),
        user_prompt=request.prompt,
    )
    yield SSEEvent(event="prompt_enhanced", data={
        "original": request.prompt,
        "enhanced": enhanced.text,
    })
    logger.info(f"Prompt enhanced: '{request.prompt[:50]}...' → enhanced")
    
    # 3. Image Generation
    yield SSEEvent(event="generating", data={})
    result = await image_generator.generate(
        prompt=enhanced.text,
        image_base64=request.image_base64,
        ratio=request.aspect_ratio,
    )
    yield SSEEvent(event="result", data={
        "image_url": result.url,
        "revised_prompt": result.revised_prompt,
    })
    logger.info(f"Image generated: {result.url}")
```

## API-Key & Logging

```
# .env.example
AGNES_API_KEY=sk-your-key-here
LOG_LEVEL=INFO              # DEBUG | INFO | WARNING | ERROR

# agnes.log (auto-created, git-ignored)
[2026-07-28 06:37:54] [INFO] [skill_loader] Loaded 3 skills (3840 chars)
[2026-07-28 06:37:55] [INFO] [prompt_enhancer] Enhanced prompt (200 chars) in 1.2s
[2026-07-28 06:37:56] [INFO] [image_generator] Generated image (2048x2048) in 3.4s
[2026-07-28 06:37:57] [ERROR] [pipeline] API 429: Rate limit exceeded, retry in 10s
```

## .devcontainer/devcontainer.json (Entwurf)

```json
{
  "name": "Agnes Edit Image",
  "image": "mcr.microsoft.com/devcontainers/universal:2",
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "22" },
    "ghcr.io/devcontainers/features/python:1": { "version": "3.12" }
  },
  "forwardPorts": [5173, 8000],
  "portsAttributes": {
    "5173": { "label": "Frontend (Vite)", "onAutoForward": "openBrowser" },
    "8000": { "label": "Backend (FastAPI)", "onAutoForward": "notify" }
  },
  "postCreateCommand": "sudo apt-get update && sudo apt-get install -y imagemagick && pip install -r backend/requirements.txt && cd frontend && npm install",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "bradlc.vscode-tailwindcss",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

## CI/CD (GitHub Actions)

### ci.yml (`ubuntu-latest`)

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - name: Cache pip
        uses: actions/cache@v4
        with: { path: ~/.cache/pip, key: pip-${{ hashFiles('backend/requirements.txt') }} }
      - name: Cache npm
        uses: actions/cache@v4
        with: { path: ~/.npm, key: npm-${{ hashFiles('frontend/package-lock.json') }} }
      - name: Install backend deps
        run: pip install -r backend/requirements.txt
      - name: Extract skills
        run: python -m backend.app.services.skill_extractor
      - name: Run backend tests
        run: pytest backend/tests -v --cov=backend.app
        env: { AGNES_API_KEY: ${{ secrets.AGNES_API_KEY }} }
      - name: Install frontend deps
        run: cd frontend && npm ci
      - name: Lint frontend
        run: cd frontend && npm run lint
      - name: Run frontend tests
        run: cd frontend && npm run test -- --run    # Vitest in CI mode
      - name: Build frontend
        run: cd frontend && npm run build
```

### release.yml (Tag-Trigger)

```yaml
name: Release
on:
  push: { tags: ["v*.*.*"] }
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - name: Install + build backend
        run: |
          pip install -r backend/requirements.txt
          python -m backend.app.services.skill_extractor
          pytest backend/tests -v
      - name: Install + build frontend
        run: |
          cd frontend && npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: agnes-edit-image-${{ github.ref_name }}
          path: |
            frontend/dist/
            backend/
          include-hidden-files: true
```

### Schritt 12: API-Key Settings (Neu)

**Backend:**
- `backend/app/config.py`: `Settings`-Klasse erweitert um `config_file_path` (Property), Methoden `load_config()` / `save_config(key)` → liest/schreibt `config.json` im Arbeitsverzeichnis (Dev: Projekt-Root, Exe: `sys._MEIPASS`/Exe-Verzeichnis). `AGNES_API_KEY` Property prüft: Env → config.json → Default.
- `backend/app/routers/settings.py`: 
  - `GET /api/settings` → `{ "has_key": bool }` (Key selbst nie zurückgeben)
  - `POST /api/settings` → Body: `{ "api_key": "sk-..." }`, validiert via `GET https://apihub.agnes-ai.com/v1/models` (Auth: Bearer Key), bei 200 speichert in config.json, returned `{ "ok": true }`, bei 401/403 `{ "ok": false, "error": "Invalid API key" }`.
- `backend/app/main.py`: Router inkludieren (`app.include_router(settings_router, prefix="/api")`).

**Frontend:**
- `src/components/SettingsModal.tsx`: Modal mit Passwort-Feld (`type="password"`), Toggle-Button (Show/Hide), "Testen & Speichern"-Button. Zeigt Loading + Ergebnis (Grün/Rot).
- `src/hooks/useSettings.ts`: `fetchSettings()` (GET), `saveSettings(key)` (POST + Validierung), State `{ hasKey, loading, error }`.
- `src/components/Sidebar.tsx`: Zahnrad-Icon (`⚙️`) oben/rechts → `onClick` öffnet Modal.
- `src/App.tsx`: `SettingsProvider` (Context) wrappt App, lädt `hasKey` beim Mount.

**Config-Datei (`config.json`):**
```json
{ "agnes_api_key": "sk-..." }
```
Git-ignoriert (`.gitignore` ergänzt).

**Tests:**
- Backend: `test_settings_router.py` (mockt `httpx.AsyncClient.get` für Validierung)
- Frontend: `SettingsModal.test.tsx` (Mock `fetch`, prüft Modal-Öffnen/Validierung)

### Schritt 1: Projekt-Cleanup
- Lösche: `AgnesWindows.sln`, `Directory.Build.props`
- Lösche: `src/` (komplett), `tests/AgnesWindows.Tests/`
- Lösche: `.github/workflows/ci.yml`, `.github/workflows/release.yml`
- Lösche: `scripts/extract-skills.ps1`, `scripts/extract-skills.sh`
- Bereinige `.gitignore`: Entferne .NET/WinUI/MSIX-Einträge, füge `__pycache__/`, `*.pyc`, `node_modules/`, `dist/`, `.env`, `agnes.log`, `backend/skills/extracted/` hinzu
- Verschiebe: `src/AgnesWindows.Skills/raw/*.md` → `backend/skills/raw/`

### Schritt 2: Backend-Grundgerüst
- Erstelle `backend/` mit `requirements.txt` (`fastapi`, `uvicorn[standard]`, `openai`, `python-multipart`, `pytest`, `pytest-asyncio`, `httpx`)
- `backend/app/main.py`: FastAPI-App mit CORS (`allow_origins=["*"]` für Dev, Frontend-URL für Prod), Lifespan-Handler für Skill-Cache-Vorladung
- `backend/app/config.py`: Pydantic `Settings` (liest `AGNES_API_KEY`, `LOG_LEVEL`)
- `backend/app/logging_config.py`: `RotatingFileHandler` (5MB, 3 Backups), Format `[%Y-%m-%d %H:%M:%S] [%(levelname)s] [%(name)s] %(message)s`

### Schritt 3: Skill-System (Python)
- `backend/app/services/skill_extractor.py`: Python-Neuimplementierung des Bash-Skripts — liest `.md` aus `raw/`, extrahiert prompt-relevante Sections, schreibt nach `extracted/`. Enthält `if __name__ == "__main__": main()` für CLI-Aufruf (`python -m backend.app.services.skill_extractor`)
- `backend/app/services/skill_loader.py`: Liest `extracted/`-Dateien, cached in Memory (Singleton), gibt Liste von `SkillInfo(path, chars, content)` zurück
- Tests: `test_skill_loader.py` (mockt Dateisystem, prüft Cache-Verhalten)

### Schritt 4: API-Client-Dienste
- `backend/app/services/prompt_enhancer.py`: Nutzt `openai.OpenAI(base_url="https://apihub.agnes-ai.com/v1")`, baut System-Prompt aus Skill-Content, ruft `agnes-2.0-flash` auf, gibt Enhanced Prompt zurück. Loggt Latenz + Prompt-Länge.
- `backend/app/services/image_generator.py`: Ruft `agnes-image-2.1-flash` auf, sendet Prompt + Base64-Bild + Aspect Ratio. Loggt Latenz + Bildgröße.
- Tests: `test_prompt_enhancer.py`, `test_image_generator.py` (mocken `openai`-Client mit `pytest.monkeypatch`)

### Schritt 5: Pipeline & Router
- `backend/app/services/pipeline.py`: `edit_image_pipeline()` — AsyncGenerator, der SSE-Events yieldet. Jeder Schritt in eigenem try/except. Error-Event enthält `code`, `message`, `step` ("skills"/"enhance"/"generate"), `retryable` (true/false). Nicht-retryable Fehler: `config_error` (kein API-Key), `auth_failed` (invalid key), `invalid_image`. Retryable: `rate_limit_exceeded`, `server_error`, `timeout`, `network_error`.
- `backend/app/routers/edit_image.py`: `POST /api/edit-image` — nimmt `EditRequest` (prompt, image_base64, aspect_ratio), returned `StreamingResponse` mit SSE-Events. Loggt Request-Start, -Ende, Fehler. Keine Session-IDs (stateless).
- `backend/app/models/schemas.py`: Pydantic-Modelle: `EditRequest`, `SkillInfo`, `PromptEnhancement`, `GenerationResult`, `SSEEvent`, `ErrorEvent`

### Schritt 6: App-Icon & Favicon
- Lade `https://agnes-ai.com/images/biglogo.png` herunter nach `frontend/public/logo.png`
- ImageMagick `convert` für Favicon-Erzeugung (vorinstalliert im devcontainer):
  ```bash
  cd frontend/public
  convert logo.png -resize 32x32 favicon.ico
  convert logo.png -resize 32x32 favicon-32x32.png
  convert logo.png -resize 16x16 favicon-16x16.png
  convert logo.png -resize 180x180 apple-touch-icon.png
  ```
- Trage Icons in `index.html` ein:
  ```html
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
  ```
- Das Logo erscheint in der Sidebar (oben) und im WelcomeScreen

### Schritt 7: Frontend-Grundgerüst
- `npm create vite@latest frontend -- --template react-ts`
- Dependencies: `react-router-dom` (Version 7, mit `createBrowserRouter`)
- Tailwind CSS 4 installieren + per CSS konfigurieren (`@import "tailwindcss"` in `index.css`, keine `tailwind.config.ts`)
- Theme als CSS-Variablen: `#000000` Background, `#1C1C1E` Sidebar, `#00BCD4` Accent, `#2962FF` Secondary
- Dev-Abhängigkeiten: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`
- `vite.config.ts`: Proxy `/api` → `http://localhost:8000` (dev), `@`-Alias für `src/`
- `vitest.config.ts`: identische Aliase, environment `jsdom`, setup-File `tests/setup.ts`

**Routing-Struktur (`App.tsx` → `main.tsx`):**
```tsx
// main.tsx: Router + Provider
import { BrowserRouter } from "react-router-dom";

root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);
```

```tsx
// App.tsx: Layout Shell with Sidebar + Routes
function App() {
  return (
    <div className="flex h-screen bg-[#000000] text-white">
      <Sidebar />                        {/* persistent, immer sichtbar */}
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/edit" element={<EditImagePage />} />
        </Routes>
      </main>
    </div>
  );
}
```

- **Navigation:** Sidebar-Button "New Task" → `navigate("/edit")`; Aktion "Edit Image" auf WelcomePage → `navigate("/edit")`
- **TypeScript-Typen** in `types/index.ts`

### Schritt 8: Frontend-Seiten & Komponenten (nach Screenshot-Look)

**Seiten (in `pages/`):**
- `WelcomePage.tsx` (Route `/`): Logo + "Welcome What can I do for you?" + Input-Feld + Action-Buttons-Kacheln (AI Slides, Build website, AI Design, AI Sheet, More — alle navigieren zu `/edit`) + "Limited-time offer" Banner
- `EditImagePage.tsx` (Route `/edit`): Orchestriert gesamten Pipeline-Flow:
  - State `idle` → Show `ImageUploader` + `AspectRatioSelect` + Prompt-Input
  - State `skills_loading` → Show 3× `SkillLoadCard`
  - State `enhancing` → Show `PromptPanel`
  - State `generating` → Show Loading-Indicator
  - State `result` → Show `ImageCompare` + `ActionToolbar`
  - State `error` → Show `ErrorBanner`

**Komponenten (in `components/`):**
- `Sidebar.tsx`: Navigation (New Task, Search, Scheduled, Library), "ALL TASKS"-Liste, Logo oben. "New Task" → `navigate("/edit")`
- `ImageUploader.tsx`: Drag & Drop + File Picker, Canvas-Kompression (max 2048px, JPEG 0.85), zeigt Preview
- `SkillLoadCard.tsx`: 3 Karten mit Lade-Animation (Buch-Icon, Pfad/Tag, Char-Count), simuliert 50-200ms pro Card
- `PromptPanel.tsx`: Zweispaltig — Original (links) vs Enhanced (rechts), mit Copy-Button
- `ImageCompare.tsx`: Side-by-Side — Original/Before links, Result/After rechts
- `ActionToolbar.tsx`: Like, Dislike, Copy URL, Download
- `AspectRatioSelect.tsx`: Segmented Control: 1:1, 16:9, 9:16, 4:3, 3:2, 21:9
- `ErrorBanner.tsx`: Fehlermeldung + Retry-Button, nutzt `useRetryState`

### Schritt 9: Frontend-Hooks & State-Machine

**State-Machine (exakte Übergänge):**

```
idle ──(image + prompt)──→ input_ready
input_ready ──(generate click)──→ uploading ──→ skills_loading
skills_loading ──(SSE: skill_loaded ×3)──→ enhancing
enhancing ──(SSE: prompt_enhanced)──→ generating
generating ──(SSE: result)──→ result
ANY ──(SSE: error / Netzwerkfehler)──→ error
error ──(retry click)──→ retrying ──→ skills_loading (full pipeline restart)
result ──(new image/prompt)──→ input_ready
```

**Timeouts:**
- Enhancement-Request: 60s
- Generation-Request: 120s
- Gesamt-Pipeline: 180s
- Retry: exponential backoff 1s→2s→4s, max 3 Versuche
- 429: `Retry-After` Header auswerten, sonst 10s

**Implementierung:**
- `useEditImage.ts`: 
  ```ts
  const res = await fetch("/api/edit-image", { method: "POST", body: JSON.stringify(req) });
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  // Zeilenweises SSE-Parsing: "event: xxx\ndata: {...}\n\n" → dispatch per useReducer
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    // parse "event:" / "data:" Zeilen aus decoder.decode(value)
    // Splitte bei "\n\n", extrahiere event + data, rufe dispatch(event, JSON.parse(data)) auf
  }
  ```
  State-Machine via discriminated union Type. AbortController bei unmount/timeout.
- `useImageCompress.ts`: Canvas-basiert, max 2048px, JPEG-Qualität 0.85, gibt `{ base64, size_bytes }` zurück
- `useRetryState.ts`: localStorage-Schlüssel `agnes_retry_state`, speichert `{ prompt, enhanced_prompt, image_base64, aspect_ratio, step_failed }`

### Schritt 10: Devcontainer & Gitignore
- `.devcontainer/devcontainer.json` (siehe Entwurf oben)
- `.gitignore`: Alte .NET-Einträge entfernen, neue hinzufügen: `__pycache__/`, `*.pyc`, `node_modules/`, `dist/`, `.env`, `backend/skills/extracted/`, `agnes.log`

### Schritt 11: CI/CD-Workflows
- `.github/workflows/ci.yml` (siehe Entwurf oben)
- `.github/workflows/release.yml` (siehe Entwurf oben)
- README.md aktualisieren

### Schritt 12: Integrationstest & Validierung
- **Backend:** `curl POST /api/edit-image` mit Sample-Image + Prompt → SSE-Stream mit allen 5 Event-Typen
- **Production Serving:** `curl http://localhost:8000/` → gibt `index.html` zurück (kein 404)
- **Image-Kompression:** Prüfen dass Base64 <4MB für 4K-Input
- **Fehlerszenarien:** 401 (falscher Key, `AGNES_API_KEY=invalid`), 429 (Rate-Limit via Test-Key), Timeout (mock), leeres Bild
- **Retry:** Fehler provozieren → Retry-Button erscheint → klicken → Pipeline restartet ab `skills_loading`
- **Routing:** `curl http://localhost:8000/` → 200 + WelcomePage. `curl http://localhost:8000/edit` → Vite SPA fallback (200, EditImagePage)
- **Frontend-Tests:** `npx vitest run` — mindestens 5 Test-Suites (WelcomePage, EditImagePage, SkillLoadCard, useEditImage, useImageCompress)

## Risiken & Migration

| Risiko | Mitigation |
|--------|-----------|
| Alte .NET-Dateien nicht vollständig gelöscht | Schritt 1 explizit: `rm -rf src/ tests/ *.sln *.props` |
| Skill-Dateien verloren | Verschieben vor Löschen in Schritt 1 |
| Frontend-Build failed in CI | `npm ci` statt `npm install` für deterministische Builds |
| API-Key in CI nicht gesetzt | Tests via `pytest.mark.skipif(not os.environ.get("AGNES_API_KEY"))` schützen |
| SSE-Stream nicht korrekt verarbeitet | Backend-Test mit `httpx.AsyncClient.stream()`, Frontend-Test mit `fetch`/`ReadableStream`-Mock |
| Production Serving: Frontend vor API gemountet | API-Router VOR StaticFiles mounten (Reihenfolge in `main.py`) |
| 429 Rate-Limit blockiert CI | Retry-Logik im Backend, CI-Tests mit `@pytest.mark.slow` markieren, nicht im critical path |

---

## Windows .exe Build (PyInstaller + WebView2)

### Ziel
Einzelne `AgnesAI.exe` für Windows, die **alles im eigenen Fenster** ausführt (kein externer Browser):
- Native Windows-Fenster mit **embedded WebView2** (via `pywebview`)
- React-Frontend wird im eingebetteten Browser gerendert (`http://localhost:8000`)
- **Bei erstem Start: API-Key-Dialog** (Tkinter, keine extra Deps)
- Key wird in `config.json` **neben der .exe** gespeichert
- Bei vorhandenem Key: direkter Start → eingebetteter Browser lädt UI
- Konsolenfenster zeigt Logs (`--console`)

### Neuer Code

**`scripts/agnes_launcher.py`** — Entrypoint für PyInstaller
```python
import sys
import os
import json
import threading
import time
import uvicorn
import tkinter as tk
from tkinter import messagebox
import webview  # pywebview → nutzt WebView2 auf Windows

if hasattr(sys, '_MEIPASS'):
    sys.path.insert(0, sys._MEIPASS)
    # _MEIPASS/backend/ enthält das kopierte backend/-Paket
    sys.path.insert(0, os.path.join(sys._MEIPASS, "backend"))

CONFIG_FILE = "config.json"

def get_config_path():
    """Pfad zur config.json neben der .exe (oder im Working Dir)."""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), CONFIG_FILE)
    return os.path.join(os.getcwd(), CONFIG_FILE)

def load_key():
    path = get_config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f).get("agnes_api_key")
        except Exception:
            pass
    return None

def save_key(key):
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"agnes_api_key": key}, f)
    os.environ["AGNES_API_KEY"] = key

def show_key_dialog():
    """Tkinter-Dialog für API-Key-Eingabe (läuft vor webview-Start)."""
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
    """Startet uvicorn im Hintergrund-Thread."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, log_level="info", access_log=False)

def main():
    # 1. Key laden (Env > config.json)
    api_key = os.environ.get("AGNES_API_KEY") or load_key()

    # 2. Falls kein Key → Dialog zeigen
    if not api_key:
        api_key = show_key_dialog()
        if not api_key:
            return  # User hat Abbrechen geklickt

    # 3. Server im Hintergrund starten
    print("[INFO] Starte Agnes AI Server auf http://localhost:8000")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 4. Warten bis Server ready
    time.sleep(1.5)

    # 5. WebView2-Fenster erstellen und UI laden
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
```

**`scripts/build_exe.py`** — PyInstaller-Aufruf via API
```python
import PyInstaller.__main__

PyInstaller.__main__.run([
    'scripts/agnes_launcher.py',
'--onefile',
    '--windowed',  # Kein Konsolenfenster — saubere Desktop-App
    '--name', 'AgnesAI',
    '--add-data', 'backend/app;backend',   # backend/ im Bundle behalten!
    '--add-data', 'frontend/dist;frontend/dist',
    '--add-data', 'backend/skills;skills',
    '--hidden-import', 'backend.app.config',
    '--hidden-import', 'backend.app.main',
    '--hidden-import', 'backend.app.routers.edit_image',
    '--hidden-import', 'backend.app.routers.settings',
    '--hidden-import', 'backend.app.services.pipeline',
    '--hidden-import', 'backend.app.services.prompt_enhancer',
    '--hidden-import', 'backend.app.services.image_generator',
    '--hidden-import', 'backend.app.services.skill_loader',
    '--hidden-import', 'backend.app.services.skill_extractor',
    '--hidden-import', 'backend.app.models.schemas',
    '--hidden-import', 'backend.app.logging_config',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'tkinter.messagebox',
    '--hidden-import', 'webview',
'--hidden-import', 'webview.platforms.edgechromium', # WebView2 Backend
        '--hidden-import', 'webview.js.css',
        '--hidden-import', 'webview.js.api',
        # FastAPI + Starlette + Uvicorn explizit (sonst: ModuleNotFoundError)
        '--hidden-import', 'fastapi',
        '--hidden-import', 'fastapi.responses',
        '--hidden-import', 'fastapi.routing',
        '--hidden-import', 'starlette',
        '--hidden-import', 'starlette.middleware',
        '--hidden-import', 'starlette.middleware.cors',
        '--hidden-import', 'uvicorn',
        '--hidden-import', 'uvicorn.logging',
        '--hidden-import', 'uvicorn.loops.auto',
        '--hidden-import', 'uvicorn.protocols.http.auto',
        '--hidden-import', 'uvicorn.protocols.websockets.auto',
        '--hidden-import', 'uvicorn.lifespan.on',
        '--hidden-import', 'pydantic',
        '--hidden-import', 'pydantic_core',
        '--hidden-import', 'openai',
        '--hidden-import', 'httpx',
        '--collect-all', 'fastapi',
    ])
```

**Neue Abhängigkeit**: `requirements.txt` um `pywebview` ergänzen:
```
pywebview>=5.0
```

### Release-Workflow-Erweiterung (`.github/workflows/release.yml`)

`build-exe` Job installiert zusätzlich `pywebview`:
```yaml
- name: Install Dependencies
  run: |
    pip install -r backend/requirements.txt
    pip install pyinstaller pywebview
```

### Validierung
1. Tag pushen: `git tag v0.1.0 && git push origin v0.1.0`
2. Workflow wartet auf `build-exe` (windows-latest)
3. Artefakt `AgnesAI.exe` herunterladen
4. Auf Windows: **Doppelklick** auf `AgnesAI.exe`
   - Beim ersten Start: Dialog öffnet sich → Key eingeben → Speichern
   - Key wird in `config.json` neben der .exe gespeichert
   - Native Fenster öffnet sich, lädt `http://localhost:8000` im eingebetteten WebView2
   - React-UI läuft **vollständig im App-Fenster** (kein externer Browser)
5. Weitere Starts: Kein Dialog, direkter Start (Key aus config.json)

### Risiken & Mitigation
| Risiko | Mitigation |
|--------|-----------|
| PyInstaller findet versteckte Imports nicht | Explizite `--hidden-import` für alle Backend-Module + `tkinter` + `webview` + `fastapi`/`starlette`/`uvicorn` + `--collect-all fastapi` |
| Tkinter nicht verfügbar | Ist Teil der Python-Stdlib, immer dabei |
| config.json Schreibrechte | Neben .exe im User-Ordner (Downloads/Desktop) problemlos |
| `skill_extractor` nicht gelaufen | Build-Script ruft es explizit vor PyInstaller auf |
| WebView2 Runtime fehlt | `pywebview` zeigt Installations-Dialog an; Windows 10/11 haben es meist vorinstalliert |
| Einfrierender Server bei Fenster-Schluss | Daemon-Thread (`daemon=True`) → Prozess endet mit Hauptthread; für clean shutdown später `atexit`/Signal-Handler ergänzen |
| Mehrfach-Start (Doppelklick) | Optional: Port-Check (8000) vor Server-Start → existierendes Fenster fokussieren (später) |
| Console vs. Windowed Build | Aktuell `--console` (Logs sichtbar); für Release `--windowed` Variante ergänzen |

---

## Finale Design-Entscheidungen (Implementierungsfertig)

| Bereich | Entscheidung | Begründung |
|---------|--------------|------------|
| **Entrypoint** | `scripts/agnes_launcher.py` (Tkinter-Dialog → WebView2) | Einzelne .exe, keine externen Browser |
| **API-Key Speicher** | `config.json` neben .exe (portabel) + Env-Var Fallback | Einfach, portable, CI-freundlich |
| **Backend** | FastAPI + uvicorn im Daemon-Thread (`daemon=True`) | Einfache Prozess-Lebensdauer, kein Signal-Handling nötig |
| **Frontend** | React build (Vite) → statische Files → `webview.create_window(url)` | Native Look, volle React-Funktionalität |
| **PyInstaller** | `--onefile --windowed` für Release, `--console` nur für Debug-Builds | Sauberes Desktop-App-Fenster ohne Konsolen-Overlay; Logs gehen nach `agnes.log` |
| **Hidden Imports** | Alle Backend-Module + `tkinter` + `webview` + `webview.platforms.edgechromium` | PyInstaller findet WebView2-Backend nicht automatisch |
| **Requirements** | `pywebview>=5.0` zu `backend/requirements.txt` | WebView2 auf Windows |
| **Release Workflow** | Parallel: `build` (ubuntu) + `build-exe` (windows-latest) | Schnelle CI, parallele Artefakte |
| **Single Instance** | Port-Check (8000) → existierende Instanz fokussieren (optional, v2) | MVP: erlauben; Nutzer sieht bei 2. Klick "Address already in use" |
| **Graceful Shutdown** | Daemon-Thread; Prozess-Exit beim Fenster-Schluss | Einfach, robust; Cleanup in v2 nachrüsten |

---

**Status: Implementation-ready** ✅
| WebView2 Runtime fehlt | Windows 10/11 hat WebView2 meist vorinstalliert; sonst Fallback-Dialog via `webview` |
| API-Key fehlt | Launcher prüft `AGNES_API_KEY` vor Start, klarer Error-Text |
| Windows Runner in CI langsam | Job läuft parallel zu `build`, nur ~60-90s extra |
