import os

from fastapi import FastAPI

app = FastAPI(title="ssm-parameter-store-pr")

# Nombres que el proyecto espera ya cargados en el ambiente.
APP_ENV_KEYS = ("DB_HOST", "DB_USER", "DB_PASSWORD", "API_KEY")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/env")
def environment() -> dict[str, str | list[str]]:
    """Nombres de las variables del proyecto que ya estan en el ambiente. No devuelve los valores."""
    loaded = [key for key in APP_ENV_KEYS if key in os.environ]
    return {"ENV": os.environ.get("ENV", ""), "variables": loaded}
