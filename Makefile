.PHONY: install build backend frontend start clean

install: ## Vollständige Installation (Python + Node + Build)
	bash scripts/install.sh

build: ## Frontend + Skills bauen
	cd frontend && npm run build
	cd backend && python -m app.services.skill_extractor

backend: ## Backend-Abhängigkeiten installieren
	cd backend && pip install -r requirements.txt
	cd backend && python -m app.services.skill_extractor

frontend: ## Frontend bauen
	cd frontend && npm install && npm run build

start: ## Produktions-Server starten (AGNES_API_KEY muss gesetzt sein)
	@if [ -z "$${AGNES_API_KEY}" ]; then \
		echo "AGNES_API_KEY nicht gesetzt!"; \
		echo "  export AGNES_API_KEY=sk-..."; \
		exit 1; \
	fi
	cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

clean: ## Build-Artefakte entfernen
	rm -rf frontend/dist frontend/node_modules
	rm -rf backend/.venv backend/__pycache__ backend/**/__pycache__
	rm -rf backend/skills/extracted
	rm -f agnes.log
	rm -rf .pytest_cache

help: ## Hilfe anzeigen
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
