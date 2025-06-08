#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de ejemplo
"""

from app import create_app
from app.models.database import db, User, Song, FavoriteSong, ChatMessage
from datetime import datetime
from werkzeug.security import generate_password_hash

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
            User(email='admin@musicapp.com', password=generate_password_hash('admin123')),
            User(email='musiclover@example.com', password=generate_password_hash('music123')),
            User(email='djmaster@example.com', password=generate_password_hash('dj123')),
            User(email='listener1@example.com', password=generate_password_hash('listen123'))
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users)} users")
        
        # Crear canciones de ejemplo con nuevos campos
        songs = [
            Song(
                title='Bohemian Rhapsody', 
                artist='Queen', 
                album='A Night at the Opera', 
                duration=355,
                cover_url='https://example.com/covers/bohemian_rhapsody.jpg',
                artist_name='Queen',
                artist_nickname='The Champions',
                nationality='UK'
            ),
            Song(
                title='Stairway to Heaven', 
                artist='Led Zeppelin', 
                album='Led Zeppelin IV', 
                duration=482,
                cover_url='https://example.com/covers/stairway_to_heaven.jpg',
                artist_name='Led Zeppelin',
                artist_nickname='Zeppelin',
                nationality='UK'
            ),
            Song(
                title='Hotel California', 
                artist='Eagles', 
                album='Hotel California', 
                duration=391,
                cover_url='https://example.com/covers/hotel_california.jpg',
                artist_name='Eagles',
                artist_nickname='The Eagles',
                nationality='US'
            ),
            Song(
                title='Imagine', 
                artist='John Lennon', 
                album='Imagine', 
                duration=183,
                cover_url='https://example.com/covers/imagine.jpg',
                artist_name='John Lennon',
                artist_nickname='Johnny',
                nationality='UK'
            ),
            Song(
                title='Billie Jean', 
                artist='Michael Jackson', 
                album='Thriller', 
                duration=294,
                cover_url='https://example.com/covers/billie_jean.jpg',
                artist_name='Michael Jackson',
                artist_nickname='MJ',
                nationality='US'
            ),
            Song(
                title='Like a Rolling Stone', 
                artist='Bob Dylan', 
                album='Highway 61 Revisited', 
                duration=369,
                cover_url='https://example.com/covers/like_a_rolling_stone.jpg',
                artist_name='Bob Dylan',
                artist_nickname='Dylan',
                nationality='US'
            ),
            Song(
                title='Smells Like Teen Spirit', 
                artist='Nirvana', 
                album='Nevermind', 
                duration=301,
                cover_url='https://example.com/covers/smells_like_teen_spirit.jpg',
                artist_name='Nirvana',
                artist_nickname='Nirvana',
                nationality='US'
            ),
            Song(
                title='What\'s Going On', 
                artist='Marvin Gaye', 
                album='What\'s Going On', 
                duration=232,
                cover_url='https://example.com/covers/whats_going_on.jpg',
                artist_name='Marvin Gaye',
                artist_nickname='Marvin',
                nationality='US'
            )
        ]
        
        for song in songs:
            db.session.add(song)
        
        db.session.commit()
        print(f"Created {len(songs)} songs")
        
        # Crear canciones favoritas de ejemplo
        admin_user = User.query.filter_by(email='admin@musicapp.com').first()
        musiclover_user = User.query.filter_by(email='musiclover@example.com').first()
        
        # Agregar algunas canciones como favoritas
        bohemian = Song.query.filter_by(title='Bohemian Rhapsody').first()
        stairway = Song.query.filter_by(title='Stairway to Heaven').first()
        hotel = Song.query.filter_by(title='Hotel California').first()
        imagine = Song.query.filter_by(title='Imagine').first()
        billie = Song.query.filter_by(title='Billie Jean').first()
        
        favorites = []
        if admin_user and bohemian:
            favorites.append(FavoriteSong(user_id=admin_user.id, song_id=bohemian.id))
        if admin_user and stairway:
            favorites.append(FavoriteSong(user_id=admin_user.id, song_id=stairway.id))
        if admin_user and hotel:
            favorites.append(FavoriteSong(user_id=admin_user.id, song_id=hotel.id))
        
        if musiclover_user and billie:
            favorites.append(FavoriteSong(user_id=musiclover_user.id, song_id=billie.id))
        if musiclover_user and imagine:
            favorites.append(FavoriteSong(user_id=musiclover_user.id, song_id=imagine.id))
        
        for favorite in favorites:
            db.session.add(favorite)
        
        db.session.commit()
        print(f"Created {len(favorites)} favorite songs")
        
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
        print(f"- Favorite Songs: {FavoriteSong.query.count()}")
        print(f"- Chat Messages: {ChatMessage.query.count()}")
        
        print("\nSample users created:")
        for user in User.query.all():
            print(f"- {user.email} (ID: {user.id})")
        
        print("\nYou can now:")
        print("1. Start the server: python app.py")
        print("2. Access the API at: http://localhost:5000")
        print("3. Test the endpoints:")
        print("   - GET /api/users")
        print("   - GET /api/music/songs")
        print("   - GET /api/favorites/user/1")
        print("   - POST /api/users/login (with email and password)")
        print("4. Test the chat with WebSocket clients")

if __name__ == '__main__':
    init_sample_data()
