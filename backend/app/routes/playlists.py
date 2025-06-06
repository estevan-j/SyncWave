from flask import Blueprint, request, jsonify
from app.models.playlist import Playlist
from app.services.playlist_service import PlaylistService
from app.utils.responses import ApiResponse

playlists_bp = Blueprint('playlists', __name__)

# Simulamos base de datos en memoria
playlists_db = []
playlist_id_counter = 1

@playlists_bp.route('/', methods=['GET'])
def get_playlists():
    """Get all playlists"""
    return ApiResponse.success([playlist.to_dict() for playlist in playlists_db])

@playlists_bp.route('/', methods=['POST'])
def create_playlist():
    """Create a new playlist"""
    global playlist_id_counter
    data = request.get_json()
    
    # Validaciones usando el servicio
    errors = PlaylistService.validate_playlist_data(data)
    if errors:
        return ApiResponse.error('; '.join(errors), 400)
    
    playlist = Playlist(
        id=playlist_id_counter,
        name=data['name'],
        description=data.get('description'),
        user_id=data.get('user_id')
    )
    
    playlists_db.append(playlist)
    playlist_id_counter += 1
    
    return ApiResponse.success(playlist.to_dict(), 'Playlist created successfully')

@playlists_bp.route('/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get a specific playlist by ID"""
    playlist = next((p for p in playlists_db if p.id == playlist_id), None)
    if not playlist:
        return ApiResponse.error('Playlist not found', 404)
    
    return ApiResponse.success(playlist.to_dict())

@playlists_bp.route('/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    """Update a playlist"""
    playlist = next((p for p in playlists_db if p.id == playlist_id), None)
    if not playlist:
        return ApiResponse.error('Playlist not found', 404)
    
    data = request.get_json()
    
    if 'name' in data:
        if not data['name'].strip():
            return ApiResponse.error('Playlist name cannot be empty', 400)
        playlist.name = data['name']
        
    if 'description' in data:
        playlist.description = data['description']
    
    return ApiResponse.success(playlist.to_dict(), 'Playlist updated successfully')

@playlists_bp.route('/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    """Delete a playlist"""
    global playlists_db
    playlist = next((p for p in playlists_db if p.id == playlist_id), None)
    if not playlist:
        return ApiResponse.error('Playlist not found', 404)
    
    playlists_db = [p for p in playlists_db if p.id != playlist_id]
    return ApiResponse.success(None, 'Playlist deleted successfully')

@playlists_bp.route('/<int:playlist_id>/songs', methods=['POST'])
def add_song_to_playlist(playlist_id):
    """Add a song to a playlist"""
    playlist = next((p for p in playlists_db if p.id == playlist_id), None)
    if not playlist:
        return ApiResponse.error('Playlist not found', 404)
    
    data = request.get_json()
    song_id = data.get('song_id')
    
    if not song_id:
        return ApiResponse.error('Song ID is required', 400)
    
    # Verificar que la canción existe (importamos songs_db desde music.py)
    from app.routes.music import songs_db
    song = next((s for s in songs_db if s.id == song_id), None)
    if not song:
        return ApiResponse.error('Song not found', 404)
    
    if song_id in playlist.songs:
        return ApiResponse.error('Song already in playlist', 400)
    
    playlist.add_song(song_id)
    return ApiResponse.success(playlist.to_dict(), 'Song added to playlist')

@playlists_bp.route('/<int:playlist_id>/songs/<int:song_id>', methods=['DELETE'])
def remove_song_from_playlist(playlist_id, song_id):
    """Remove a song from a playlist"""
    playlist = next((p for p in playlists_db if p.id == playlist_id), None)
    if not playlist:
        return ApiResponse.error('Playlist not found', 404)
    
    if song_id not in playlist.songs:
        return ApiResponse.error('Song not in playlist', 404)
    
    playlist.remove_song(song_id)
    return ApiResponse.success(playlist.to_dict(), 'Song removed from playlist')

@playlists_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_playlists(user_id):
    """Get all playlists for a specific user"""
    user_playlists = [p for p in playlists_db if p.user_id == user_id]
    return ApiResponse.success([playlist.to_dict() for playlist in user_playlists])
