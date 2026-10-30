"""
Script para subir un archivo .env a Parameter Store.

Uso:
    python scripts/upload_parameters.py .env.dev

Nombre de cada parametro:
    /ssm-parameter-store-pr/<ambiente>/<CLAVE>
"""

import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


class EnvFile:
    """
    Maneja el archivo .env que se recibio en el comando.

    Lo lee, saca el ambiente de la linea ENV=dev y deja las demas variables
    listas para subir. No llama a AWS.
    """

    # Ambientes que este archivo puede declarar. Hoy solo dev.
    ALLOWED_ENVIRONMENTS = ("dev",)

    # Clave del .env de donde sale el ambiente. La linea es ENV=dev.
    ENV_KEY = "ENV"

    def __init__(self, path: Path) -> None:
        """Lee path y llena environment y variables. Falla si el archivo no sirve."""
        self.path = path
        self.environment, self.variables = self._load()

    def _load(self) -> tuple[str, dict[str, str]]:
        """
        Lee las lineas CLAVE=valor y saca el ambiente de ENV.

        Returns:
            El ambiente y las variables a subir, sin ENV.
            Ejemplo: ("dev", {"DB_PASSWORD": "dev-password-ejemplo"}).
        """
        variables = self._read_lines()
        environment = self._environment_from(variables)
        to_upload = {key: value for key, value in variables.items() if key != self.ENV_KEY}
        if not to_upload:
            raise ValueError(f"El archivo '{self.path}' solo tiene {self.ENV_KEY}. No hay parametros para subir.")
        return environment, to_upload

    def _read_lines(self) -> dict[str, str]:
        """
        Lee las lineas CLAVE=valor. Ignora vacias y las que empiezan con #.

        Returns:
            Todas las variables, incluida ENV.
        """
        if not self.path.is_file():
            raise FileNotFoundError(
                f"No existe el archivo '{self.path}'. Ejemplo: python scripts/upload_parameters.py .env.dev"
            )

        variables: dict[str, str] = {}
        for line_number, raw_line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"La linea {line_number} de '{self.path}' no tiene el formato CLAVE=valor.")

            key, value = line.split("=", 1)
            key = key.strip()
            if not key:
                raise ValueError(f"La linea {line_number} de '{self.path}' tiene la clave vacia.")
            variables[key] = value

        if not variables:
            raise ValueError(f"El archivo '{self.path}' no tiene variables para subir.")
        return variables

    def _environment_from(self, variables: dict[str, str]) -> str:
        """
        Toma ENV, le quita espacios, lo pasa a minusculas y lo compara con ALLOWED_ENVIRONMENTS.

        Returns:
            El ambiente. Ejemplo: dev.
        """
        raw = variables.get(self.ENV_KEY)
        if raw is None or not raw.strip():
            allowed = ", ".join(self.ALLOWED_ENVIRONMENTS)
            raise ValueError(
                f"El archivo '{self.path}' no tiene la variable {self.ENV_KEY}. "
                f"Agrega una linea {self.ENV_KEY}=dev. Ambientes disponibles: {allowed}."
            )

        environment = raw.strip().lower()
        if environment not in self.ALLOWED_ENVIRONMENTS:
            allowed = ", ".join(self.ALLOWED_ENVIRONMENTS)
            raise ValueError(
                f"El ambiente '{environment}' no esta disponible. Usa uno de estos: {allowed}."
            )
        return environment


class ParameterStore:
    """
    Maneja AWS Parameter Store.

    Sube cada variable del archivo como un parametro, por ejemplo
    /ssm-parameter-store-pr/dev/DB_PASSWORD.
    Si el parametro ya existia, reemplaza el valor.
    Si una variable se quito del archivo, borra ese parametro en AWS.
    """

    # Inicio del nombre: /ssm-parameter-store-pr/dev/DB_PASSWORD.
    PREFIX = "/ssm-parameter-store-pr"

    def __init__(self) -> None:
        """Abre la conexion con Parameter Store usando la configuracion de AWS de la maquina."""
        self._client = boto3.client("ssm")

    def upload(self, environment: str, variables: dict[str, str]) -> None:
        """
        Guarda cada variable como parametro de ese ambiente.

        DB_PASSWORD=dev-password-ejemplo con environment "dev" queda en
        /ssm-parameter-store-pr/dev/DB_PASSWORD.
        """
        for key, value in variables.items():
            name = self._name(environment, key)
            self._client.put_parameter(
                Name=name,
                Value=value,
                Type="SecureString",
                Overwrite=True,
            )
            print(f"Subido: {name}")

    def delete_missing(self, environment: str, variables: dict[str, str]) -> int:
        """
        Borra parametros de ese ambiente cuyo nombre no esta en variables.

        Si en AWS existe /ssm-parameter-store-pr/dev/API_KEY y variables no trae
        API_KEY, ese parametro se elimina.

        Returns:
            Cuantos parametros borro. 0 si no sobraba ninguno.
        """
        path = f"{self.PREFIX}/{environment}"
        names_in_file = {self._name(environment, key) for key in variables}
        deleted = 0

        for name in self._names_under(path):
            if name in names_in_file:
                continue
            self._client.delete_parameter(Name=name)
            print(f"Eliminado: {name}")
            deleted += 1
        return deleted

    def _name(self, environment: str, key: str) -> str:
        """
        Nombre completo de una clave en un ambiente.

        Returns:
            Con environment "dev" y key "DB_PASSWORD":
            "/ssm-parameter-store-pr/dev/DB_PASSWORD".
        """
        return f"{self.PREFIX}/{environment}/{key}"

    def _names_under(self, path: str) -> list[str]:
        """
        Nombres que ya existen en Parameter Store dentro de path.

        Returns:
            Ejemplo, con path "/ssm-parameter-store-pr/dev":
            ["/ssm-parameter-store-pr/dev/API_KEY"].
        """
        names: list[str] = []
        next_token = None
        while True:
            request = {"Path": path, "Recursive": True}
            if next_token:
                request["NextToken"] = next_token
            response = self._client.get_parameters_by_path(**request)
            names.extend(parameter["Name"] for parameter in response.get("Parameters", []))
            next_token = response.get("NextToken")
            if not next_token:
                return names


class UploadCommand:
    """
    Maneja el comando con el que se ejecuta el script.

    python scripts/upload_parameters.py .env.dev
    toma esa ruta, le pide a EnvFile que lea el archivo y a ParameterStore
    que suba las variables y borre las que ya no estan.
    """

    def __init__(self, path: Path) -> None:
        """Guarda la ruta. El archivo todavia no se lee; eso ocurre en run."""
        self._path = path

    @classmethod
    def from_terminal(cls) -> "UploadCommand":
        """
        Toma la ruta que viene despues del nombre del script.

        python scripts/upload_parameters.py .env.dev
        usa .env.dev. Si no hay ruta, muestra la ayuda y el programa termina.

        Returns:
            Un UploadCommand con esa ruta.
        """
        parser = argparse.ArgumentParser(description="Recibe la ruta de un archivo .env.")
        parser.add_argument("file", help="Ruta del archivo. Ejemplo: .env.dev")
        return cls(Path(parser.parse_args().file))

    def run(self) -> int:
        """
        Lee el .env, sube sus variables y borra en AWS las que ya no vienen.

        Returns:
            0 si termino bien. 1 si el archivo, el ambiente o AWS fallaron.
        """
        try:
            env_file = EnvFile(self._path)
            store = ParameterStore()
            store.upload(env_file.environment, env_file.variables)
            deleted = store.delete_missing(env_file.environment, env_file.variables)
        except ValueError as error:
            print(f"Error de validacion: {error}", file=sys.stderr)
            return 1
        except FileNotFoundError as error:
            print(f"Error de archivo: {error}", file=sys.stderr)
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

        print(
            f"Listo. Se subieron {len(env_file.variables)} parametros "
            f"y se eliminaron {deleted} en el ambiente '{env_file.environment}'."
        )
        return 0


if __name__ == "__main__":
    sys.exit(UploadCommand.from_terminal().run())
