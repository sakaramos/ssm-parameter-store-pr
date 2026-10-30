# Práctica para gestionar secretos de un proyecto de software en AWS Parameter Store

Esto no mide cuántos scripts conoces ni cuánto código sabes escribir. Mide si puedes resolver un problema de un proyecto real: las variables y los secretos no pueden quedar en el código, cada ambiente tiene los suyos y producción no se mezcla con el resto.

Este repositorio es una práctica. Tiene un proyecto en Python ya configurado y funcionando. Hoy se ejecuta en un solo ambiente, `dev`. La práctica pide poder ejecutarlo también en otros ambientes.

Antes de entrar en el problema, lee estas tres notas. Cada una responde una sola cosa:

- **Guía de conceptos:** [Variables de entorno, secretos y AWS Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/003-Variables-de-entorno-secretos-y-AWS-Parameter-Store.md)
- **Configuraciones iniciales en AWS:** [Políticas y usuarios de IAM para Parameter Store](https://github.com/sakaramos/sakaramos/blob/main/posts/002-Politicas-y-usuarios-de-IAM-para-Parameter-Store.md)
- **Configurar un usuario de AWS en tu máquina:** [Configurar un usuario de AWS en tu máquina](https://github.com/sakaramos/sakaramos/blob/main/posts/001-Configurar-un-usuario-de-AWS-en-tu-m%C3%A1quina.md)

> **Importante:** no olvides dejar una estrella en el [repositorio de la práctica](https://github.com/sakaramos/ssm-parameter-store-pr) y en [mi perfil](https://github.com/sakaramos). También puedes seguirme en [GitHub](https://github.com/sakaramos) y en [YouTube](https://www.youtube.com/@sakaramos).

## El problema

El proyecto ya sube, descarga y ejecuta sus variables, pero solo para `dev`. Los parámetros viven en `/ssm-parameter-store-pr/dev/CLAVE` y los scripts rechazan cualquier otro ambiente.

Hay dos retos. El primero es más fácil: gestionar un ambiente nuevo, `staging`, sin romper `dev`. El segundo es más ambiguo: explicar cómo se gestionaría `prod` sin mezclar credenciales.

Puedes hacer cualquiera de los dos, o todos los retos que se plantean abajo. Puedes usar la herramienta que quieras, incluida una IA. Lo que cuenta es qué decides, por qué y cómo queda funcionando.

## Qué hace el proyecto

Es una API en Python. Las variables no van escritas en el código. Se cargan en el ambiente antes de arrancar.

Los scripts hablan con Parameter Store usando boto3. Hoy solo aceptan el ambiente `dev`.

- Subir: `python scripts/upload_parameters.py .env.dev`. El archivo tiene que traer `ENV=dev`. Cada línea `CLAVE=valor` queda en `/ssm-parameter-store-pr/dev/CLAVE`. Si el parámetro ya existe, se reemplaza. Si quitaste una variable del archivo, ese parámetro se borra.
- Descargar: `python scripts/download_parameters.py dev`. Lee esa ruta y escribe `.env.dev`.
- Ejecutar: copias ese archivo a `.env`, lo cargas en la terminal y arrancas la API. La API usa las variables del ambiente. No lee el archivo.

La forma de clonar, instalar y arrancar está en el [README](../README.md) del proyecto.

El proyecto está en [sakaramos/ssm-parameter-store-pr](https://github.com/sakaramos/ssm-parameter-store-pr).

## Los retos

### 1. Un ambiente nuevo: staging

Este es el reto más fácil. Hoy el proyecto solo sube y descarga `dev`. Hace falta otro ambiente, `staging`, con los mismos scripts.

Qué tienes que lograr:

- Poder subir un archivo de `staging` y descargarlo.
- Los parámetros quedan en `/ssm-parameter-store-pr/staging/CLAVE`.
- `dev` sigue funcionando igual.
- La política del usuario tiene que permitir esa ruta. Si no, AWS rechaza la llamada.

Quien quiera un extra: refactoriza el código, y escribe tests. El extra es opcional. El reto queda resuelto cuando `staging` se puede subir y descargar.

### 2. Producción sin mezclar credenciales

Este es el reto más difícil. No hay que desarrollar nada. Tampoco hay una respuesta correcta.

`dev` y `staging` sirven para practicar. Producción es otro caso: un error ahí afecta el servicio real. La pregunta es cómo lo gestionarías de forma segura, no cómo se suele hacer.

Responde y justifica cada punto:

- ¿Cómo gestionarías producción y sus variables?
- Según lo que hacen esos scripts, ¿qué permitirías en `prod` y qué no?
- ¿Permitirías borrar un parámetro de producción, o lo conservarías aunque ese ambiente ya no lo use?
- ¿Cómo harías un despliegue seguro para producción?
- ¿Qué otras limitaciones le pondrías a esa ruta para que un flujo pensado para `dev` no pueda modificarla?

La entrega es un documento en `docs/`, dentro de un pull request, con tus decisiones y la razón de cada una.

### 3. Otro servicio en la misma cuenta

Este reto es adicional. Hasta aquí la ruta solo separa por ambiente: `/ssm-parameter-store-pr/dev` y `/ssm-parameter-store-pr/staging`. Si en la misma cuenta hay otro servicio, sus parámetros no pueden quedar mezclados con los de este.

Haz que un segundo servicio funcione con sus propios ambientes y que la consulta distinga el servicio y el ambiente. Por ejemplo, `/pagos/dev/CLAVE` y `/pagos/staging/CLAVE`, aparte de `/ssm-parameter-store-pr/dev/CLAVE`.

Qué tienes que lograr:

- Subir y descargar cada servicio sin leer los parámetros del otro.
- Cada servicio conserva sus ambientes.
- La política permite solo las rutas de los servicios que ese usuario debe tocar.
