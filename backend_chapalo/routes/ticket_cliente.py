from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.ticket import Ticket
from models.premio import Premio
from models.premio import Premio
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
import uuid
from models.solicitud_ticket import SolicitudTicket

ticket_cliente_bp = Blueprint("ticket_cliente", __name__)

# ============================
# Generar tickets para un premio
# ============================
@ticket_cliente_bp.route("/generar-tickets", methods=["POST"])
@rol_requerido(["cliente"])
def generar_tickets():
    data = request.get_json()
    cliente_id = get_jwt_identity()
    premio_id = data.get("premio_id")
    cantidad = data.get("cantidad", 1)  # puede generar más de 1

    premio = Premio.query.get(premio_id)
    if not premio:
        return jsonify({"error": "Premio no encontrado"}), 404

    tickets_generados = []
    for _ in range(cantidad):
        codigo_ticket = "TICK-" + uuid.uuid4().hex[:8].upper()

        ticket = Ticket(
            cliente_id=cliente_id,
            premio_id=premio_id,
            codigo_ticket=codigo_ticket
        )
        db.session.add(ticket)
        tickets_generados.append(codigo_ticket)

    db.session.commit()
    return jsonify({"msg": "Tickets generados", "tickets": tickets_generados}), 201

# ============================
# Ver mis tickets generados
# ============================
@ticket_cliente_bp.route("/tickets", methods=["GET"])
@rol_requerido(["cliente"])
def ver_mis_tickets():
    cliente_id = get_jwt_identity()

    tickets = Ticket.query.filter_by(cliente_id=cliente_id).all()
    resultado = []

    for t in tickets:
        premio = Premio.query.get(t.premio_id)
        resultado.append({
            "codigo_ticket": t.codigo_ticket,
            "premio": premio.nombre,
            "fecha_sorteo": premio.fecha_sorteo.isoformat(),
            "imagen_url": premio.imagen_url
        })

    return jsonify(resultado), 200

@ticket_cliente_bp.route("/solicitar-chances", methods=["POST"])
@rol_requerido(["cliente"])
def solicitar_chances():
    data = request.get_json()
    cliente_id = get_jwt_identity()
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
        cantidad=cantidad,
        estado="pendiente"
    )

    db.session.add(solicitud)
    db.session.commit()

    return jsonify({"msg": "Solicitud enviada. Esperando autorización del administrador."}), 201