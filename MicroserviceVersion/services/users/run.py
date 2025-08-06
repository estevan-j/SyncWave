import os
from app import create_app
from flask_socketio import SocketIO

app = create_app(os.environ.get('FLASK_ENV', 'development'))
socketio = SocketIO(app, cors_allowed_origins="*")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)