from datetime import datetime

class Song:
    def __init__(self, id, title, artist, album=None, duration=None, file_path=None, created_at=None):
        self.id = id
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration  # in seconds
        self.file_path = file_path
        self.created_at = created_at or datetime.now()
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
