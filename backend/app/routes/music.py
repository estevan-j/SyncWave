from flask import Blueprint, request, jsonify
from app.models.song import Song
from app.services.music_service import MusicService
from app.utils.responses import ApiResponse

music_bp = Blueprint('music', __name__)

# Simulamos base de datos en memoria
songs_db = []
song_id_counter = 1

@music_bp.route('/songs', methods=['GET'])
def get_songs():
    """Get all songs"""
    return ApiResponse.success([song.to_dict() for song in songs_db])

@music_bp.route('/songs', methods=['POST'])
def create_song():
    """Create a new song"""
    global song_id_counter
    data = request.get_json()
    
    # Validaciones usando el servicio
    errors = MusicService.validate_song_data(data)
    if errors:
        return ApiResponse.error('; '.join(errors), 400)
    
    song = Song(
        id=song_id_counter,
        title=data['title'],
        artist=data['artist'],
        album=data.get('album'),
        duration=data.get('duration'),
        file_path=data.get('file_path')
    )
    
    songs_db.append(song)
    song_id_counter += 1
    
    return ApiResponse.success(song.to_dict(), 'Song created successfully')

@music_bp.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """Get a specific song by ID"""
    song = next((s for s in songs_db if s.id == song_id), None)
    if not song:
        return ApiResponse.error('Song not found', 404)
    
    return ApiResponse.success(song.to_dict())

@music_bp.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """Update a song"""
    song = next((s for s in songs_db if s.id == song_id), None)
    if not song:
        return ApiResponse.error('Song not found', 404)
    
    data = request.get_json()
    
    if 'title' in data and data['title'].strip():
        song.title = data['title']
    if 'artist' in data and data['artist'].strip():
        song.artist = data['artist']
    if 'album' in data:
        song.album = data['album']
    if 'duration' in data:
        song.duration = data['duration']
    if 'file_path' in data:
        song.file_path = data['file_path']
    
    return ApiResponse.success(song.to_dict(), 'Song updated successfully')

@music_bp.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Delete a song"""
    global songs_db
    song = next((s for s in songs_db if s.id == song_id), None)
    if not song:
        return ApiResponse.error('Song not found', 404)
    
    songs_db = [s for s in songs_db if s.id != song_id]
    return ApiResponse.success(None, 'Song deleted successfully')

@music_bp.route('/songs/search', methods=['GET'])
def search_songs():
    """Search songs by title or artist"""
    query = request.args.get('q', '').lower()
    if not query:
        return ApiResponse.error('Search query is required', 400)
    
    filtered_songs = [
        song for song in songs_db
        if query in song.title.lower() or query in song.artist.lower()
    ]
    
    return ApiResponse.success([song.to_dict() for song in filtered_songs])
