import os
from flask import Blueprint, request, jsonify, g
from app.repositories.music_repository import MusicRepository
from app.schemas.music_schema import MusicCreate, MusicUpdate, MusicResponse
from app.utils.auth import require_auth, no_auth
from app.utils.supabase_client import supabase
from pydantic import ValidationError
import logging

music_bp = Blueprint('music', __name__, url_prefix='/api/musics')

# Logger básico para el controlador
logger = logging.getLogger("music_controller")

# GET /musics - SIN AUTH TEMPORALMENTE
@music_bp.route('/', methods=['GET', 'OPTIONS'])
@require_auth
def get_all_musics():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
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

# NUEVO: PUT /musics/songs/<int:music_id>/metadata - Para compatibilidad con frontend
@music_bp.route('/<int:music_id>/metadata', methods=['PUT', 'OPTIONS'])
@require_auth
def update_music_metadata(music_id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "PUT,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    request_id = getattr(g, 'request_id', 'unknown')
    music = MusicRepository.get_music_by_id(music_id)
    if not music:
        logger.warning(f"Music not found for metadata update: {music_id}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Music not found', 'request_id': request_id}), 404

    try:
        data = request.get_json()
        # Permitir actualización parcial de metadata
        allowed_fields = ['title', 'artist', 'album', 'genre', 'duration']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update', 'request_id': request_id}), 400
            
        music_update = MusicUpdate(**update_data)
    except (TypeError, ValidationError) as e:
        logger.warning(f"Invalid input for metadata update: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Invalid input', 'details': str(e), 'request_id': request_id}), 400

    for field, value in music_update.dict(exclude_unset=True).items():
        setattr(music, field, value)
    try:
        music = MusicRepository.update_music(music)
        logger.info("Music metadata updated", extra={'custom_request_id': request_id, 'music_id': music_id})
        return jsonify(MusicResponse.from_orm(music).dict()), 200
    except Exception as e:
        logger.error(f"Failed to update music metadata: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Failed to update music metadata', 'details': str(e), 'request_id': request_id}), 500

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
   


@music_bp.route('/upload', methods=['POST', 'OPTIONS'])
@no_auth
def upload_music_file():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "POST,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    request_id = getattr(g, 'request_id', 'unknown')

    if 'file' not in request.files:
        logger.warning("No file field in request", extra={'custom_request_id': request_id})
        return jsonify({'error': 'No file field in request', 'request_id': request_id}), 400

    file = request.files['file']
    if not file or file.filename == '':
        logger.warning("No file selected", extra={'custom_request_id': request_id})
        return jsonify({'error': 'No file selected', 'request_id': request_id}), 400

    allowed_extensions = {'mp3', 'wav', 'flac', 'm4a', 'ogg'}
    filename = file.filename
    if not filename or '.' not in filename or filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        logger.warning("Invalid file extension", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Invalid file extension', 'request_id': request_id}), 400

    try:
        import uuid
        import time
        timestamp = int(time.time())
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}.{file_extension}"

        # Validar tamaño (50MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes", extra={'custom_request_id': request_id})
            return jsonify({'error': 'File too large (max 50MB)', 'request_id': request_id}), 400

        # Subir a Supabase Storage
        file_bytes = file.read()
        bucket_name = "musics"  # Cambia esto si tu bucket tiene otro nombre
        supabase.storage.from_(bucket_name).upload(unique_filename, file_bytes, {"content-type": file.mimetype})

        # Obtener URL pública
        public_url = supabase.storage.from_(bucket_name).get_public_url(unique_filename)

        logger.info("File uploaded to Supabase", extra={'custom_request_id': request_id, 'file': unique_filename})

        return jsonify({
            'message': 'File uploaded successfully',
            'url': public_url,
            'filename': unique_filename,
            'original_filename': filename,
            'file_size': file_size,
            'request_id': request_id
        }), 201

    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}", extra={'custom_request_id': request_id})
        return jsonify({'error': 'Internal server error', 'details': str(e), 'request_id': request_id}), 500