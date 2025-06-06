from datetime import datetime

class Playlist:
    def __init__(self, id, name, description=None, user_id=None, songs=None, created_at=None):
        self.id = id
        self.name = name
        self.description = description
        self.user_id = user_id
        self.songs = songs or []  # List of song IDs
        self.created_at = created_at or datetime.now()
        
    def add_song(self, song_id):
        """Add a song to the playlist if it's not already there"""
        if song_id not in self.songs:
            self.songs.append(song_id)
            
    def remove_song(self, song_id):
        """Remove a song from the playlist if it exists"""
        if song_id in self.songs:
            self.songs.remove(song_id)
        
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'songs': self.songs,
            'song_count': len(self.songs),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
