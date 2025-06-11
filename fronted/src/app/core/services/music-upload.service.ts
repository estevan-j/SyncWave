import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpRequest } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { TrackModel } from '@core/models/tracks.model';

export interface UploadProgress {
    percentage: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
    message?: string;
}

export interface SongUploadData {
    title: string;
    artist: string;
    album?: string;
    duration?: number;
    file: File;
    // Campos adicionales para el backend
    cover_url?: string;
    artist_name?: string;
    artist_nickname?: string;
    nationality?: string;
}

export interface UploadResponse {
    success: boolean;
    message: string;
    data?: TrackModel;
    error_code?: string;
}

@Injectable({
    providedIn: 'root'
})
export class MusicUploadService {
    private readonly API_URL = 'http://localhost:5000/api/music';

    // Estado de subida
    private uploadProgress$ = new BehaviorSubject<UploadProgress | null>(null);
    private isUploading$ = new BehaviorSubject<boolean>(false);

    constructor(private http: HttpClient) { }

    /**
     * Obtener progreso de subida
     */
    getUploadProgress(): Observable<UploadProgress | null> {
        return this.uploadProgress$.asObservable();
    }

    /**
     * Verificar si hay una subida en progreso
     */
    getIsUploading(): Observable<boolean> {
        return this.isUploading$.asObservable();
    }

    /**
     * Validar archivo de audio
     */
    validateAudioFile(file: File): { valid: boolean; error?: string } {
        const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/aac'];
        const maxSize = 50 * 1024 * 1024; // 50MB

        if (!allowedTypes.includes(file.type)) {
            return {
                valid: false,
                error: 'Formato de archivo no soportado. Use MP3, WAV, OGG, M4A o AAC.'
            };
        }

        if (file.size > maxSize) {
            return {
                valid: false,
                error: 'El archivo es demasiado grande. Máximo 50MB.'
            };
        }

        return { valid: true };
    }

    /**
     * Subir nueva canción
     */
    uploadSong(songData: SongUploadData): Observable<UploadResponse> {
        // Validar archivo
        const validation = this.validateAudioFile(songData.file);
        if (!validation.valid) {
            return new Observable(observer => {
                observer.error({
                    success: false,
                    message: validation.error,
                    error_code: 'INVALID_FILE'
                });
            });
        }        // Preparar FormData
        const formData = new FormData();
        formData.append('file', songData.file);
        formData.append('title', songData.title);
        formData.append('artist', songData.artist);

        if (songData.album) {
            formData.append('album', songData.album);
        }

        if (songData.duration) {
            formData.append('duration', songData.duration.toString());
        }

        // Campos adicionales - usar artist como artist_name por defecto
        formData.append('artist_name', songData.artist_name || songData.artist);

        if (songData.artist_nickname) {
            formData.append('artist_nickname', songData.artist_nickname);
        }

        if (songData.nationality) {
            formData.append('nationality', songData.nationality);
        }

        if (songData.cover_url) {
            formData.append('cover_url', songData.cover_url);
        } console.log('📤 Uploading song:', songData.title, 'by', songData.artist);

        // Crear request con progreso
        const uploadRequest = new HttpRequest('POST', `${this.API_URL}/songs/upload`, formData, {
            reportProgress: true
        });

        this.isUploading$.next(true);
        this.uploadProgress$.next({
            percentage: 0,
            status: 'uploading',
            message: 'Iniciando subida...'
        });

        return this.http.request<UploadResponse>(uploadRequest).pipe(
            map(event => {
                switch (event.type) {
                    case HttpEventType.UploadProgress:
                        if (event.total) {
                            const percentage = Math.round(100 * event.loaded / event.total);
                            this.uploadProgress$.next({
                                percentage,
                                status: 'uploading',
                                message: `Subiendo archivo... ${percentage}%`
                            });
                        }
                        return null as any; // Continuar el stream

                    case HttpEventType.Response:
                        this.isUploading$.next(false);

                        if (event.body?.success) {
                            this.uploadProgress$.next({
                                percentage: 100,
                                status: 'completed',
                                message: 'Canción subida exitosamente'
                            });
                            console.log('✅ Upload completed:', event.body);
                            return event.body;
                        } else {
                            this.uploadProgress$.next({
                                percentage: 0,
                                status: 'error',
                                message: event.body?.message || 'Error al subir la canción'
                            });
                            throw event.body;
                        }

                    default:
                        return null as any;
                }
            }),
            catchError(error => {
                console.error('❌ Upload error:', error);
                this.isUploading$.next(false);
                this.uploadProgress$.next({
                    percentage: 0,
                    status: 'error',
                    message: error.message || 'Error al subir la canción'
                });
                throw error;
            })
        );
    }

    /**
     * Actualizar información de una canción existente
     */    updateSong(songId: number, updateData: Partial<SongUploadData>): Observable<UploadResponse> {
        const formData = new FormData();

        if (updateData.title) formData.append('title', updateData.title);
        if (updateData.artist) formData.append('artist', updateData.artist);
        if (updateData.album) formData.append('album', updateData.album);
        if (updateData.duration) formData.append('duration', updateData.duration.toString());
        if (updateData.file) formData.append('file', updateData.file);

        // Campos adicionales
        if (updateData.artist_name) formData.append('artist_name', updateData.artist_name);
        if (updateData.artist_nickname) formData.append('artist_nickname', updateData.artist_nickname);
        if (updateData.nationality) formData.append('nationality', updateData.nationality);
        if (updateData.cover_url) formData.append('cover_url', updateData.cover_url); console.log('📝 Updating song:', songId);

        return this.http.put<UploadResponse>(`${this.API_URL}/songs/${songId}/upload`, formData);
    }

    /**
     * Eliminar una canción
     */
    deleteSong(songId: number): Observable<UploadResponse> {
        console.log('🗑️ Deleting song:', songId);
        return this.http.delete<UploadResponse>(`${this.API_URL}/songs/${songId}`);
    }

    /**
     * Limpiar estado de subida
     */
    clearUploadState(): void {
        this.uploadProgress$.next(null);
        this.isUploading$.next(false);
    }

    /**
     * Obtener duración de un archivo de audio (usando Web API)
     */
    getAudioDuration(file: File): Promise<number> {
        return new Promise((resolve, reject) => {
            const audio = new Audio();
            const objectUrl = URL.createObjectURL(file);

            audio.addEventListener('loadedmetadata', () => {
                URL.revokeObjectURL(objectUrl);
                resolve(audio.duration);
            });

            audio.addEventListener('error', () => {
                URL.revokeObjectURL(objectUrl);
                reject(new Error('No se pudo cargar el archivo de audio'));
            });

            audio.src = objectUrl;
        });
    }
}
