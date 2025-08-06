from app import db
from sqlalchemy import Column, Integer, String, TIMESTAMP, func

class Music(db.Model):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(100), nullable=False)
    album = Column(String(100))
    duration = Column(Integer)
    url = Column(String(500))
    cover_url = Column(String(500))
    artist_name = Column(String(100))
    artist_nickname = Column(String(100))
    nationality = Column(String(10))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp())