import os
from werkzeug.utils import secure_filename

class MusicService:
    ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'ogg', 'm4a', 'aac'}
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in MusicService.ALLOWED_EXTENSIONS
    
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
        """Validate song data"""
        errors = []
        
        if not data.get('title'):
            errors.append('Title is required')
        elif len(data.get('title', '').strip()) < 1:
            errors.append('Title cannot be empty')
            
        if not data.get('artist'):
            errors.append('Artist is required')
        elif len(data.get('artist', '').strip()) < 1:
            errors.append('Artist cannot be empty')
            
        if 'duration' in data and data['duration'] is not None:
            try:
                duration = int(data['duration'])
                if duration < 0:
                    errors.append('Duration must be positive')
            except (ValueError, TypeError):
                errors.append('Duration must be a valid number')
                
        return errors
    
    @staticmethod
    def get_file_duration(file_path):
        """Get duration of audio file (placeholder)"""
        # Aquí podrías usar librerías como mutagen o librosa
        # Por ahora retornamos None como placeholder
        return None
    
    @staticmethod
    def filter_songs_by_genre(songs_db, genre):
        """Filter songs by genre (if implemented in Song model)"""
        # Placeholder para futura funcionalidad
        return songs_db
    
    @staticmethod
    def get_popular_songs(songs_db, limit=10):
        """Get popular songs (placeholder implementation)"""
        # Por ahora retorna las primeras canciones
        return songs_db[:limit]
