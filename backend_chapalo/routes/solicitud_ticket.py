from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.solicitud_ticket import SolicitudTicket
from models.premio import Premio
from models.cliente import Cliente
from models.ticket import Ticket

solicitud_ticket_bp = Blueprint("solicitud_ticket", __name__)

@solicitud_ticket_bp.route("/solicitudes", methods=["GET"])
@rol_requerido(["cliente"])
def obtener_solicitudes():
    cliente_id = int(get_jwt_identity())
    solicitudes = SolicitudTicket.query.filter_by(cliente_id=cliente_id).all()
    
    resultado = []
    for s in solicitudes:
        premio = Premio.query.get(s.premio_id)
        resultado.append({
            "solicitud_id": s.solicitud_id,
            "premio_nombre": premio.nombre if premio else "Premio no encontrado",
            "cantidad": s.cantidad,
            "estado": s.estado,
            "fecha_solicitud": s.fecha_solicitud.isoformat()
        })
    
    return jsonify(resultado), 200

@solicitud_ticket_bp.route("/solicitudes", methods=["POST"])
@rol_requerido(["cliente"])
def crear_solicitud():
    cliente_id = int(get_jwt_identity())
    data = request.get_json()
    
    premio_id = data.get("premio_id")
    cantidad = data.get("cantidad", 1)
    
    if not premio_id or cantidad < 1:
        return jsonify({"error": "Datos inválidos"}), 400
    
    premio = Premio.query.get(premio_id)
    if not premio:
        return jsonify({"error": "Premio no encontrado"}), 404
    
    solicitud = SolicitudTicket(
        cliente_id=cliente_id,
        premio_id=premio_id,
        cantidad=cantidad
    )
    
    db.session.add(solicitud)
    db.session.commit()
    
    return jsonify({
        "msg": "Solicitud creada exitosamente",
        "solicitud_id": solicitud.solicitud_id
    }), 201

@solicitud_ticket_bp.route("/admin/solicitudes/pendientes", methods=["GET"])
@rol_requerido(["admin"])
def obtener_solicitudes_pendientes():
    solicitudes = SolicitudTicket.query.filter_by(estado="pendiente").all()
    
    resultado = []
    for s in solicitudes:
        cliente = Cliente.query.get(s.cliente_id)
        premio = Premio.query.get(s.premio_id)
        resultado.append({
            "solicitud_id": s.solicitud_id,
            "cliente_dni": cliente.dni if cliente else "N/A",
            "cliente_nombre": f"{cliente.nombres} {cliente.apellidos}" if cliente else "N/A",
            "premio_nombre": premio.nombre if premio else "N/A",
            "cantidad": s.cantidad,
            "estado": s.estado,
            "fecha_solicitud": s.fecha_solicitud.isoformat()
        })
    
    return jsonify(resultado), 200

@solicitud_ticket_bp.route("/admin/solicitudes/<int:solicitud_id>/autorizar", methods=["PUT"])
@rol_requerido(["admin"])
def autorizar_solicitud(solicitud_id):
    solicitud = SolicitudTicket.query.get(solicitud_id)
    if not solicitud or solicitud.estado != "pendiente":
        return jsonify({"error": "Solicitud no válida"}), 404

    solicitud.estado = "aprobado"
    db.session.commit()
    return jsonify({"msg": "Solicitud aprobada"}), 200

@solicitud_ticket_bp.route("/admin/solicitudes/<int:solicitud_id>/rechazar", methods=["PUT"])
@rol_requerido(["admin"])
def rechazar_solicitud(solicitud_id):
    solicitud = SolicitudTicket.query.get(solicitud_id)
    if not solicitud or solicitud.estado != "pendiente":
        return jsonify({"error": "Solicitud no válida"}), 404

    solicitud.estado = "rechazado"
    db.session.commit()
    return jsonify({"msg": "Solicitud rechazada"}), 200

