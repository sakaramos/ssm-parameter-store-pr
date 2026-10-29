# ssm-parameter-store-pr

Práctica para subir y gestionar parámetros y variables de entorno en AWS Systems Manager Parameter Store.

Antes de usar el proyecto, lee la guía. Ahí están el contexto y el paso a paso:

[Gestión de secretos y variables de entorno en AWS Systems Manager Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/Gestion-de-secretos-y-variables-de-entorno-en-AWS-System-Manager-Parameter-Store.md)

## Requisitos

- Python 3.14
- Cuenta de AWS con acceso a Systems Manager Parameter Store
- AWS configurado en tu máquina (credenciales y región)
- boto3, el SDK de AWS para Python. El proyecto lo usa para llamar a Parameter Store con esas credenciales
- La configuración de AWS está explicada en la guía

## Uso

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Documentación: http://127.0.0.1:8000/docs
- `GET /health` responde `{"status": "ok"}`
