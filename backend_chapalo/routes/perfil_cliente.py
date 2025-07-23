from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.cliente import Cliente
from flask import request
from utils.seguridad import generar_hash

perfil_cliente_bp = Blueprint("perfil_cliente", __name__)

# ============================
# Ver perfil del cliente
# ============================
@perfil_cliente_bp.route("/perfil", methods=["GET"])
@rol_requerido(["cliente"])
def ver_perfil():
    cliente_id = get_jwt_identity()
    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    referido_por = None
    if cliente.referido_por_codigo:
        referente = Cliente.query.filter_by(codigo_referencia=cliente.referido_por_codigo).first()
        if referente:
            referido_por = {
                "nombres": referente.nombres,
                "apellidos": referente.apellidos,
                "codigo_participante": referente.codigo_participante
            }

    return jsonify({
        "dni": cliente.dni,
        "nombres": cliente.nombres,
        "apellidos": cliente.apellidos,
        "correo": cliente.correo,
        "celular": cliente.celular,
        "codigo_participante": cliente.codigo_participante,
        "codigo_referencia": cliente.codigo_referencia,
        "referido_por": referido_por,
        "suscripcion": cliente.suscripcion,
        "fecha_suscripcion": cliente.fecha_suscripcion.isoformat() if cliente.fecha_suscripcion else None,
        "autorizado": cliente.autorizado
    }), 200

# ============================
# Actualizar perfil del cliente
# ============================
@perfil_cliente_bp.route("/perfil", methods=["PUT"])
@rol_requerido(["cliente"])
def actualizar_perfil():
    cliente_id = get_jwt_identity()
    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    data = request.get_json()

    # Campos actualizables
    cliente.nombres = data.get("nombres", cliente.nombres)
    cliente.apellidos = data.get("apellidos", cliente.apellidos)
    cliente.celular = data.get("celular", cliente.celular)
    cliente.correo = data.get("correo", cliente.correo)

    # Si se envía nueva clave
    if data.get("clave"):
        cliente.clave_hash = generar_hash(data["clave"])

    try:
        db.session.commit()
        return jsonify({"msg": "Perfil actualizado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400