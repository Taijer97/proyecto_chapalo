from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.cliente import Cliente

clientes_admin_bp = Blueprint("clientes_admin", __name__)

@clientes_admin_bp.route("/clientes/pendientes", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def listar_clientes_pendientes():
    pendientes = Cliente.query.filter_by(autorizado=False).filter(Cliente.suscripcion.isnot(None)).all()

    resultado = []
    for c in pendientes:
        resultado.append({
            "id": c.id,
            "dni": c.dni,
            "nombres": c.nombres,
            "apellidos": c.apellidos,
            "correo": c.correo,
            "celular": c.celular,
            "suscripcion": c.suscripcion,
            "fecha_suscripcion": c.fecha_suscripcion.isoformat() if c.fecha_suscripcion else None,
            "codigo_participante": c.codigo_participante
        })

    return jsonify(resultado), 200

# ============================
# 3. Autorizar cliente
# ============================
@clientes_admin_bp.route("/clientes/<int:cliente_id>/autorizar", methods=["PUT"])
@rol_requerido(["admin", "superadmin"])
def autorizar_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    if cliente.autorizado:
        return jsonify({"msg": "Cliente ya está autorizado"}), 200

    cliente.autorizado = True
    db.session.commit()
    return jsonify({"msg": f"Cliente {cliente.nombres} autorizado correctamente"}), 200
