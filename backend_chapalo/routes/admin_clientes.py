from flask import Blueprint, jsonify
from models.cliente import Cliente
from utils.autenticacion import rol_requerido

admin_clientes_bp = Blueprint("admin_clientes", __name__)

@admin_clientes_bp.route("/admin/clientes", methods=["GET"])
@rol_requerido(["admin", "superadmin"])
def listar_clientes():
    clientes = Cliente.query.all()
    resultado = []

    for c in clientes:
        resultado.append({
            "id": c.id,
            "nombres": c.nombres,
            "apellidos": c.apellidos,
            "codigo_participante": c.codigo_participante
        })

    return jsonify(resultado), 200
