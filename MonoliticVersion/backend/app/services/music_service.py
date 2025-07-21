import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_


class MusicService:
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'}

    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower(
               ) in MusicService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_file(file, upload_folder):
        """Save uploaded file to disk"""
        if file and MusicService.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)

            # Create upload folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)

            file.save(file_path)
            return file_path
        return None

    @staticmethod
    def validate_song_data(data):
        """Validate song data comprehensively"""
        errors = []

        # Validar título
        if not data.get('title'):
            errors.append('Title is required')
        elif len(data.get('title', '').strip()) < 1:
            errors.append('Title cannot be empty')
        elif len(data.get('title', '').strip()) > 200:
            errors.append('Title cannot exceed 200 characters')

        # Validar artista
        if not data.get('artist'):
            errors.append('Artist is required')
        elif len(data.get('artist', '').strip()) < 1:
            errors.append('Artist cannot be empty')
        elif len(data.get('artist', '').strip()) > 100:
            errors.append('Artist cannot exceed 100 characters')

        # Validar álbum (opcional)
        if data.get('album') and len(data.get('album', '').strip()) > 100:
            errors.append('Album cannot exceed 100 characters')

        # Validar duración
        if 'duration' in data and data['duration'] is not None:
            try:
                duration = int(data['duration'])
                if duration < 0:
                    errors.append('Duration must be positive')
                elif duration > 7200:  # 2 horas máximo
                    errors.append(
                        'Duration cannot exceed 2 hours (7200 seconds)')
            except (ValueError, TypeError):
                errors.append('Duration must be a valid number')

        # Validar URLs
        if data.get('file_path') and len(data.get('file_path', '')) > 500:
            errors.append('File path cannot exceed 500 characters')

        if data.get('cover_url') and len(data.get('cover_url', '')) > 500:
            errors.append('Cover URL cannot exceed 500 characters')

        return errors

    @staticmethod
    def search_songs_by_criteria(db, Song, title=None, artist=None, query=None):
        """Search songs by multiple criteria"""
        if query:
            # Búsqueda general
            return Song.query.filter(
                or_(
                    Song.title.ilike(f'%{query}%'),
                    Song.artist.ilike(f'%{query}%'),
                    Song.album.ilike(f'%{query}%'),
                    Song.artist_name.ilike(f'%{query}%'),
                    Song.artist_nickname.ilike(f'%{query}%')
                )
            ).all()

        # Búsqueda específica por título y artista
        filters = []
        if title:
            filters.append(Song.title.ilike(f'%{title}%'))
        if artist:
            filters.append(or_(
                Song.artist.ilike(f'%{artist}%'),
                Song.artist_name.ilike(f'%{artist}%'),
                Song.artist_nickname.ilike(f'%{artist}%')
            ))

        if filters:
            return Song.query.filter(*filters).all()

        return []

    @staticmethod
    def check_duplicate_song(db, Song, title, artist):
        """Check if song already exists"""
        return Song.query.filter(
            Song.title.ilike(title.strip()),
            or_(
                Song.artist.ilike(artist.strip()),
                Song.artist_name.ilike(artist.strip())
            )
        ).first()

    @staticmethod
    def get_file_duration(file_path):
        """Get duration of audio file (placeholder)"""
        # Aquí podrías usar librerías como mutagen o librosa
        return None

    @staticmethod
    def sanitize_song_data(data):
        """Sanitize and clean song data"""
        sanitized = {}

        # Limpiar strings
        string_fields = ['title', 'artist', 'album',
                         'artist_name', 'artist_nickname', 'nationality']
        for field in string_fields:
            if data.get(field):
                sanitized[field] = data[field].strip()

        # Procesar otros campos
        if 'duration' in data and data['duration'] is not None:
            try:
                sanitized['duration'] = int(data['duration'])
            except (ValueError, TypeError):
                pass

        # URLs
        url_fields = ['file_path', 'cover_url']
        for field in url_fields:
            if data.get(field):
                sanitized[field] = data[field].strip()

        return sanitized
