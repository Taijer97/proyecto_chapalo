from app import db
from datetime import date

class Premio(db.Model):
    __tablename__ = 'premios'

    id = db.Column(db.Integer, primary_key=True)
    codigo_premio = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.Text)
    fecha_sorteo = db.Column(db.Date, nullable=False)
    creado_por = db.Column(db.Integer, db.ForeignKey('administradores.id'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    tickets = db.relationship('Ticket', backref='premio', lazy=True)
    ganadores = db.relationship('Ganador', backref='premio', lazy=True)

    # Nuevo campo
    vencido = db.Column(db.Boolean, default=False)

    def actualizar_estado_vencido(self):
        self.vencido = self.fecha_sorteo < date.today()