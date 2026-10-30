# ssm-parameter-store-pr

Sube y descarga variables de entorno en una cuenta de AWS, en el ambiente `dev`, con AWS Systems Manager Parameter Store.

Hoy los scripts solo aceptan `dev`. Cada variable queda en `/ssm-parameter-store-pr/dev/<CLAVE>`.

La práctica, con los retos, está en [docs/practica.md](docs/practica.md).

## Requisitos

- Python 3.14 instalado en tu máquina
- Una cuenta de AWS
- Un usuario de IAM con una política que solo permita esta ruta y sus parámetros:
  - `arn:aws:ssm:[REGION]:[ID-CUENTA]:parameter/ssm-parameter-store-pr/dev`
  - `arn:aws:ssm:[REGION]:[ID-CUENTA]:parameter/ssm-parameter-store-pr/dev/*`
- AWS CLI configurado en tu máquina con ese usuario

Esas tres partes están explicadas aquí:

- [Variables de entorno, secretos y AWS Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/003-Variables-de-entorno-secretos-y-AWS-Parameter-Store.md)
- [Políticas y usuarios de IAM para Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/002-Politicas-y-usuarios-de-IAM-para-Parameter-Store.md)
- [Configurar un usuario de AWS en tu máquina](https://github.com/sakaramos/sakaramos/blob/main/posts/001-Configurar-un-usuario-de-AWS-en-tu-m%C3%A1quina.md)

Sin esa política, el script de subida no puede crear los parámetros de `dev`.

## Instalación

```bash
git clone https://github.com/sakaramos/ssm-parameter-store-pr.git
cd ssm-parameter-store-pr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para comprobar que las credenciales ya están configuradas en el ambiente:

```bash
python app/test_aws.py
```

Si la conexión es correcta, imprime la cuenta y el usuario. Al clonar todavía no hay parámetros en tu cuenta, así que no hay nada que descargar. Sube el archivo de ejemplo:

```bash
python scripts/upload_parameters.py .env.example
```

Eso crea los parámetros de `dev` en tu AWS. A partir de ahí puedes descargarlos y arrancar la API:

```bash
python scripts/download_parameters.py dev
cp .env.dev .env
set -a
source .env
set +a
uvicorn app.main:app --reload
```

`source .env` carga las variables en el ambiente. La API usa esas variables. No lee el archivo.

- API: http://127.0.0.1:8000
- Documentación: http://127.0.0.1:8000/docs
- `GET /health` responde `{"status": "ok"}`
- `GET /env` devuelve el ambiente y los nombres de las variables que encontró. No devuelve los valores

`.env` no se sube al repositorio. `.env.example` es el archivo de ejemplo. La descarga escribe `.env.dev`.

## Scripts

### Subir

```bash
python scripts/upload_parameters.py .env.example
```

El parámetro es la ruta del archivo. El archivo tiene que incluir `ENV=dev`. El script lee cada línea `CLAVE=valor` y la guarda en `/ssm-parameter-store-pr/dev/CLAVE`. Si el parámetro ya existe, reemplaza el valor. Si quitaste una variable del archivo, borra ese parámetro en Parameter Store.

### Descargar

```bash
python scripts/download_parameters.py dev
```

El parámetro es el ambiente. El script lee `/ssm-parameter-store-pr/dev` y escribe `.env.dev`. La primera línea es `ENV=dev`.
