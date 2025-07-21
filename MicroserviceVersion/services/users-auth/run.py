"""
Users Auth Service Entry Point
"""
from app import create_app, db
import os

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")

@app.cli.command()
def reset_db():
    """Reset the database"""
    db.drop_all()
    db.create_all()
    print("Database reset successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
