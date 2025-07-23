from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from models.solicitud_ticket import SolicitudTicket
from models.premio import Premio
from models.cliente import Cliente
from models.ticket import Ticket
from app import db

solicitudes_admin_bp = Blueprint("solicitudes_admin", __name__)

@solicitudes_admin_bp.route("/solicitudes/pendientes", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def obtener_solicitudes_pendientes():
    solicitudes = SolicitudTicket.query.filter_by(estado="pendiente").all()
    resultado = []
    for s in solicitudes:
        cliente = Cliente.query.get(s.cliente_id)
        premio = Premio.query.get(s.premio_id)
        resultado.append({
            "solicitud_id": s.solicitud_id,
            "cliente_dni": cliente.dni,
            "cliente_nombre": f"{cliente.nombres} {cliente.apellidos}",
            "premio_nombre": premio.nombre if premio else "N/D",
            "cantidad": s.cantidad,
            "fecha_solicitud": s.fecha_solicitud.isoformat()
        })
    return jsonify(resultado), 200

@solicitudes_admin_bp.route("/solicitudes/<int:solicitud_id>/<string:accion>", methods=["PUT"])
@rol_requerido(["admin", "superadmin"])
def responder_solicitud(solicitud_id, accion):
    solicitud = SolicitudTicket.query.get(solicitud_id)
    if not solicitud or solicitud.estado != "pendiente":
        return jsonify({"error": "Solicitud inválida o ya procesada"}), 404

    if accion == "autorizar":
        solicitud.estado = "aprobada"
        for i in range(solicitud.cantidad):
            # Generate unique ticket code
            import uuid
            codigo_ticket = f"TKT-{uuid.uuid4().hex[:8].upper()}"
            
            ticket = Ticket(
                cliente_id=solicitud.cliente_id,
                premio_id=solicitud.premio_id,  # Use the premio_id from the solicitud
                codigo_ticket=codigo_ticket
            )
            ticket.estado = 'autorizado'
            db.session.add(ticket)
        msg = "Solicitud aprobada y tickets asignados."
    elif accion == "rechazar":
        solicitud.estado = "rechazada"
        msg = "Solicitud rechazada."
    else:
        return jsonify({"error": "Acción no válida"}), 400

    db.session.commit()
    return jsonify({"msg": msg}), 200
