#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd 2>/dev/null || echo "$SCRIPT_DIR")"

# ── Farben ──────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*"; }

# ── Prüfen: Python 3.12+ ───────────────────────────────────────
check_python() {
    if ! command -v python3 &>/dev/null; then
        err "Python 3 nicht gefunden. Bitte installieren: https://python.org"
        exit 1
    fi
    local ver
    ver=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
    local major="${ver%.*}"
    local minor="${ver#*.}"
    if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 12 ]; }; then
        err "Python 3.12+ erforderlich (gefunden: $(python3 --version))"
        exit 1
    fi
    ok "Python $(python3 --version)"
}

# ── Prüfen: Node 22+ ────────────────────────────────────────────
check_node() {
    if ! command -v node &>/dev/null; then
        err "Node.js nicht gefunden. Bitte installieren: https://nodejs.org"
        exit 1
    fi
    local ver
    ver=$(node --version 2>&1 | grep -oP '\d+')
    if [ "$ver" -lt 22 ]; then
        warn "Node.js 22+ empfohlen (gefunden: $(node --version))"
    else
        ok "Node $(node --version)"
    fi
    if ! command -v npm &>/dev/null; then
        err "npm nicht gefunden"
        exit 1
    fi
    ok "npm $(npm --version)"
}

# ── Prüfen: ImageMagick ─────────────────────────────────────────
check_imagemagick() {
    if ! command -v convert &>/dev/null; then
        warn "ImageMagick nicht gefunden – Favicon-Erstellung übersprungen"
        info "  Installieren: sudo apt install imagemagick  (Linux)"
        info "  Installieren: brew install imagemagick      (macOS)"
    else
        ok "ImageMagick $(convert --version 2>&1 | head -1)"
    fi
}

# ── Backend-Setup ────────────────────────────────────────────────
setup_backend() {
    echo ""
    info "── Backend ──"
    cd "$PROJECT_DIR/backend"

    if [ ! -f requirements.txt ]; then
        err "requirements.txt nicht gefunden in $PWD"
        exit 1
    fi

    if [ -d .venv ]; then
        warn "Virtuelle Umgebung existiert bereits – überspringe"
    else
        python3 -m venv .venv
        ok "Virtuelle Umgebung erstellt: .venv"
    fi

    source .venv/bin/activate
    pip install -q -r requirements.txt
    ok "Python-Abhängigkeiten installiert"

    python -m app.services.skill_extractor
    ok "Skills extrahiert"
}

# ── Frontend-Setup ───────────────────────────────────────────────
setup_frontend() {
    echo ""
    info "── Frontend ──"
    cd "$PROJECT_DIR/frontend"

    if [ ! -f package.json ]; then
        err "package.json nicht gefunden in $PWD"
        exit 1
    fi

    if [ -d node_modules ]; then
        warn "node_modules existiert bereits – überspringe npm install"
    else
        npm install
        ok "Node-Abhängigkeiten installiert"
    fi

    npm run build
    ok "Frontend gebaut (dist/)"
}

# ── .env anlegen (falls nicht vorhanden) ─────────────────────────
setup_env() {
    echo ""
    info "── Umgebungsvariablen ──"
    cd "$PROJECT_DIR"

    if [ -f .env ]; then
        warn ".env existiert bereits – überspringe"
    else
        if [ -f .env.example ]; then
            cp .env.example .env
            warn ".env aus .env.example erstellt"
            info "  Bitte AGNES_API_KEY in .env setzen!"
        else
            cat > .env << 'EOF'
AGNES_API_KEY=sk-your-key-here
LOG_LEVEL=INFO
EOF
            warn ".env mit Platzhalter erstellt"
            info "  Bitte AGNES_API_KEY in .env setzen!"
        fi
    fi
}

# ── Start-Skript erzeugen ────────────────────────────────────────
create_start_script() {
    echo ""
    info "── Start-Skript ──"
    cd "$PROJECT_DIR"

    cat > start.sh << 'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# .env laden
if [ -f .env ]; then
    set -a; source .env; set +a
fi

BACKEND_DIR="$PWD/backend"
FRONTEND_DIST="$PWD/frontend/dist"

# Prüfe API-Key
if [ -z "${AGNES_API_KEY:-}" ]; then
    echo "[ERROR] AGNES_API_KEY nicht gesetzt!"
    echo "  Bitte in .env eintragen oder als Umgebungsvariable setzen."
    exit 1
fi

# Virtuelle Umgebung aktivieren
if [ -d "$BACKEND_DIR/.venv" ]; then
    source "$BACKEND_DIR/.venv/bin/activate"
fi

echo "[INFO] Starte Agnes AI Server auf http://localhost:8000"
echo "[INFO] Drücke Ctrl+C zum Beenden"
cd "$BACKEND_DIR"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
SCRIPT
    chmod +x start.sh
    ok "start.sh erstellt"
}

# ── Hauptablauf ──────────────────────────────────────────────────
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║     Agnes AI – Installer             ║${NC}"
    echo -e "${CYAN}║     Edit Image Workflow              ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════╝${NC}"
    echo ""

    check_python
    check_node
    check_imagemagick

    setup_env
    setup_backend
    setup_frontend
    create_start_script

    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Installation abgeschlossen!      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════╝${NC}"
    echo ""
    echo "  Nächste Schritte:"
    echo "    1. AGNES_API_KEY in .env setzen"
    echo "    2. ./start.sh"
    echo "    3. http://localhost:8000 öffnen"
    echo ""
}

main
