from flask import Flask, send_from_directory
from config import Config
from flask_cors import CORS
from utils.extensions import db, jwt
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    # Configuración unificada para uploads
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
    # Configuración CORS muy permisiva para desarrollo
    CORS(app, 
         origins="*",
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         allow_headers=["*"],
         expose_headers=["*"]
    )
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)

    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    with app.app_context():
        from models import cliente, administrador, premio, ticket, ganador
        db.create_all()

    # Ruta para servir archivos estáticos
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


    # Registrar rutas
    from routes.auth_cliente import auth_cliente_bp
    from routes.auth_admin import auth_admin_bp
    from routes.premio_admin import premio_admin_bp
    from routes.clientes_admin import clientes_admin_bp
    from routes.ticket_cliente import ticket_cliente_bp
    from routes.ganadores_publico import ganadores_bp
    from routes.perfil_cliente import perfil_cliente_bp
    from routes.suscripcion_cliente import suscripcion_bp
    from routes.premios_cliente import premios_cliente_bp
    from routes.exportar_excel import exportar_bp
    from routes.solicitud_ticket import solicitud_ticket_bp
    from routes.suscripciones_admin import suscripciones_admin_bp
    from routes.solicitudes_admin import solicitudes_admin_bp
    from routes.admin_clientes import admin_clientes_bp
    #from routes.admin_premios import admin_premios_bp
    from routes.admin_tickets import tickets_admin_bp

    app.register_blueprint(auth_cliente_bp, url_prefix="/cliente")
    app.register_blueprint(auth_admin_bp, url_prefix="/admin")
    app.register_blueprint(premio_admin_bp, url_prefix="/admin")
    app.register_blueprint(clientes_admin_bp, url_prefix="/admin")
    app.register_blueprint(ticket_cliente_bp, url_prefix="/cliente")
    app.register_blueprint(ganadores_bp, url_prefix="/cliente")
    app.register_blueprint(perfil_cliente_bp, url_prefix="/cliente")
    app.register_blueprint(suscripcion_bp, url_prefix="/cliente")
    app.register_blueprint(premios_cliente_bp, url_prefix="/cliente")
    app.register_blueprint(exportar_bp, url_prefix="/admin")
    app.register_blueprint(solicitud_ticket_bp, url_prefix="/cliente")
    app.register_blueprint(suscripciones_admin_bp, url_prefix="/admin")
    app.register_blueprint(solicitudes_admin_bp, url_prefix="/admin")
    app.register_blueprint(admin_clientes_bp)
    #app.register_blueprint(admin_premios_bp, url_prefix="/admin")
    app.register_blueprint(tickets_admin_bp, url_prefix="/admin")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)