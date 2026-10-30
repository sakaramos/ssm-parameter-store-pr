"""
Script para descargar un ambiente de Parameter Store a un archivo .env.

Uso:
    python scripts/download_parameters.py dev

Lee los parametros de /ssm-parameter-store-pr/dev y escribe .env.dev.
"""

import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class ParameterStore:
    """
    Maneja la lectura de AWS Parameter Store.

    Baja las variables del ambiente pedido. Por ejemplo, dev sale de
    /ssm-parameter-store-pr/dev/DB_PASSWORD.
    No sube ni borra nada.
    """

    # Inicio del nombre: /ssm-parameter-store-pr/dev/DB_PASSWORD.
    PREFIX = "/ssm-parameter-store-pr"

    # Ambientes que este script puede descargar. Hoy solo dev.
    ALLOWED_ENVIRONMENTS = ("dev",)

    def __init__(self) -> None:
        """Abre la conexion con Parameter Store usando la configuracion de AWS de la maquina."""
        self._client = boto3.client("ssm")

    def download(self, environment: str) -> dict[str, str]:
        """
        Lee los parametros de ese ambiente.

        Returns:
            Las variables, sin ENV. Ejemplo: {"DB_PASSWORD": "dev-password-ejemplo"}.
        """
        environment = self._check_environment(environment)
        path = f"{self.PREFIX}/{environment}"
        variables: dict[str, str] = {}

        for name, value in self._parameters_under(path):
            key = name.removeprefix(f"{path}/")
            if not key or "/" in key:
                continue
            variables[key] = value

        if not variables:
            raise ValueError(f"No hay parametros en '{path}'.")
        return variables

    def _check_environment(self, environment: str) -> str:
        """
        Compara el ambiente del comando con ALLOWED_ENVIRONMENTS.

        Returns:
            El ambiente en minusculas. Ejemplo: dev.
        """
        environment = environment.strip().lower()
        if environment not in self.ALLOWED_ENVIRONMENTS:
            allowed = ", ".join(self.ALLOWED_ENVIRONMENTS)
            raise ValueError(
                f"El ambiente '{environment}' no esta disponible. Usa uno de estos: {allowed}."
            )
        return environment

    def _parameters_under(self, path: str) -> list[tuple[str, str]]:
        """
        Nombres y valores descifrados que existen dentro de path.

        Returns:
            Ejemplo: [("/ssm-parameter-store-pr/dev/DB_PASSWORD", "dev-password-ejemplo")].
        """
        found: list[tuple[str, str]] = []
        next_token = None
        while True:
            request = {"Path": path, "Recursive": True, "WithDecryption": True}
            if next_token:
                request["NextToken"] = next_token
            response = self._client.get_parameters_by_path(**request)
            found.extend((parameter["Name"], parameter["Value"]) for parameter in response.get("Parameters", []))
            next_token = response.get("NextToken")
            if not next_token:
                return found


class EnvFile:
    """
    Maneja el archivo .env que se va a escribir en la carpeta del proyecto.

    Para el ambiente dev escribe .env.dev, con la linea ENV=dev y el resto
    de variables que vinieron de AWS.
    """

    ENV_KEY = "ENV"

    def __init__(self, environment: str, variables: dict[str, str]) -> None:
        """Guarda el ambiente y las variables. El archivo se escribe en save."""
        self.environment = environment
        self.variables = variables
        self.path = Path(f".env.{environment}")

    def save(self) -> None:
        """
        Escribe el archivo .env.<ambiente>.

        La primera linea es ENV=dev. Despues van las variables en orden alfabetico.
        """
        lines = [f"{self.ENV_KEY}={self.environment}"]
        for key in sorted(self.variables):
            lines.append(f"{key}={self.variables[key]}")
        self.path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class DownloadCommand:
    """
    Maneja el comando con el que se ejecuta el script.

    python scripts/download_parameters.py dev
    toma ese ambiente, le pide a ParameterStore que lo lea y a EnvFile
    que escriba .env.dev.
    """

    def __init__(self, environment: str) -> None:
        """Guarda el ambiente escrito en el comando. AWS se consulta en run."""
        self._environment = environment

    @classmethod
    def from_terminal(cls) -> "DownloadCommand":
        """
        Toma el ambiente que viene despues del nombre del script.

        python scripts/download_parameters.py dev
        usa dev. Si no hay ambiente, muestra la ayuda y el programa termina.

        Returns:
            Un DownloadCommand con ese ambiente.
        """
        parser = argparse.ArgumentParser(description="Recibe el ambiente a descargar. Ejemplo: dev.")
        parser.add_argument("environment", help="Ambiente a descargar. Ejemplo: dev.")
        return cls(parser.parse_args().environment)

    def run(self) -> int:
        """
        Descarga el ambiente y escribe .env.<ambiente>.

        Returns:
            0 si termino bien. 1 si el ambiente o AWS fallaron.
        """
        try:
            store = ParameterStore()
            variables = store.download(self._environment)
            env_file = EnvFile(self._environment.strip().lower(), variables)
            env_file.save()
        except ValueError as error:
            print(f"Error de validacion: {error}", file=sys.stderr)
            return 1
        except ClientError as error:
            code = error.response.get("Error", {}).get("Code", "Unknown")
            message = error.response.get("Error", {}).get("Message", str(error))
            print(f"Error de AWS ({code}): {message}", file=sys.stderr)
            return 1
        except BotoCoreError as error:
            print(f"Error al hablar con AWS: {error}", file=sys.stderr)
            return 1
        except Exception as error:
            print(f"Error inesperado: {error}", file=sys.stderr)
            return 1

        print(f"Listo. Se descargaron {len(variables)} parametros en '{env_file.path}'.")
        return 0


if __name__ == "__main__":
    sys.exit(DownloadCommand.from_terminal().run())
