from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.ticket import Ticket
from models.cliente import Cliente
from models.premio import Premio
from models.ganador import Ganador
import random
from datetime import date

sorteo_admin_bp = Blueprint("sorteo_admin", __name__)

# ============================
# Sorteo de ganador
# ============================
@sorteo_admin_bp.route("/sorteo/<int:premio_id>", methods=["POST"])
@rol_requerido(["admin", "superadmin"])
def realizar_sorteo(premio_id):
    tickets = Ticket.query.filter_by(premio_id=premio_id).all()

    if not tickets:
        return jsonify({"error": "No hay tickets para este premio"}), 404

    ticket_ganador = random.choice(tickets)
    cliente = Cliente.query.get(ticket_ganador.cliente_id)
    premio = Premio.query.get(premio_id)

    # Verifica si ya existe un ganador para este premio
    ganador_existente = Ganador.query.filter_by(premio_id=premio_id).first()
    if ganador_existente:
        return jsonify({"error": "Ya se sorteó este premio"}), 409

    nuevo_ganador = Ganador(
        premio_id=premio_id,
        cliente_id=cliente.id,
        fecha_ganado=date.today()
    )
    db.session.add(nuevo_ganador)
    db.session.commit()

    return jsonify({
        "msg": "Ganador registrado exitosamente",
        "premio": premio.nombre,
        "ticket_ganador": ticket_ganador.codigo_ticket,
        "cliente": {
            "dni": cliente.dni,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "codigo_participante": cliente.codigo_participante
        }
    }), 200
