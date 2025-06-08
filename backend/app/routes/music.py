from flask import Blueprint, request, jsonify
from app.models.database import db, Song
from app.services.music_service import MusicService
from app.utils.responses import ApiResponse
from app.utils.validators import Validators

music_bp = Blueprint('music', __name__)

@music_bp.route('/songs', methods=['GET'])
def get_songs():
    """Get all songs"""
    songs = Song.query.all()
    return ApiResponse.success([song.to_dict() for song in songs])

@music_bp.route('/songs', methods=['POST'])
def create_song():
    """Create a new song"""
    data = request.get_json()
    
    # Validaciones básicas
    if not data or 'title' not in data or 'artist' not in data:
        return ApiResponse.error('Title and artist are required', 400)
    
    try:
        song = Song(
            title=data['title'],
            artist=data['artist'],
            album=data.get('album'),
            duration=data.get('duration'),
            file_path=data.get('file_path'),
            cover_url=data.get('cover_url'),
            artist_name=data.get('artist_name'),
            artist_nickname=data.get('artist_nickname'),
            nationality=data.get('nationality')
        )
        
        db.session.add(song)
        db.session.commit()
        
        return ApiResponse.success(song.to_dict(), 'Song created successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error creating song: {str(e)}", 500)

@music_bp.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """Get a specific song by ID"""
    song = Song.query.get_or_404(song_id)
    return ApiResponse.success(song.to_dict())

@music_bp.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """Update a song"""
    song = Song.query.get_or_404(song_id)
    data = request.get_json()
    
    try:
        # Actualizar campos básicos
        if 'title' in data:
            song.title = data['title']
        if 'artist' in data:
            song.artist = data['artist']
        if 'album' in data:
            song.album = data['album']
        if 'duration' in data:
            song.duration = data['duration']
        if 'file_path' in data:
            song.file_path = data['file_path']
        
        # Actualizar campos nuevos
        if 'cover_url' in data:
            song.cover_url = data['cover_url']
        if 'artist_name' in data:
            song.artist_name = data['artist_name']
        if 'artist_nickname' in data:
            song.artist_nickname = data['artist_nickname']
        if 'nationality' in data:
            song.nationality = data['nationality']
        
        db.session.commit()
        return ApiResponse.success(song.to_dict(), 'Song updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating song: {str(e)}", 500)

@music_bp.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Delete a song"""
    song = Song.query.get_or_404(song_id)
    
    try:
        db.session.delete(song)
        db.session.commit()
        return ApiResponse.success({}, 'Song deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error deleting song: {str(e)}", 500)

@music_bp.route('/songs/search', methods=['GET'])
def search_songs():
    """Search songs by title, artist, or album"""
    query = request.args.get('q', '').lower()
    
    if len(query) < 2:
        return ApiResponse.error('Search query must be at least 2 characters', 400)
    
    songs = Song.query.filter(
        db.or_(
            Song.title.contains(query),
            Song.artist.contains(query),
            Song.album.contains(query),
            Song.artist_name.contains(query),
            Song.artist_nickname.contains(query)
        )
    ).all()
    
    return ApiResponse.success([song.to_dict() for song in songs])

@music_bp.route('/songs/by-artist/<artist_name>', methods=['GET'])
def get_songs_by_artist(artist_name):
    """Get all songs by a specific artist"""
    songs = Song.query.filter(
        db.or_(
            Song.artist.contains(artist_name),
            Song.artist_name.contains(artist_name)
        )
    ).all()
    
    return ApiResponse.success([song.to_dict() for song in songs])

@music_bp.route('/songs/by-nationality/<nationality>', methods=['GET'])
def get_songs_by_nationality(nationality):
    """Get all songs by artist nationality"""
    songs = Song.query.filter_by(nationality=nationality).all()
    
    return ApiResponse.success([song.to_dict() for song in songs])

@music_bp.route('/upload', methods=['POST'])
def upload_song():
    """Upload a song file (placeholder for file upload functionality)"""
    # Esta función se puede implementar más tarde con manejo de archivos
    return ApiResponse.error('File upload not implemented yet', 501)
