import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { AuthService } from '@core/services/auth.service';
import { environment } from '../../../environments/environment';

export interface UploadProgress {
    percentage: number;
    status: 'uploading' | 'processing' | 'completed' | 'error';
    message?: string;
}

// Interfaz para datos de canción existentes (para editar/eliminar)
export interface SongUploadData {
    title: string;
    artist: string;
    album?: string;
    duration?: number;
    cover_url?: string;
    artist_name?: string;
    artist_nickname?: string;
    nationality?: string;
}

// Interfaz para crear nueva canción con URL
export interface CreateSongData {
    url: string;        // URL del archivo (obligatorio)
    title: string;      // Título (obligatorio)
    name: string;       // Nombre (obligatorio)
    duration: number;   // Duración (obligatorio)
    album?: string;     // Álbum (opcional)
    artist?: string;    // Artista (opcional)
    cover_url?: string; // URL de portada (opcional)
}

export interface UploadResponse {
    success: boolean;
    message: string;
    data?: any;
    error_code?: string;
}

@Injectable({
    providedIn: 'root'
})
export class MusicUploadService {
    private readonly API_URL = `${environment.apiUrlMusic}/api/musics`;

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

    // Crear nueva canción con URL
    createSongWithUrl(songData: CreateSongData): Observable<UploadResponse> {
        const headers = this.getAuthHeaders();

        console.log('🎵 Creating new song with URL:', songData);

        return this.http.post<UploadResponse>(`${this.API_URL}`, songData, { headers });
    }

    // Actualizar metadatos de canción existente
    updateSongMetadata(songId: number, updateData: Partial<SongUploadData>): Observable<UploadResponse> {
        const headers = this.getAuthHeaders();

        console.log('📝 Updating metadata for song ID:', songId, 'Data:', updateData);

        return this.http.put<UploadResponse>(`${this.API_URL}/${songId}`, updateData, { headers });
    }

    // Eliminar canción
    deleteSong(songId: number): Observable<UploadResponse> {
        const headers = this.getAuthHeaders();

        console.log('🗑️ Deleting song ID:', songId);

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