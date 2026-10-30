# ssm-parameter-store-pr

Práctica para subir y descargar variables de entorno en AWS Systems Manager Parameter Store.

La guía, con el contexto y el paso a paso, está en [Gestión de secretos y variables de entorno en AWS Systems Manager Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/Gestion-de-secretos-y-variables-de-entorno-en-AWS-System-Manager-Parameter-Store.md).

## Requisitos

- Python 3.14 instalado en tu máquina

## Instalación y ejecución

```bash
git clone https://github.com/sakaramos/ssm-parameter-store-pr.git
cd ssm-parameter-store-pr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/download_parameters.py dev
cp .env.dev .env
set -a
source .env
set +a
uvicorn app.main:app --reload
```

`download_parameters.py` escribe `.env.dev` con lo que hay en Parameter Store. Esa descarga usa la configuración de AWS de la sección de abajo. `source .env` carga las variables en el ambiente. La API usa esas variables. No lee el archivo.

- API: http://127.0.0.1:8000
- Documentación: http://127.0.0.1:8000/docs
- `GET /health` responde `{"status": "ok"}`
- `GET /env` devuelve el ambiente y los nombres de las variables que encontró en el ambiente. No devuelve los valores

`.env` no se sube al repositorio. `.env.example` es el archivo de ejemplo. La descarga escribe `.env.dev`.

## Parameter Store

Para subir o descargar variables hace falta una cuenta de AWS con acceso a Systems Manager Parameter Store y AWS CLI configurado:

```bash
aws configure
```

Cómo hacerlo está en la [documentación oficial](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html). El proyecto usa boto3, el SDK de AWS para Python, para llamar a Parameter Store con esa configuración.

- Ambientes disponibles: `dev`
- Prefijo: `/ssm-parameter-store-pr`
- Cada variable queda en `/ssm-parameter-store-pr/dev/<CLAVE>`

### Subir

```bash
python scripts/upload_parameters.py .env.dev
```

El parámetro es la ruta del archivo. El archivo tiene que incluir `ENV=dev`. Si el parámetro ya existe, el valor se reemplaza. Si quitaste una variable del archivo, ese parámetro se borra en Parameter Store.

### Descargar

```bash
python scripts/download_parameters.py dev
```

El parámetro es el ambiente. El script lee `/ssm-parameter-store-pr/dev` y escribe `.env.dev`. La primera línea es `ENV=dev`. Para usarlo en la API, cópialo a `.env` y cárgalo como en la instalación.
