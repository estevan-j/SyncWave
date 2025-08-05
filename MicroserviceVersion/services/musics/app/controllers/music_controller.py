from flask import Blueprint, request, jsonify, g
from app.repositories.music_repository import MusicRepository
from app.schemas.music_schema import MusicCreate, MusicUpdate, MusicResponse
from app.utils.auth import require_auth
from app.utils.supabase_client import supabase
from pydantic import ValidationError
import logging

from microservice_logging import get_logger

music_bp = Blueprint('music', __name__, url_prefix='/api/musics')

# Logger básico para el controlador
logger = get_logger("music_controller")

# GET /musics
@music_bp.route('/', methods=['GET'])
@require_auth
def get_all_musics():
    request_id = getattr(g, 'request_id', 'unknown')
    try:
        musics = MusicRepository.get_all_musics()
        return jsonify([MusicResponse.from_orm(m).dict() for m in musics]), 200
    except Exception as e:
        logger.error(f"Error fetching all musics: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to fetch musics', 'details': str(e), 'request_id': request_id}), 500

# GET /musics/<int:music_id>
@music_bp.route('/<int:music_id>', methods=['GET'])
@require_auth
def get_musics_by_id(music_id):
    request_id = getattr(g, 'request_id', 'unknown')
    try:
        music = MusicRepository.get_music_by_id(music_id)
        if not music:
            logger.warning(f"Music not found: {music_id}", extra={'custom_request_id': request_id})
            return jsonify({'error': 'Music not found', 'request_id': request_id}), 404
        return jsonify(MusicResponse.from_orm(music).dict()), 200
    except Exception as e:
        logger.error(f"Error fetching music by id: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to fetch music', 'details': str(e), 'request_id': request_id}), 500

# POST /musics
@music_bp.route('/', methods=['POST'])
@require_auth
def create_music():
    request_id = getattr(g, 'request_id', 'unknown')
    try:
        data = request.get_json()
        music_in = MusicCreate(**data)
    except (TypeError, ValidationError) as e:
        logger.warning(f"Invalid input for create: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Invalid input', 'details': str(e), 'request_id': request_id}), 400

    from app.models.music import Music
    music = Music(**music_in.dict())
    try:
        music = MusicRepository.add_music(music)
        if logger.isEnabledFor(logging.INFO):
            logger.info("Music created", extra={'custom_request_id': request_id, 'music_title': music.title})
        return jsonify(MusicResponse.from_orm(music).dict()), 201
    except Exception as e:
        logger.error(f"Failed to create music: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to create music', 'details': str(e), 'request_id': request_id}), 500

# PUT /musics/<int:music_id>
@music_bp.route('/<int:music_id>', methods=['PUT'])
@require_auth
def update_music(music_id):
    request_id = getattr(g, 'request_id', 'unknown')
    music = MusicRepository.get_music_by_id(music_id)
    if not music:
        logger.warning(f"Music not found for update: {music_id}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Music not found', 'request_id': request_id}), 404

    try:
        data = request.get_json()
        music_update = MusicUpdate(**data)
    except (TypeError, ValidationError) as e:
        logger.warning(f"Invalid input for update: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Invalid input', 'details': str(e), 'request_id': request_id}), 400

    for field, value in music_update.dict(exclude_unset=True).items():
        setattr(music, field, value)
    try:
        music = MusicRepository.update_music(music)
        if logger.isEnabledFor(logging.INFO):
            logger.info("Music updated", extra={'custom_request_id': request_id, 'music_id': music_id})
        return jsonify(MusicResponse.from_orm(music).dict()), 200
    except Exception as e:
        logger.error(f"Failed to update music: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to update music', 'details': str(e), 'request_id': request_id}), 500

# DELETE /musics/<int:music_id>
@music_bp.route('/<int:music_id>', methods=['DELETE'])
@require_auth
def delete_music(music_id):
    request_id = getattr(g, 'request_id', 'unknown')
    try:
        deleted = MusicRepository.delete_music(music_id)
        if not deleted:
            logger.warning(f"Music not found for delete: {music_id}", extra={'custom_request_id': request_id})
            return jsonify({'error': 'Music not found', 'request_id': request_id}), 404
        if logger.isEnabledFor(logging.INFO):
            logger.info("Music deleted", extra={'custom_request_id': request_id, 'music_id': music_id})
        return jsonify({'message': 'Music deleted', 'request_id': request_id}), 200
    except Exception as e:
        logger.error(f"Failed to delete music: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to delete music', 'details': str(e), 'request_id': request_id}), 500
    
@music_bp.route('/upload', methods=['POST'])
@require_auth
def upload_music_file():
    """
    Endpoint to upload a music file to Supabase Storage.
    Expects a multipart/form-data with a file field named 'file'.
    """
    request_id = getattr(g, 'request_id', 'unknown')
    file = request.files.get('file')
    if not file:
        logger.warning("No file provided for upload", extra={'custom_request_id': request_id})
        return jsonify({'error': 'No file provided', 'request_id': request_id}), 400

    allowed_extensions = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}
    filename = file.filename
    if not filename or '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        logger.warning("Invalid file extension", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Invalid file extension', 'request_id': request_id}), 400

    try:
        SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'musics')
        file_bytes = file.read()
        storage_path = f"{filename}"

        # Subir a Supabase Storage
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(storage_path, file_bytes, file.content_type, upsert=True)
        if hasattr(res, 'error') and res.error:
            logger.error(f"Supabase upload error: {res.error}", extra={'custom_request_id': request_id})
            return jsonify({'error': 'Failed to upload file', 'details': str(res.error), 'request_id': request_id}), 500

        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(storage_path)
        logger.info("File uploaded to Supabase", extra={'custom_request_id': request_id, 'file': filename})

        return jsonify({'message': 'File uploaded', 'url': public_url, 'request_id': request_id}), 201

    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to upload file', 'details': str(e), 'request_id': request_id}), 500
    