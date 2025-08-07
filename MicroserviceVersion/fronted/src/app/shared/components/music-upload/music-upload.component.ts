import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MusicUploadService, CreateSongData, UploadProgress } from '@core/services/music-upload.service';
import { TracksService } from '@core/services/tracks.service';
import { Subject, takeUntil } from 'rxjs';
import { environment } from '../../../../environments/environment';

import { HttpClient, HttpEventType, HttpHeaders } from '@angular/common/http';

@Component({
    selector: 'app-music-upload',
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule],
    templateUrl: './music-upload.component.html',
    styleUrls: ['./music-upload.component.css']
})
export class MusicUploadComponent implements OnInit, OnDestroy {
    uploadForm: FormGroup;
    selectedFile: File | null = null;
    uploadProgress: UploadProgress | null = null;
    isUploading = false;
    dragOver = false;
    songUrl: string | null = null;
    songDuration: number | null = null;
    fileUploadError: string | null = null;

    private destroy$ = new Subject<void>();

    constructor(
        private fb: FormBuilder,
        private uploadService: MusicUploadService,
        private tracksService: TracksService,
        private http: HttpClient
    ) {
        this.uploadForm = this.fb.group({
            title: ['', [Validators.required, Validators.minLength(1)]],
            artist: ['', [Validators.required, Validators.minLength(1)]],
            album: [''],
            cover_url: [''],
            file: [null, Validators.required]
        });
    }

    ngOnInit(): void {
        this.uploadService.getUploadProgress()
            .pipe(takeUntil(this.destroy$))
            .subscribe(progress => {
                this.uploadProgress = progress;
            });

        this.uploadService.getIsUploading()
            .pipe(takeUntil(this.destroy$))
            .subscribe(uploading => {
                this.isUploading = uploading;
            });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
    }

    onFileSelected(event: Event): void {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            this.handleFile(target.files[0]);
        }
    }

    onDragOver(event: DragEvent): void {
        event.preventDefault();
        this.dragOver = true;
    }

    onDragLeave(event: DragEvent): void {
        event.preventDefault();
        this.dragOver = false;
    }

    onFileDrop(event: DragEvent): void {
        event.preventDefault();
        this.dragOver = false;

        if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
            this.handleFile(event.dataTransfer.files[0]);
        }
    }

    private handleFile(file: File): void {
        this.fileUploadError = null;
        this.songUrl = null;
        this.songDuration = null;

        const validation = this.uploadService.validateAudioFile(file);
        if (!validation.valid) {
            alert(validation.error);
            return;
        }

        this.selectedFile = file;
        this.uploadForm.patchValue({ file });

        // Auto-llenar título si está vacío
        if (!this.uploadForm.get('title')?.value) {
            const fileName = file.name.replace(/\.[^/.]+$/, '');
            this.uploadForm.patchValue({ title: fileName });
        }

        // Obtener duración ANTES de subir el archivo
        this.uploadService.getAudioDuration(file)
            .then(duration => {
                console.log('⏱️ Audio duration:', duration, 'seconds');
                this.songDuration = Math.round(duration);
                // Subir archivo DESPUÉS de obtener la duración
                this.uploadFileToBackend(file);
            })
            .catch(error => {
                console.warn('⚠️ Could not get audio duration:', error);
                alert('No se pudo obtener la duración del archivo. Se usará 0 como valor por defecto.');
                this.songDuration = 0;
                this.uploadFileToBackend(file);
            });
    }

    private uploadFileToBackend(file: File): void {
        this.isUploading = true;
        this.fileUploadError = null;
        this.songUrl = null;

        const formData = new FormData();
        formData.append('file', file);

        // Usar la URL base del environment
        const uploadUrl = `${environment.apiUrl}/musics/upload`;

        this.http.post<any>(uploadUrl, formData, {
            reportProgress: true,
            observe: 'events',
            headers: new HttpHeaders({})
        }).subscribe({
            next: (event) => {
                if (event.type === HttpEventType.Response) {
                    if (event.body && event.body.url) {
                        this.songUrl = event.body.url;
                        alert('Archivo subido correctamente. Ahora completa los datos y guarda la canción.');
                    } else {
                        this.fileUploadError = 'No se pudo obtener la URL del archivo subido.';
                        alert(this.fileUploadError);
                    }
                    this.isUploading = false;
                }
            },
            error: (error: any) => {
                this.fileUploadError = error?.error?.error || 'Error al subir el archivo.';
                alert(this.fileUploadError);
                this.isUploading = false;
            }
        });
    }

    onSubmit(): void {
        if (!this.uploadForm.valid || !this.selectedFile || !this.songUrl || this.songDuration === null) {
            alert('Debes seleccionar un archivo válido y esperar a que termine la subida antes de guardar la canción.');
            return;
        }

        const formData = this.uploadForm.value;

        // Crear datos según los campos requeridos por el backend
        const songData: CreateSongData = {
            url: this.songUrl,                           // URL del archivo (obligatorio)
            title: formData.title.trim(),                // Título (obligatorio)
            name: formData.title.trim(),                 // Nombre = título (obligatorio)
            duration: this.songDuration,                 // Duración (obligatorio)
            album: formData.album?.trim() || undefined,  // Álbum (opcional)
            artist: formData.artist.trim(),              // Artista (opcional)
            cover_url: formData.cover_url?.trim() || undefined // URL de portada (opcional)
        };

        console.log('📤 Sending song data:', songData);

        this.uploadService.createSongWithUrl(songData).subscribe({
            next: (response: any) => {
                if (response) {
                    this.resetForm();
                    alert('¡Canción guardada exitosamente!');
                    this.refreshTracksList();
                }
            },
            error: (error: any) => {
                console.error('❌ Error creating song:', error);
                alert(`Error al guardar la canción: ${error.error?.message || error.message || 'Error desconocido'}`);
            }
        });
    }

    resetForm(): void {
        this.uploadForm.reset();
        this.selectedFile = null;
        this.songUrl = null;
        this.songDuration = null;
        this.fileUploadError = null;
        this.uploadService.clearUploadState();
    }

    cancelUpload(): void {
        this.resetForm();
    }

    private refreshTracksList(): void {
        console.log('🔄 MusicUpload: Triggering tracks refresh after upload');
        this.tracksService.refreshTracks();
    }

    get titleInvalid(): boolean {
        const control = this.uploadForm.get('title');
        return !!(control?.invalid && control?.touched);
    }

    get artistInvalid(): boolean {
        const control = this.uploadForm.get('artist');
        return !!(control?.invalid && control?.touched);
    }

    get fileInvalid(): boolean {
        const control = this.uploadForm.get('file');
        return !!(control?.invalid && control?.touched);
    }

    formatFileSize(bytes: number): string {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}