from app import db

class Ganador(db.Model):
    __tablename__ = 'ganadores'

    id = db.Column(db.Integer, primary_key=True)
    premio_id = db.Column(db.Integer, db.ForeignKey('premios.id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    fecha_ganado = db.Column(db.Date, nullable=False)
