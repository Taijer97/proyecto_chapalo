from app import db
from datetime import datetime

class SolicitudTicket(db.Model):
    __tablename__ = "solicitudes_ticket"

    solicitud_id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.String, nullable=False)
    premio_id = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente, autorizado, rechazado
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)