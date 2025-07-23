from utils.extensions import db


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    clave_hash = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(15))
    suscripcion = db.Column(db.Enum('mensual', 'trimestral', 'anual'), default=None)
    fecha_suscripcion = db.Column(db.Date)
    fecha_vencimiento = db.Column(db.Date)  # ✅ Campo agregado
    comprobante_url = db.Column(db.String(255))
    tickets_por_suscripcion = db.Column(db.Integer, default=0)  # ✅ Campo agregado
    vip = db.Column(db.Boolean, default=False)  # ✅ Campo agregado
    autorizado = db.Column(db.Boolean, default=False)
    codigo_participante = db.Column(db.String(15), unique=True)
    codigo_referencia = db.Column(db.String(10), unique=True)
    referido_por_codigo = db.Column(db.String(10), db.ForeignKey('clientes.codigo_referencia'))
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    tickets = db.relationship('Ticket', backref='cliente', lazy=True)
