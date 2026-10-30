# ssm-parameter-store-pr

Práctica para subir y gestionar parámetros y variables de entorno en AWS Systems Manager Parameter Store.

Antes de usar el proyecto, lee la guía. Ahí están el contexto y el paso a paso:

[Gestión de secretos y variables de entorno en AWS Systems Manager Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/Gestion-de-secretos-y-variables-de-entorno-en-AWS-System-Manager-Parameter-Store.md)

## Requisitos

- Python 3.14 instalado en tu máquina
- Cuenta de AWS con acceso a Systems Manager Parameter Store
- AWS configurado en tu máquina (credenciales y región)
- boto3, el SDK de AWS para Python. El proyecto lo usa para llamar a Parameter Store con esas credenciales
- La configuración de AWS está explicada en la guía

## Bajar el repositorio

```bash
git clone https://github.com/sakaramos/ssm-parameter-store-pr.git
cd ssm-parameter-store-pr
```

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

## Subir variables

Primero configura AWS en tu máquina:

```bash
aws configure
```

Cómo hacerlo está en la [documentación oficial de AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) y en la guía de este proyecto.

Con el repositorio clonado y el entorno virtual activo, sube o actualiza el ambiente `dev` pasándole la ruta del archivo:

```bash
python scripts/upload_parameters.py .env.dev
```

- Ambientes disponibles: `dev`
- El archivo tiene que incluir `ENV=dev`
- Prefijo configurado: `/ssm-parameter-store-pr`
- Cada variable queda en `/ssm-parameter-store-pr/dev/<CLAVE>`

Si vuelves a ejecutar el comando, los valores que siguen en el archivo se reemplazan. Si quitaste una variable del archivo, ese parámetro se borra en Parameter Store.
