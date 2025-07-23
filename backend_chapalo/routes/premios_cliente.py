from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.premio import Premio
from models.ticket import Ticket
from models.cliente import Cliente
import uuid
from flask_jwt_extended import jwt_required, get_jwt
from datetime import date

premios_cliente_bp = Blueprint("premios_cliente", __name__)

@premios_cliente_bp.route("/premios", methods=["GET"])
@rol_requerido(["cliente"])
def listar_premios():
    try:
        cliente_id = get_jwt_identity()
        hoy = date.today()

        # 🔧 Filtrar premios con fecha futura o igual a hoy
        premios = Premio.query.filter(Premio.fecha_sorteo >= hoy).order_by(Premio.fecha_sorteo.asc()).all()
        resultado = []

        for p in premios:
            cantidad_chances = Ticket.query.filter_by(cliente_id=cliente_id, premio_id=p.id).count()
            resultado.append({
                "premio_id": p.id,
                "codigo_premio": p.codigo_premio,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "imagen_url": p.imagen_url,
                "fecha_sorteo": p.fecha_sorteo.isoformat(),
                "mis_chances": cantidad_chances
            })

        return jsonify(resultado), 200

    except Exception as e:
        print(f"❌ Error al obtener premios: {e}")
        return jsonify({"error": f"Error al obtener premios: {str(e)}"}), 500

@premios_cliente_bp.route("/premios/<int:premio_id>/aumentar", methods=["POST"])
@rol_requerido(["cliente"])
def aumentar_chances(premio_id):
    cliente_id = get_jwt_identity()
    data = request.get_json()
    cantidad = data.get("cantidad", 1)

    if cantidad <= 0 or cantidad > 10:
        return jsonify({"error": "Cantidad inválida (1-10)"}), 400

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

    try:
        db.session.commit()
        return jsonify({
            "msg": f"{cantidad} chances generadas para {premio.nombre}",
            "tickets": tickets_generados
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al guardar tickets: {e}")
        return jsonify({"error": "Error al generar tickets"}), 500