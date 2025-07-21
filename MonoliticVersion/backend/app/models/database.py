from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # ✨ NUEVO CAMPO PASSWORD
    username = db.Column(db.String(50), nullable=True, default=None)  # ✨ NUEVO CAMPO USERNAME
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    favorite_songs = db.relationship('FavoriteSong', backref='user', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('ChatMessage', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Song(db.Model):
    __tablename__ = 'songs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)          # "name" del JSON
    artist = db.Column(db.String(100), nullable=False)         # "artist.name" simplificado
    album = db.Column(db.String(100))                          # "album" del JSON
    duration = db.Column(db.Integer)                           # "duration.end" del JSON (en segundos)
    file_path = db.Column(db.String(500))                      # "url" del JSON
    cover_url = db.Column(db.String(500))                      # "cover" del JSON ✨
    artist_name = db.Column(db.String(100))                    # "artist.name" completo ✨
    artist_nickname = db.Column(db.String(100))                # "artist.nickname" del JSON ✨
    nationality = db.Column(db.String(10))                     # "artist.nationality" del JSON ✨
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    favorited_by = db.relationship('FavoriteSong', backref='song', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'file_path': self.file_path,
            'cover_url': self.cover_url,
            'artist_name': self.artist_name,
            'artist_nickname': self.artist_nickname,
            'nationality': self.nationality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class FavoriteSong(db.Model):
    __tablename__ = 'favorite_songs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint para evitar duplicados
    __table_args__ = (db.UniqueConstraint('user_id', 'song_id', name='unique_user_song'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'song_id': self.song_id,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'song': self.song.to_dict() if self.song else None
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.Column(db.String(50), default='general')  # Chat room/channel
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.author.email if self.author else 'Unknown',
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'room': self.room
        }
