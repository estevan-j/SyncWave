import re

class Validators:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username or len(username) < 3:
            return False
        if len(username) > 50:
            return False
        # Only allow alphanumeric characters, hyphens, and underscores
        return re.match(r'^[a-zA-Z0-9_-]+$', username) is not None
    
    @staticmethod
    def validate_song_title(title):
        """Validate song title"""
        return title and len(title.strip()) > 0 and len(title.strip()) <= 200
    
    @staticmethod
    def validate_artist_name(artist):
        """Validate artist name"""
        return artist and len(artist.strip()) > 0 and len(artist.strip()) <= 100
    
    @staticmethod
    def validate_playlist_name(name):
        """Validate playlist name"""
        return name and len(name.strip()) > 0 and len(name.strip()) <= 100
    
    @staticmethod
    def validate_duration(duration):
        """Validate song duration (in seconds)"""
        try:
            duration_int = int(duration)
            return duration_int > 0 and duration_int <= 86400  # Max 24 hours
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_file_extension(filename, allowed_extensions):
        """Validate file extension"""
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
