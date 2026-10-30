import boto3

def main():
    try:
        client = boto3.client('sts')
        # STS es el servicio de AWS que genera y verifica credenciales de seguridad temporales y permisos limitados.

        identity = client.get_caller_identity()
        
        print("¡Conexión exitosa con AWS!")
        print(f"Cuenta ID : {identity.get('Account')}")
        print(f"Usuario ARN: {identity.get('Arn')}")
        
    except Exception as e:
        print("Error al conectar con AWS:")
        print(e)

if __name__ == "__main__":
    main()
