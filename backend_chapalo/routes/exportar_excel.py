from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.premio import Premio
from models.ticket import Ticket
from models.cliente import Cliente
import pandas as pd
import os

exportar_bp = Blueprint("exportar_excel", __name__)

@exportar_bp.route("/exportar-participantes/<int:premio_id>", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def exportar_participantes(premio_id):
    premio = Premio.query.get(premio_id)
    if not premio:
        return jsonify({"error": "Premio no encontrado"}), 404

    tickets = Ticket.query.filter_by(premio_id=premio_id).all()
    if not tickets:
        return jsonify({"error": "No hay participantes en este premio"}), 404

    datos = []
    for t in tickets:
        cliente = Cliente.query.get(t.cliente_id)
        datos.append({
            "Código Ticket": t.codigo_ticket,
            "DNI": cliente.dni,
            "Nombres": cliente.nombres,
            "Apellidos": cliente.apellidos,
            "Código Participante": cliente.codigo_participante,
            "Fecha Participación": t.generado_en.strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(datos)
    nombre_archivo = f"participantes_premio_{premio.codigo_premio}.xlsx"
    ruta = f"/tmp/{nombre_archivo}"
    df.to_excel(ruta, index=False)

    return send_file(
        ruta,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
