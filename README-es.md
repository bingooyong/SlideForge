# NBLM2PPTX

Convierte PDF o imágenes en PPTX con **imagen de fondo y texto editable**. Este repositorio es una implementación fullstack **FastAPI (backend) + React (frontend)** con subida de PDF, progreso en tiempo real y exportación de PPTX editable.

> Inspirado/referenciado en [laihenyi/NBLM2PPTX](https://github.com/laihenyi/NBLM2PPTX).

[中文](README.md) | [简体中文](README-zh-CN.md) | [繁體中文](README-zh-TW.md) | [日本語](README-ja.md) | [Español](README-es.md) | [Français](README-fr.md)

## Stack técnico

- **Backend**: FastAPI, PyMuPDF, Google Gemini (OCR de diseño), OpenCV (color/recorte), python-pptx
- **Frontend**: React, Vite, WebSocket (progreso)
- **Flujo**: PDF → imágenes de página → Gemini análisis de diseño → color/recorte/limpieza de fondo → composición PPTX

## Inicio rápido

### Docker (recomendado)

```bash
export GEMINI_API_KEY=tu_clave_API
./scripts/run-docker.sh
```

### Inicio local con un comando

```bash
./scripts/build-and-serve.sh
```

Si falta `backend/.env`, se copia desde `backend/.env.example`; edita y rellena `GEMINI_API_KEY` y vuelve a ejecutar. Luego accede a <http://127.0.0.1:8000>, documentación API en <http://127.0.0.1:8000/docs>.

### Paso a paso (desarrollo)

```bash
# Backend
cd backend && cp .env.example .env && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend (otra terminal)
cd frontend && npm install && npm run dev
```

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `GEMINI_API_KEY` | **Requerido**. Clave de Gemini API para OCR de diseño. |
| `UPLOAD_DIR` | Directorio de subidas y tareas, por defecto `./uploads`. |
| `GEMINI_LAYOUT_MODEL` | Opcional, por defecto `gemini-2.5-flash`. |
| `GEMINI_MAX_RPM` | Opcional; en capa gratuita 2.5 Flash se recomienda `5`. |

Documentación completa en [README.md](README.md). Índice de documentación en [docs/INDEX.md](docs/INDEX.md).
