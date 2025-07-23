from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.cliente import Cliente
from models.premio import Premio
from models.ticket import Ticket
from datetime import date, timedelta
import uuid
import os

suscripcion_bp = Blueprint("suscripcion", __name__)

# ============================
# Seleccionar suscripción
# ============================
@suscripcion_bp.route("/suscripcion", methods=["PUT"])
@rol_requerido(["cliente"])
def seleccionar_suscripcion():
    cliente_id = get_jwt_identity()

    # Verifica campos
    if "suscripcion" not in request.form or "comprobante" not in request.files:
        return jsonify({"error": "Debe enviar la suscripción y el comprobante"}), 400

    tipo = request.form.get("suscripcion")
    comprobante = request.files["comprobante"]

    if tipo not in ["mensual", "trimestral", "anual"]:
        return jsonify({"error": "Tipo de suscripción inválido"}), 400

    cliente = Cliente.query.get(cliente_id)
    if cliente.suscripcion:
        return jsonify({"error": "Ya seleccionó una suscripción"}), 409

    # Calcular vencimiento y beneficios
    hoy = date.today()
    if tipo == "mensual":
        vencimiento = hoy + timedelta(days=30)
        tickets = 4
        vip = 0
    elif tipo == "trimestral":
        vencimiento = hoy + timedelta(days=90)
        tickets = 16
        vip = 0
    elif tipo == "anual":
        vencimiento = hoy + timedelta(days=365)
        tickets = 48
        vip = 1

    # Guardar comprobante
    extension = comprobante.filename.rsplit(".", 1)[-1].lower()
    nombre_archivo = f"comprobante_{cliente_id}_{tipo}.{extension}"
    ruta_guardado = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_archivo)
    comprobante.save(ruta_guardado)

    # Actualizar cliente
    cliente.suscripcion = tipo
    cliente.fecha_suscripcion = hoy
    cliente.fecha_vencimiento = vencimiento
    cliente.tickets_por_suscripcion = tickets
    cliente.vip = vip
    cliente.autorizado = 0
    cliente.comprobante_url = ruta_guardado

    db.session.commit()

    return jsonify({"msg": f"Suscripción {tipo} registrada. Esperando autorización."}), 200

@suscripcion_bp.route("/suscripcion", methods=["GET"])
@rol_requerido(["cliente"])
def obtener_suscripcion():
    cliente_id = get_jwt_identity()
    cliente = Cliente.query.get(cliente_id)
    
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    
    # Contar tickets disponibles
    tickets_disponibles = Ticket.query.filter_by(cliente_id=cliente_id).count()
    
    return jsonify({
        "suscripcion": cliente.suscripcion,
        "fecha_suscripcion": cliente.fecha_suscripcion.isoformat() if cliente.fecha_suscripcion else None,
        "tickets_disponibles": tickets_disponibles,
        "puede_seleccionar": cliente.suscripcion is None,
        "autorizado": cliente.autorizado
    }), 200

@suscripcion_bp.route("/verificar-suscripcion", methods=["GET"])
@rol_requerido(["cliente"])
def verificar_suscripcion():
    cliente_id = get_jwt_identity()
    cliente = Cliente.query.get(cliente_id)

    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404

    # ✅ Simplificar la verificación usando solo campos existentes
    if cliente.autorizado and cliente.suscripcion:
        return jsonify({"autorizado": True}), 200
    else:
        return jsonify({"autorizado": False}), 200



