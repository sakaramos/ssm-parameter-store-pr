# ssm-parameter-store-pr
Práctica para la gestión de secretos y variables de entorno en AWS System Manager Parameter Store

## Arranque

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda en http://127.0.0.1:8000. Documentación interactiva: http://127.0.0.1:8000/docs. `GET /health` responde `{"status": "ok"}`.
