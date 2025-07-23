from flask import Blueprint, jsonify, request
from app import db
from models.ganador import Ganador
from models.cliente import Cliente
from models.premio import Premio
from models.ticket import Ticket
from datetime import datetime
from utils.autenticacion import rol_requerido

ganadores_bp = Blueprint("ganadores", __name__)

@ganadores_bp.route("/ganadores", methods=["GET"])
@rol_requerido(["cliente"])
def listar_ganadores():
    print("✅ Ruta /ganadores accedida correctamente")
    fecha_str = request.args.get("fecha_sorteo")
    query = Ganador.query

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            query = query.filter(Ganador.fecha_ganado == fecha)  # corregido
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido (YYYY-MM-DD)"}), 400

    ganadores = query.order_by(Ganador.fecha_ganado.desc()).all()
    resultado = []
    for g in ganadores:
        cliente = Cliente.query.get(g.cliente_id)
        premio = Premio.query.get(g.premio_id)
        ticket = Ticket.query.get(g.ticket_id) if g.ticket_id else None

        resultado.append({
            "fecha": g.fecha_ganado.isoformat(),
            "premio": premio.nombre,
            "imagen_url": premio.imagen_url,
            "codigo_ticket": ticket.codigo_ticket if ticket else None,
            "cliente": {
                "nombres": cliente.nombres,
                "apellidos": cliente.apellidos,
                "codigo_participante": cliente.codigo_participante
            }
        })

    return jsonify(resultado), 200