import { Injectable } from '@angular/core';
import { HttpClient, HttpEventType, HttpRequest, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { TrackModel } from '@core/models/tracks.model';
import { AuthService } from '@core/services/auth.service';
import { environment } from '../../../environments/environment';

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
    file?: File; // Hacer opcional para updates de metadata
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
    private readonly API_URL = `${environment.musicsApiUrl}/api/musics`;

    private uploadProgress$ = new BehaviorSubject<UploadProgress | null>(null);
    private isUploading$ = new BehaviorSubject<boolean>(false);

    constructor(private http: HttpClient, private authService: AuthService) { }

    private getAuthHeaders(): HttpHeaders {
        const token = this.authService.getToken();
        return new HttpHeaders({
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        });
    }

    private getAuthHeadersMultipart(): HttpHeaders {
        const token = this.authService.getToken();
        return new HttpHeaders({
            'Authorization': `Bearer ${token}`
            // No agregar Content-Type para FormData, el browser lo hace automáticamente
        });
    }

    getUploadProgress(): Observable<UploadProgress | null> {
        return this.uploadProgress$.asObservable();
    }

    getIsUploading(): Observable<boolean> {
        return this.isUploading$.asObservable();
    }

    validateAudioFile(file: File): { valid: boolean; error?: string } {
        const allowedTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/ogg', 'audio/m4a', 'audio/aac'];
        const maxSize = 50 * 1024 * 1024;
        if (!allowedTypes.includes(file.type)) {
            return { valid: false, error: 'Formato de archivo no soportado. Use MP3, WAV, OGG, M4A o AAC.' };
        }
        if (file.size > maxSize) {
            return { valid: false, error: 'El archivo es demasiado grande. Máximo 50MB.' };
        }
        return { valid: true };
    }

    uploadSong(songData: SongUploadData): Observable<UploadResponse> {
        if (!songData.file) {
            return new Observable(observer => {
                observer.error({
                    success: false,
                    message: 'Archivo requerido para subida',
                    error_code: 'FILE_REQUIRED'
                });
            });
        }

        const validation = this.validateAudioFile(songData.file);
        if (!validation.valid) {
            return new Observable(observer => {
                observer.error({
                    success: false,
                    message: validation.error,
                    error_code: 'INVALID_FILE'
                });
            });
        }

        const formData = new FormData();
        formData.append('file', songData.file);
        formData.append('title', songData.title);
        formData.append('artist', songData.artist);
        if (songData.album) formData.append('album', songData.album);
        if (songData.duration) formData.append('duration', songData.duration.toString());
        formData.append('artist_name', songData.artist_name || songData.artist);
        if (songData.artist_nickname) formData.append('artist_nickname', songData.artist_nickname);
        if (songData.nationality) formData.append('nationality', songData.nationality);
        if (songData.cover_url) formData.append('cover_url', songData.cover_url);

        const headers = this.getAuthHeadersMultipart();
        const uploadRequest = new HttpRequest('POST', `${this.API_URL}/upload`, formData, {
            reportProgress: true,
            headers: headers
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
                        return null as any;
                    case HttpEventType.Response:
                        this.isUploading$.next(false);
                        if (event.body?.success) {
                            this.uploadProgress$.next({
                                percentage: 100,
                                status: 'completed',
                                message: 'Canción subida exitosamente'
                            });
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

    // ✅ NUEVA FUNCIÓN: Solo para actualizar metadatos (sin archivo)
    updateSongMetadata(songId: number, updateData: Partial<SongUploadData>): Observable<UploadResponse> {
        const headers = this.getAuthHeaders();

        // Crear objeto JSON limpio (sin propiedades file)
        const metadataUpdate: any = {};
        if (updateData.title) metadataUpdate.title = updateData.title;
        if (updateData.artist) metadataUpdate.artist = updateData.artist;
        if (updateData.album) metadataUpdate.album = updateData.album;
        if (updateData.duration) metadataUpdate.duration = updateData.duration;
        if (updateData.artist_name) metadataUpdate.artist_name = updateData.artist_name;
        if (updateData.artist_nickname) metadataUpdate.artist_nickname = updateData.artist_nickname;
        if (updateData.nationality) metadataUpdate.nationality = updateData.nationality;
        if (updateData.cover_url) metadataUpdate.cover_url = updateData.cover_url;

        console.log('📝 Updating metadata for song ID:', songId, 'Data:', metadataUpdate);

        return this.http.put<UploadResponse>(`${this.API_URL}/${songId}`, metadataUpdate, { headers });
    }

    // ✅ MANTENER FUNCIÓN ORIGINAL para cuando se necesite subir archivo
    updateSong(songId: number, updateData: Partial<SongUploadData>): Observable<UploadResponse> {
        // Si hay archivo, usar FormData
        if (updateData.file) {
            const formData = new FormData();
            if (updateData.title) formData.append('title', updateData.title);
            if (updateData.artist) formData.append('artist', updateData.artist);
            if (updateData.album) formData.append('album', updateData.album);
            if (updateData.duration) formData.append('duration', updateData.duration.toString());
            if (updateData.file) formData.append('file', updateData.file);
            if (updateData.artist_name) formData.append('artist_name', updateData.artist_name);
            if (updateData.artist_nickname) formData.append('artist_nickname', updateData.artist_nickname);
            if (updateData.nationality) formData.append('nationality', updateData.nationality);
            if (updateData.cover_url) formData.append('cover_url', updateData.cover_url);

            const headers = this.getAuthHeadersMultipart();
            return this.http.put<UploadResponse>(`${this.API_URL}/${songId}`, formData, { headers });
        } else {
            // Si no hay archivo, usar JSON para metadatos
            return this.updateSongMetadata(songId, updateData);
        }
    }

    deleteSong(songId: number): Observable<UploadResponse> {
        const headers = this.getAuthHeaders();
        return this.http.delete<UploadResponse>(`${this.API_URL}/${songId}`, { headers });
    }

    clearUploadState(): void {
        this.uploadProgress$.next(null);
        this.isUploading$.next(false);
    }

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