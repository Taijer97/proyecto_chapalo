from app import db

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    premio_id = db.Column(db.Integer, db.ForeignKey('premios.id'), nullable=False)
    codigo_ticket = db.Column(db.String(20), unique=True, nullable=False)
    generado_en = db.Column(db.DateTime, server_default=db.func.now())
