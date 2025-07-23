from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from utils.autenticacion import rol_requerido
from app import db
from models.premio import Premio
from models.ticket import Ticket
from models.cliente import Cliente
from models.ganador import Ganador  # Añadir esta línea
import uuid
from datetime import datetime, date  # Añadir date aquí también
from models.administrador import Administrador
from werkzeug.utils import secure_filename
import os

premio_admin_bp = Blueprint("premio_admin", __name__)

# ============================
# 1. Crear nuevo premio
# ============================
@premio_admin_bp.route("/premios", methods=["POST"])
@rol_requerido(["admin", "superadmin"])
def registrar_premio():
    if "nombre" not in request.form or "fecha_sorteo" not in request.form or "imagen" not in request.files:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    fecha_sorteo = request.form.get("fecha_sorteo")
    imagen = request.files["imagen"]

    if not nombre or not fecha_sorteo or imagen.filename == "":
        return jsonify({"error": "Datos inválidos"}), 400

    try:
        fecha_sorteo_dt = datetime.strptime(fecha_sorteo, "%Y-%m-%d").date()
    except:
        return jsonify({"error": "Formato de fecha inválido (YYYY-MM-DD)"}), 400

    # Guardar la imagen en la carpeta correcta
    filename = secure_filename(imagen.filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
    ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    imagen.save(ruta)

    # URL correcta para el frontend
    imagen_url = f"/uploads/{unique_name}"

    # Crear premio
    codigo_premio = "PRM-" + uuid.uuid4().hex[:6].upper()

    nuevo_premio = Premio(
        codigo_premio=codigo_premio,
        nombre=nombre,
        descripcion=descripcion,
        imagen_url=imagen_url,
        fecha_sorteo=fecha_sorteo_dt,
        creado_por=get_jwt_identity()
    )

    try:
        db.session.add(nuevo_premio)
        db.session.commit()
        return jsonify({
            "msg": "Premio registrado correctamente",
            "codigo_premio": codigo_premio
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ============================
# 2. Ver participantes por premio
# ============================
@premio_admin_bp.route("/premios/<int:premio_id>/participantes", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def listar_participantes(premio_id):
    tickets = Ticket.query.filter_by(premio_id=premio_id).all()
    resultado = []
    for t in tickets:
        cliente = Cliente.query.get(t.cliente_id)
        resultado.append({
            "codigo_ticket": t.codigo_ticket,
            "cliente_id": cliente.id,
            "nombres": cliente.nombres,
            "apellidos": cliente.apellidos,
            "dni": cliente.dni
        })
    return jsonify(resultado), 200

@premio_admin_bp.route("/premios", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def listar_premios():
    premios = Premio.query.filter_by(vencido=1).all()
    resultado = []

    for p in premios:
        admin = Administrador.query.get(p.creado_por)
        resultado.append({
            "id": p.id,
            "codigo_premio": p.codigo_premio,
            "nombre": p.nombre,
            "descripcion": p.descripcion,
            "imagen_url": p.imagen_url,
            "fecha_sorteo": p.fecha_sorteo.isoformat(),
            "creado_por": {
                "id": admin.id,
                "nombres": admin.nombres,
                "apellidos": admin.apellidos
            } if admin else None
        })

    return jsonify(resultado), 200

@premio_admin_bp.route("/asignar_ganador", methods=["POST"])
@rol_requerido(["admin", "superadmin"])
def asignar_ganador():
    data = request.get_json()
    print("Datos recibidos:", data)
    cliente_id = data.get("cliente_id")
    premio_id = data.get("premio_id")
    ticket_id = data.get("ticket_id")  # Mantener para referencia

    if not cliente_id or not premio_id:
        return jsonify({"error": "Faltan datos"}), 400

    try:
        # Verificar si ya existe un ganador para este premio
        ganador_existente = Ganador.query.filter_by(premio_id=premio_id).first()
        if ganador_existente:
            return jsonify({"error": "Este premio ya tiene un ganador asignado"}), 400
            
        nuevo_ganador = Ganador(
            cliente_id=cliente_id,
            premio_id=premio_id,
            ticket_id=ticket_id,
            fecha_ganado=date.today()
        )
        db.session.add(nuevo_ganador)
        db.session.commit()
        return jsonify({"msg": "Ganador asignado correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error al asignar ganador: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500