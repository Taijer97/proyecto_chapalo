from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.autenticacion import rol_requerido
from models.ticket import Ticket
from models.cliente import Cliente
from app import db

tickets_admin_bp = Blueprint("tickets_admin", __name__)

@tickets_admin_bp.route("/tickets_por_premio/<int:premio_id>", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def obtener_tickets_por_premio(premio_id):
    try:
        tickets = Ticket.query.filter_by(premio_id=premio_id).all()
        resultado = []

        for t in tickets:
            cliente = Cliente.query.get(t.cliente_id)
            resultado.append({
                "ticket_id": t.id,
                "codigo_ticket": t.codigo_ticket,
                "cliente_id": cliente.id,
                "cliente_nombres": cliente.nombres,
                "cliente_apellidos": cliente.apellidos,
                "codigo_participante": cliente.codigo_participante
            })

        return jsonify(resultado), 200
    except Exception as e:
        print(f"❌ Error al obtener tickets: {e}")
        return jsonify({"error": "Error al obtener tickets"}), 500