from app.schemas.music_schema import MusicCreate, MusicResponse, MusicUpdate
from app.repositories.music_repository import MusicRepository
from app.models.music import Music
from typing import List, Optional

class MusicService:
    """Manages music records and interacts with the MusicRepository."""
    
    @staticmethod
    def get_all_musics() -> List[MusicResponse]:
        """Retrieve all music records."""
        musics = MusicRepository.get_all_musics()
        return [MusicResponse.from_orm(music) for music in musics]

    @staticmethod
    def get_music_by_title(title: str) -> Optional[MusicResponse]:
        """Retrieve a music record by its title."""
        music = MusicRepository.get_music_by_title(title)
        return MusicResponse.from_orm(music) if music else None

    @staticmethod
    def add_music(music_data: MusicCreate) -> MusicResponse:
        """Add a new music record."""
        music = Music(**music_data.dict())
        added_music = MusicRepository.add_music(music)
        return MusicResponse.from_orm(added_music)

    @staticmethod
    def update_music(music_id: int, music_data: MusicUpdate) -> Optional[MusicResponse]:
        """Update an existing music record."""
        music = MusicRepository.get_music_by_id(music_id)
        if not music:
            return None
        for key, value in music_data.dict(exclude_unset=True).items():
            setattr(music, key, value)
        updated_music = MusicRepository.update_music(music)
        return MusicResponse.from_orm(updated_music)

    @staticmethod
    def delete_music(music_id: int) -> bool:
        """Delete a music record."""
        return MusicRepository.delete_music(music_id)