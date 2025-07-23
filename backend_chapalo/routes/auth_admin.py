from flask import Blueprint, request, jsonify
from app import db
from models.administrador import Administrador
from utils.seguridad import generar_hash, verificar_clave
from flask_jwt_extended import create_access_token

auth_admin_bp = Blueprint("auth_admin", __name__)

@auth_admin_bp.route("/register", methods=["POST"])
def registrar_admin():
    data = request.get_json()
    try:
        nuevo_admin = Administrador(
            dni=data["dni"],
            apellidos=data["apellidos"],
            nombres=data["nombres"],
            correo=data["correo"],
            celular=data["celular"],
            rol=data.get("rol", "admin"),
            clave_hash=generar_hash(data["clave"]),
        )
        db.session.add(nuevo_admin)
        db.session.commit()
        return jsonify({"msg": "Administrador registrado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_admin_bp.route("/login", methods=["POST"])
def login_admin():
    data = request.get_json()
    dni = data.get("dni")
    clave = data.get("clave")

    admin = Administrador.query.filter_by(dni=dni).first()
    if not admin:
        return jsonify({"error": "DNI no registrado"}), 404

    if not verificar_clave(clave, admin.clave_hash):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    token = create_access_token(identity=str(admin.id), additional_claims={"rol": admin.rol})

    return jsonify({
        "token": token,
        "admin": {
            "id": admin.id,
            "dni": admin.dni,
            "nombres": admin.nombres,
            "apellidos": admin.apellidos,
            "rol": admin.rol
        }
    }), 200