class PlaylistService:
    @staticmethod
    def validate_playlist_data(data):
        """Validate playlist data"""
        errors = []
        
        if not data.get('name'):
            errors.append('Playlist name is required')
        elif len(data.get('name', '').strip()) < 1:
            errors.append('Playlist name cannot be empty')
        elif len(data.get('name', '').strip()) > 100:
            errors.append('Playlist name cannot exceed 100 characters')
            
        if 'description' in data and data['description'] is not None:
            if len(data['description']) > 500:
                errors.append('Description cannot exceed 500 characters')
                
        return errors
    
    @staticmethod
    def get_playlist_duration(playlist, songs_db):
        """Calculate total duration of playlist"""
        total_duration = 0
        for song_id in playlist.songs:
            song = next((s for s in songs_db if s.id == song_id), None)
            if song and song.duration:
                total_duration += song.duration
        return total_duration
    
    @staticmethod
    def get_playlist_with_songs(playlist, songs_db):
        """Get playlist with full song information"""
        playlist_dict = playlist.to_dict()
        
        # Get full song objects
        songs_details = []
        for song_id in playlist.songs:
            song = next((s for s in songs_db if s.id == song_id), None)
            if song:
                songs_details.append(song.to_dict())
        
        playlist_dict['songs_details'] = songs_details
        playlist_dict['total_duration'] = PlaylistService.get_playlist_duration(playlist, songs_db)
        
        return playlist_dict
    
    @staticmethod
    def search_playlists(playlists_db, query):
        """Search playlists by name or description"""
        query = query.lower()
        return [
            playlist for playlist in playlists_db
            if query in playlist.name.lower() or 
               (playlist.description and query in playlist.description.lower())
        ]
    
    @staticmethod
    def get_user_playlists(playlists_db, user_id):
        """Get all playlists for a specific user"""
        return [p for p in playlists_db if p.user_id == user_id]
