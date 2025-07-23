from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt

def rol_requerido(roles_permitidos):
    """
    Decorador para restringir acceso según el rol del token JWT.
    Ejemplo de uso:
        @rol_requerido(["admin", "superadmin"])
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            try:
                claims = get_jwt()
                print(f"Claims recibidos: {claims}")  # 🔍 Log temporal
                
                # Validar existencia del rol
                if "rol" not in claims:
                    print("❌ Error: Token sin campo 'rol'")  # 🔍 Log temporal
                    return jsonify({
                        "error": "Token inválido: falta 'rol'",
                        "claims": claims
                    }), 422

                # Validar que el rol esté en los permitidos
                print(f"🔍 Rol del token: '{claims['rol']}'")
                print(f"🔍 Roles permitidos: {roles_permitidos}")
                if claims["rol"] not in roles_permitidos:
                    print(f"❌ Acceso denegado: '{claims['rol']}' no está en {roles_permitidos}")
                    return jsonify({
                        "error": f"Acceso denegado para rol '{claims['rol']}'",
                        "roles_permitidos": roles_permitidos
                    }), 403

                return fn(*args, **kwargs)

            except Exception as e:
                return jsonify({
                    "error": f"Error en validación de rol: {str(e)}",
                    "tipo_error": type(e).__name__
                }), 422

        return decorated
    return wrapper