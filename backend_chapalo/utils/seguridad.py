import bcrypt

def generar_hash(clave):
    # Convertir la clave a bytes y generar hash
    clave_bytes = clave.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(clave_bytes, salt).decode('utf-8')

def verificar_clave(clave_plana, clave_hash):
    # Convertir ambas a bytes para la verificación
    clave_bytes = clave_plana.encode('utf-8')
    hash_bytes = clave_hash.encode('utf-8')
    return bcrypt.checkpw(clave_bytes, hash_bytes)