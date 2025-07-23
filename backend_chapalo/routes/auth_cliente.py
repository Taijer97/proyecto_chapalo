from flask import Blueprint, request, jsonify
from app import db
from models.cliente import Cliente
from utils.seguridad import generar_hash, verificar_clave
from flask_jwt_extended import create_access_token
import uuid

auth_cliente_bp = Blueprint("auth_cliente", __name__)

@auth_cliente_bp.route("/register", methods=["POST"])
def registrar_cliente():
    data = request.get_json()
    codigo_unico = str(uuid.uuid4())[:8]
    try:
        nuevo_cliente = Cliente(
            dni=data["dni"],
            apellidos=data["apellidos"],
            nombres=data["nombres"],
            correo=data["correo"],
            celular=data["celular"],
            clave_hash=generar_hash(data["clave"]),
            codigo_participante=codigo_unico,
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"msg": "Cliente registrado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@auth_cliente_bp.route("/login", methods=["POST"])
def login_cliente():
    data = request.get_json()
    dni = data.get("dni")
    clave = data.get("clave")

    cliente = Cliente.query.filter_by(dni=dni).first()
    if not cliente:
        return jsonify({"error": "DNI no registrado"}), 404

    if not verificar_clave(clave, cliente.clave_hash):
        return jsonify({"error": "Contraseña incorrecta"}), 401

    token = create_access_token(identity=str(cliente.id), additional_claims={"rol": "cliente"})
    print("📩 Datos recibidos:", request.json)
    return jsonify({
        "token": token,
        "cliente": {
            "id": cliente.id,
            "dni": cliente.dni,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "codigo_participante": cliente.codigo_participante,
            "autorizado": cliente.autorizado,
            "suscripcion": cliente.suscripcion
        }
    }), 200