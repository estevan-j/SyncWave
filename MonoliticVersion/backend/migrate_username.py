"""
Migración para agregar campo username a la tabla users
"""
from app.models.database import db
from flask import Flask

def migrate_add_username():
    """Add username column to users table"""
    try:
        # Ejecutar SQL directo para agregar la columna
        db.engine.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS username VARCHAR(50) DEFAULT NULL
        """)
        print("✅ Migración completada: Campo 'username' agregado a la tabla 'users'")
        return True
    except Exception as e:
        print(f"❌ Error en migración: {str(e)}")
        return False

if __name__ == '__main__':
    # Crear app y contexto
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///musicapp.db'  # Cambia según tu DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        migrate_add_username()
