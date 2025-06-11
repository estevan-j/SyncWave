from flask import Blueprint, request, jsonify, current_app
from app.models.database import db, Song
from app.services.music_service import MusicService
from app.utils.responses import ApiResponse
from sqlalchemy import or_
import os

music_bp = Blueprint('music', __name__)


@music_bp.route('/songs', methods=['GET'])
def get_songs():
    """Get all songs"""
    try:
        songs = Song.query.order_by(Song.created_at.desc()).all()
        return ApiResponse.success([song.to_dict() for song in songs])
    except Exception as e:
        return ApiResponse.error(f"Error retrieving songs: {str(e)}", 500)


@music_bp.route('/songs', methods=['POST'])
def create_song():
    """Create a new song"""
    data = request.get_json()

    if not data:
        return ApiResponse.error('No data provided', 400)

    # Validar datos usando el servicio
    errors = MusicService.validate_song_data(data)
    if errors:
        return ApiResponse.error('Validation failed', 400, {'validation_errors': errors})

    # Sanitizar datos
    clean_data = MusicService.sanitize_song_data(data)

    # Verificar duplicados
    existing_song = MusicService.check_duplicate_song(
        db, Song, clean_data.get('title', ''), clean_data.get('artist', '')
    )
    if existing_song:
        return ApiResponse.error('Song already exists with same title and artist', 409)

    try:
        song = Song(
            title=clean_data.get('title'),
            artist=clean_data.get('artist'),
            album=clean_data.get('album'),
            duration=clean_data.get('duration'),
            file_path=clean_data.get('file_path'),
            cover_url=clean_data.get('cover_url'),
            artist_name=clean_data.get('artist_name'),
            artist_nickname=clean_data.get('artist_nickname'),
            nationality=clean_data.get('nationality')
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
    try:
        song = Song.query.get_or_404(song_id)
        return ApiResponse.success(song.to_dict())
    except Exception as e:
        return ApiResponse.error(f"Song not found: {str(e)}", 404)


@music_bp.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """Update a song"""
    song = Song.query.get_or_404(song_id)
    data = request.get_json()

    if not data:
        return ApiResponse.error('No data provided', 400)

    # Validar solo los campos que se están actualizando
    errors = MusicService.validate_song_data(data)
    if errors:
        return ApiResponse.error('Validation failed', 400, {'validation_errors': errors})

    # Sanitizar datos
    clean_data = MusicService.sanitize_song_data(data)

    try:
        # Actualizar campos de forma dinámica
        updateable_fields = [
            'title', 'artist', 'album', 'duration', 'file_path',
            'cover_url', 'artist_name', 'artist_nickname', 'nationality'
        ]

        for field in updateable_fields:
            if field in clean_data:
                setattr(song, field, clean_data[field])

        db.session.commit()
        return ApiResponse.success(song.to_dict(), 'Song updated successfully')

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating song: {str(e)}", 500)


@music_bp.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Delete a song"""
    try:
        song = Song.query.get_or_404(song_id)

        # Opcional: eliminar archivo físico si existe
        # if song.file_path and os.path.exists(song.file_path):
        #     os.remove(song.file_path)

        db.session.delete(song)
        db.session.commit()

        return ApiResponse.success({'deleted_song_id': song_id}, 'Song deleted successfully')

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error deleting song: {str(e)}", 500)


@music_bp.route('/songs/search', methods=['GET'])
def search_songs():
    """Search songs by various criteria"""
    # Parámetros de búsqueda
    query = request.args.get('q', '').strip()
    title = request.args.get('title', '').strip()
    artist = request.args.get('artist', '').strip()

    # Validar que al menos un parámetro esté presente
    if not any([query, title, artist]):
        return ApiResponse.error('At least one search parameter is required (q, title, or artist)', 400)

    # Validar longitud mínima
    if query and len(query) < 2:
        return ApiResponse.error('General search query must be at least 2 characters', 400)

    if title and len(title) < 2:
        return ApiResponse.error('Title search must be at least 2 characters', 400)

    if artist and len(artist) < 2:
        return ApiResponse.error('Artist search must be at least 2 characters', 400)

    try:
        songs = MusicService.search_songs_by_criteria(
            db, Song, title=title, artist=artist, query=query
        )

        return ApiResponse.success([song.to_dict() for song in songs],
                                   f'Found {len(songs)} songs')

    except Exception as e:
        return ApiResponse.error(f"Error searching songs: {str(e)}", 500)


@music_bp.route('/songs/by-artist/<artist_name>', methods=['GET'])
def get_songs_by_artist(artist_name):
    """Get all songs by a specific artist"""
    if len(artist_name.strip()) < 2:
        return ApiResponse.error('Artist name must be at least 2 characters', 400)

    try:
        songs = Song.query.filter(
            or_(
                Song.artist.ilike(f'%{artist_name}%'),
                Song.artist_name.ilike(f'%{artist_name}%'),
                Song.artist_nickname.ilike(f'%{artist_name}%')
            )
        ).all()

        return ApiResponse.success([song.to_dict() for song in songs],
                                   f'Found {len(songs)} songs by {artist_name}')
    except Exception as e:
        return ApiResponse.error(f"Error getting songs by artist: {str(e)}", 500)


@music_bp.route('/songs/by-nationality/<nationality>', methods=['GET'])
def get_songs_by_nationality(nationality):
    """Get all songs by artist nationality"""
    try:
        songs = Song.query.filter_by(nationality=nationality.upper()).all()
        return ApiResponse.success([song.to_dict() for song in songs],
                                   f'Found {len(songs)} songs from {nationality}')
    except Exception as e:
        return ApiResponse.error(f"Error getting songs by nationality: {str(e)}", 500)

# Rutas adicionales para compatibilidad con frontend actual


@music_bp.route('/tracks', methods=['GET'])
def get_tracks():
    """Alias for songs endpoint for frontend compatibility"""
    return get_songs()


@music_bp.route('/search', methods=['GET'])
def search_tracks():
    """Alias for search endpoint for frontend compatibility"""
    return search_songs()


@music_bp.route('/songs/upload', methods=['POST'])
def upload_song():
    """Upload a new song with file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return ApiResponse.error('No file provided', 400)

        file = request.files['file']
        if file.filename == '':
            return ApiResponse.error('No file selected', 400)

        # Validate file type
        if not MusicService.allowed_file(file.filename):
            return ApiResponse.error('Invalid file type. Allowed: mp3, wav, flac, ogg, m4a, aac', 400)

        # Get form data
        title = request.form.get('title', '').strip()
        artist = request.form.get('artist', '').strip()

        if not title:
            return ApiResponse.error('Title is required', 400)
        if not artist:
            return ApiResponse.error('Artist is required', 400)

        # Optional fields
        album = request.form.get('album', '').strip() or None
        duration = request.form.get('duration')
        cover_url = request.form.get('cover_url', '').strip() or None
        artist_name = request.form.get('artist_name', '').strip() or artist
        artist_nickname = request.form.get(
            'artist_nickname', '').strip() or None
        nationality = request.form.get('nationality', '').strip() or None

        # Convert duration to int if provided
        if duration:
            try:
                duration = int(float(duration))
            except (ValueError, TypeError):
                duration = None

        # Check for duplicates
        existing_song = MusicService.check_duplicate_song(
            db, Song, title, artist)
        if existing_song:
            return ApiResponse.error('Song already exists with same title and artist', 409)

        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = MusicService.save_file(file, upload_folder)

        if not file_path:
            return ApiResponse.error('Failed to save file', 500)
          # Create relative path for URL
        relative_path = file_path.replace(
            upload_folder, '').lstrip(os.sep).replace(os.sep, '/')
        file_url = f"http://localhost:5000/assets/{relative_path}"

        # Create song record
        song = Song(
            title=title,
            artist=artist,
            album=album,
            duration=duration,
            file_path=file_url,  # Store the full URL
            cover_url=cover_url,
            artist_name=artist_name,
            artist_nickname=artist_nickname,
            nationality=nationality
        )

        db.session.add(song)
        db.session.commit()

        return ApiResponse.success(song.to_dict(), 'Song uploaded successfully')

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error uploading song: {str(e)}", 500)


@music_bp.route('/songs/<int:song_id>/upload', methods=['PUT'])
def update_song_with_file(song_id):
    """Update a song with optional file upload"""
    try:
        song = Song.query.get_or_404(song_id)

        # Handle file upload if present
        file_url = song.file_path  # Keep existing file by default
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                # Validate file type
                if not MusicService.allowed_file(file.filename):
                    return ApiResponse.error('Invalid file type. Allowed: mp3, wav, flac, ogg, m4a, aac', 400)

                # Save new file
                upload_folder = current_app.config['UPLOAD_FOLDER']
                file_path = MusicService.save_file(file, upload_folder)
                if file_path:
                    # Create relative path for URL
                    relative_path = file_path.replace(
                        upload_folder, '').lstrip(os.sep).replace(os.sep, '/')
                    file_url = f"http://localhost:5000/assets/{relative_path}"

        # Get form data and update fields if provided
        if request.form.get('title'):
            song.title = request.form.get('title').strip()
        if request.form.get('artist'):
            song.artist = request.form.get('artist').strip()
        if request.form.get('album'):
            song.album = request.form.get('album').strip() or None
        if request.form.get('duration'):
            try:
                song.duration = int(float(request.form.get('duration')))
            except (ValueError, TypeError):
                pass
        if request.form.get('cover_url'):
            song.cover_url = request.form.get('cover_url').strip() or None
        if request.form.get('artist_name'):
            song.artist_name = request.form.get('artist_name').strip()
        if request.form.get('artist_nickname'):
            song.artist_nickname = request.form.get(
                'artist_nickname').strip() or None
        if request.form.get('nationality'):
            song.nationality = request.form.get('nationality').strip() or None

        # Update file path if changed
        song.file_path = file_url

        db.session.commit()
        return ApiResponse.success(song.to_dict(), 'Song updated successfully')

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating song: {str(e)}", 500)


@music_bp.route('/songs/<int:song_id>/metadata', methods=['PUT'])
def update_song_metadata(song_id):
    """Update song metadata only (no file upload required)"""
    try:
        song = Song.query.get_or_404(song_id)
        data = request.get_json()

        if not data:
            return ApiResponse.error('No data provided', 400)

        # Actualizar campos permitidos
        updateable_fields = ['title', 'artist', 'album', 'cover_url',
                             'artist_name', 'artist_nickname', 'nationality']

        for field in updateable_fields:
            if field in data and data[field] is not None:
                # Sanitizar strings
                if isinstance(data[field], str):
                    clean_value = data[field].strip()
                    if clean_value:  # Solo actualizar si no está vacío
                        setattr(song, field, clean_value)
                else:
                    setattr(song, field, data[field])

        db.session.commit()
        return ApiResponse.success(song.to_dict(), 'Song metadata updated successfully')

    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error updating song metadata: {str(e)}", 500)
