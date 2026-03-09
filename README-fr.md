# NBLM2PPTX

Convertit des PDF ou images en PPTX avec **image de fond et texte éditable**. Ce dépôt est une implémentation fullstack **FastAPI (backend) + React (frontend)** avec téléchargement de PDF, progression en temps réel et export PPTX éditable.

> Inspiré/référencé depuis [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX).

[中文](README.md) | [简体中文](README-zh-CN.md) | [繁體中文](README-zh-TW.md) | [日本語](README-ja.md) | [Español](README-es.md) | [Français](README-fr.md)

## Stack technique

- **Backend** : FastAPI, PyMuPDF, Google Gemini (OCR de mise en page), OpenCV (couleur/recadrage), python-pptx
- **Frontend** : React, Vite, WebSocket (progression)
- **Flux** : PDF → images de page → Gemini analyse de mise en page → couleur/recadrage/nettoyage de fond → composition PPTX

## Démarrage rapide

### Docker (recommandé)

```bash
export GEMINI_API_KEY=votre_clé_API
./scripts/run-docker.sh
```

### Lancement local en une commande

```bash
./scripts/build-and-serve.sh
```

Si `backend/.env` est absent, il est copié depuis `backend/.env.example` ; éditez et renseignez `GEMINI_API_KEY` puis relancez. Puis accédez à <http://127.0.0.1:8000>, documentation API sur <http://127.0.0.1:8000/docs>.

### Étape par étape (développement)

```bash
# Backend
cd backend && cp .env.example .env && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend (autre terminal)
cd frontend && npm install && npm run dev
```

## Variables d'environnement

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | **Requis**. Clé API Gemini pour l’OCR de mise en page. |
| `UPLOAD_DIR` | Répertoire des téléchargements et tâches, par défaut `./uploads`. |
| `GEMINI_LAYOUT_MODEL` | Optionnel, par défaut `gemini-2.5-flash`. |
| `GEMINI_MAX_RPM` | Optionnel ; en niveau gratuit 2.5 Flash, recommandé `5`. |

Documentation complète dans [README.md](README.md). Index de la documentation dans [docs/INDEX.md](docs/INDEX.md).
