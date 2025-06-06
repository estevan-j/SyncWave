#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""

from app import create_app
from app.models.database import db, User, Song, Playlist, ChatMessage
from datetime import datetime

def init_sample_data():
    """Initialize database with sample data"""
    app, socketio = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        
        # Verificar si ya hay datos
        if User.query.first():
            print("Database already has data. Skipping initialization.")
            return
        
        print("Initializing database with sample data...")
        
        # Crear usuarios de ejemplo
        users = [
            User(username='admin', email='admin@musicapp.com'),
            User(username='musiclover', email='music@example.com'),
            User(username='dj_master', email='dj@example.com'),
            User(username='listener1', email='listener1@example.com')
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Crear canciones de ejemplo
        songs = [
            Song(title='Bohemian Rhapsody', artist='Queen', album='A Night at the Opera', duration=355),
            Song(title='Stairway to Heaven', artist='Led Zeppelin', album='Led Zeppelin IV', duration=482),
            Song(title='Hotel California', artist='Eagles', album='Hotel California', duration=391),
            Song(title='Imagine', artist='John Lennon', album='Imagine', duration=183),
            Song(title='Billie Jean', artist='Michael Jackson', album='Thriller', duration=294),
            Song(title='Like a Rolling Stone', artist='Bob Dylan', album='Highway 61 Revisited', duration=369),
            Song(title='Smells Like Teen Spirit', artist='Nirvana', album='Nevermind', duration=301),
            Song(title='What\'s Going On', artist='Marvin Gaye', album='What\'s Going On', duration=232)
        ]
        
        for song in songs:
            db.session.add(song)
        
        db.session.commit()
        print(f"Created {len(songs)} songs")
        
        # Crear playlists de ejemplo
        admin_user = User.query.filter_by(username='admin').first()
        musiclover_user = User.query.filter_by(username='musiclover').first()
        
        playlists = [
            Playlist(name='Classic Rock Hits', description='Best classic rock songs', user_id=admin_user.id),
            Playlist(name='80s Favorites', description='Greatest hits from the 80s', user_id=musiclover_user.id),
            Playlist(name='Chill Vibes', description='Relaxing songs for any mood', user_id=admin_user.id)
        ]
        
        for playlist in playlists:
            db.session.add(playlist)
        
        db.session.commit()
        print(f"Created {len(playlists)} playlists")
        
        # Agregar canciones a playlists
        classic_rock = Playlist.query.filter_by(name='Classic Rock Hits').first()
        eighties = Playlist.query.filter_by(name='80s Favorites').first()
        chill = Playlist.query.filter_by(name='Chill Vibes').first()
        
        # Classic Rock playlist
        bohemian = Song.query.filter_by(title='Bohemian Rhapsody').first()
        stairway = Song.query.filter_by(title='Stairway to Heaven').first()
        hotel = Song.query.filter_by(title='Hotel California').first()
        
        if classic_rock and bohemian and stairway and hotel:
            classic_rock.songs.extend([bohemian, stairway, hotel])
        
        # 80s playlist
        billie = Song.query.filter_by(title='Billie Jean').first()
        if eighties and billie:
            eighties.songs.append(billie)
        
        # Chill playlist
        imagine = Song.query.filter_by(title='Imagine').first()
        whats_going = Song.query.filter_by(title='What\'s Going On').first()
        
        if chill and imagine and whats_going:
            chill.songs.extend([imagine, whats_going])
        
        db.session.commit()
        print("Added songs to playlists")
        
        # Crear algunos mensajes de chat de ejemplo
        chat_messages = [
            ChatMessage(
                user_id=admin_user.id,
                message='¡Bienvenidos al chat de Music App!',
                room='general',
                timestamp=datetime.utcnow()
            ),
            ChatMessage(
                user_id=musiclover_user.id,
                message='¡Hola! ¿Alguien tiene recomendaciones de música?',
                room='general',
                timestamp=datetime.utcnow()
            )
        ]
        
        for message in chat_messages:
            db.session.add(message)
        
        db.session.commit()
        print(f"Created {len(chat_messages)} chat messages")
        
        print("\n✅ Database initialized successfully!")
        print("\nSample data created:")
        print(f"- Users: {User.query.count()}")
        print(f"- Songs: {Song.query.count()}")
        print(f"- Playlists: {Playlist.query.count()}")
        print(f"- Chat Messages: {ChatMessage.query.count()}")
        
        print("\nYou can now:")
        print("1. Start the server: python app.py")
        print("2. Access the API at: http://localhost:5000")
        print("3. Test the chat with WebSocket clients")

if __name__ == '__main__':
    init_sample_data()
