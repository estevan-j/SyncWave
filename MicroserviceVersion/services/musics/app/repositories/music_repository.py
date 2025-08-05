from app.models.music import Music
from app.extensions import db
from typing import List, Optional

class MusicRepository:
    """Repository for managing music records in the database."""

    @staticmethod
    def get_all_musics() -> List[Music]:
        """Retrieve all music records from the database."""
        return Music.query.all()

    @staticmethod
    def get_music_by_id(music_id: int) -> Optional[Music]:
        """Retrieve a music record by its ID."""
        return Music.query.get(music_id)

    @staticmethod
    def get_music_by_title(title: str) -> Optional[Music]:
        """Retrieve a music record by its title."""
        return Music.query.filter_by(title=title).first()

    @staticmethod
    def add_music(music: Music) -> Music:
        """Add a new music record to the database."""
        try:
            db.session.add(music)
            db.session.commit()
            db.session.refresh(music)
            return music
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update_music(music: Music) -> Music:
        """Update an existing music record in the database."""
        try:
            db.session.commit()
            db.session.refresh(music)
            return music
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete_music(music_id: int) -> bool:
        """Delete a music record from the database. Returns True if deleted."""
        music = MusicRepository.get_music_by_id(music_id)
        if not music:
            return False
        try:
            db.session.delete(music)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e