from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.cliente import Cliente
from models.ticket import Ticket

suscripciones_admin_bp = Blueprint("suscripciones_admin", __name__)

@suscripciones_admin_bp.route("/suscripciones/pendientes", methods=["GET"])
@rol_requerido(["admin", "superadmin"])  # ✅ Acepta ambos roles
def obtener_suscripciones_pendientes():
    clientes = Cliente.query.filter(Cliente.autorizado == 0).filter(Cliente.suscripcion.isnot(None)).all()
    resultado = []
    for cliente in clientes:
        resultado.append({
            "id": cliente.id,
            "dni": cliente.dni,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "suscripcion": cliente.suscripcion,
            "fecha_suscripcion": cliente.fecha_suscripcion.isoformat() if cliente.fecha_suscripcion else None,
            "comprobante_url": cliente.comprobante_url,
        })
    return jsonify(resultado), 200

@suscripciones_admin_bp.route("/suscripciones/autorizar/<int:cliente_id>", methods=["PUT"])
@rol_requerido(["admin"])
def autorizar_suscripcion(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente or not cliente.suscripcion:
        return jsonify({"error": "Cliente no válido o sin suscripción"}), 404

    cliente.autorizado = True
    db.session.commit()

    for _ in range(cliente.tickets_por_suscripcion):
        db.session.add(Ticket(cliente_id=cliente.id, premio_id=None, estado="pendiente"))

    db.session.commit()
    return jsonify({"msg": "Suscripción autorizada y tickets asignados."}), 200
