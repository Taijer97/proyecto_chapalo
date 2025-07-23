from app import db

class Administrador(db.Model):
    __tablename__ = 'administradores'

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(15), unique=True, nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    clave_hash = db.Column(db.String(255), nullable=False)
    celular = db.Column(db.String(15))
    rol = db.Column(db.Enum('admin', 'superadmin'), default='admin')
    creado_en = db.Column(db.DateTime, server_default=db.func.now())

    premios = db.relationship('Premio', backref='creador', lazy=True)
