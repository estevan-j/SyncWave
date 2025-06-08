from flask import Blueprint, request, jsonify
from app.models.database import db, User, Song, FavoriteSong
from app.utils.responses import ApiResponse
from sqlalchemy.exc import IntegrityError

favorites_bp = Blueprint('favorites', __name__)

@favorites_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id):
    """Get all favorite songs for a user"""
    try:
        user = User.query.get_or_404(user_id)
        favorites = FavoriteSong.query.filter_by(user_id=user_id).order_by(FavoriteSong.added_at.desc()).all()
        
        return ApiResponse.success({
            'user_id': user_id,
            'email': user.email,
            'favorites': [favorite.to_dict() for favorite in favorites],
            'total_favorites': len(favorites)
        })
    except Exception as e:
        return ApiResponse.error(f"Error fetching favorites: {str(e)}", 500)

@favorites_bp.route('/user/<int:user_id>/song/<int:song_id>', methods=['POST'])
def add_favorite(user_id, song_id):
    """Add a song to user's favorites"""
    try:
        # Verificar que el usuario y la canción existen
        user = User.query.get_or_404(user_id)
        song = Song.query.get_or_404(song_id)
        
        # Verificar si ya está en favoritos
        existing_favorite = FavoriteSong.query.filter_by(user_id=user_id, song_id=song_id).first()
        if existing_favorite:
            return ApiResponse.error("Song is already in favorites", 409)
        
        # Crear nuevo favorito
        favorite = FavoriteSong(user_id=user_id, song_id=song_id)
        db.session.add(favorite)
        db.session.commit()
        
        return ApiResponse.success({
            'message': 'Song added to favorites',
            'favorite': favorite.to_dict()
        })
        
    except IntegrityError:
        db.session.rollback()
        return ApiResponse.error("Song is already in favorites", 409)
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error adding favorite: {str(e)}", 500)

@favorites_bp.route('/user/<int:user_id>/song/<int:song_id>', methods=['DELETE'])
def remove_favorite(user_id, song_id):
    """Remove a song from user's favorites"""
    try:
        favorite = FavoriteSong.query.filter_by(user_id=user_id, song_id=song_id).first()
        
        if not favorite:
            return ApiResponse.error("Song not found in favorites", 404)
        
        db.session.delete(favorite)
        db.session.commit()
        
        return ApiResponse.success({
            'message': 'Song removed from favorites',
            'user_id': user_id,
            'song_id': song_id
        })
        
    except Exception as e:
        db.session.rollback()
        return ApiResponse.error(f"Error removing favorite: {str(e)}", 500)

@favorites_bp.route('/user/<int:user_id>/song/<int:song_id>/check', methods=['GET'])
def check_favorite(user_id, song_id):
    """Check if a song is in user's favorites"""
    try:
        favorite = FavoriteSong.query.filter_by(user_id=user_id, song_id=song_id).first()
        
        return ApiResponse.success({
            'user_id': user_id,
            'song_id': song_id,
            'is_favorite': favorite is not None,
            'added_at': favorite.added_at.isoformat() if favorite else None
        })
        
    except Exception as e:
        return ApiResponse.error(f"Error checking favorite: {str(e)}", 500)

@favorites_bp.route('/song/<int:song_id>/users', methods=['GET'])
def get_song_favorites(song_id):
    """Get all users who have favorited a specific song"""
    try:
        song = Song.query.get_or_404(song_id)
        favorites = FavoriteSong.query.filter_by(song_id=song_id).all()
        
        users = []
        for favorite in favorites:
            users.append({
                'user_id': favorite.user_id,
                'email': favorite.user.email,
                'added_at': favorite.added_at.isoformat()
            })
        
        return ApiResponse.success({
            'song_id': song_id,
            'song_title': song.title,
            'favorited_by': users,
            'total_favorites': len(users)
        })
        
    except Exception as e:
        return ApiResponse.error(f"Error fetching song favorites: {str(e)}", 500)
