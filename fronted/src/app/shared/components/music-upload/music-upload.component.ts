import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MusicUploadService, SongUploadData, UploadProgress } from '@core/services/music-upload.service';
import { TracksService } from '@core/services/tracks.service';
import { Subject, takeUntil } from 'rxjs';

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

    private destroy$ = new Subject<void>();

    constructor(
        private fb: FormBuilder,
        private uploadService: MusicUploadService,
        private tracksService: TracksService
    ) {
        this.uploadForm = this.fb.group({
            title: ['', [Validators.required, Validators.minLength(1)]],
            artist: ['', [Validators.required, Validators.minLength(1)]],
            album: [''],
            artist_nickname: [''],
            nationality: [''],
            cover_url: [''],
            file: [null, Validators.required]
        });
    }

    ngOnInit(): void {
        // Suscribirse al progreso de subida
        this.uploadService.getUploadProgress()
            .pipe(takeUntil(this.destroy$))
            .subscribe(progress => {
                this.uploadProgress = progress;
            });

        // Suscribirse al estado de subida
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

    // Manejar selección de archivo
    onFileSelected(event: Event): void {
        const target = event.target as HTMLInputElement;
        if (target.files && target.files.length > 0) {
            this.handleFile(target.files[0]);
        }
    }

    // Manejar drag & drop
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

    // Procesar archivo seleccionado
    private handleFile(file: File): void {
        console.log('📁 File selected:', file.name, file.type, file.size);

        // Validar archivo
        const validation = this.uploadService.validateAudioFile(file);
        if (!validation.valid) {
            alert(validation.error);
            return;
        }

        this.selectedFile = file;
        this.uploadForm.patchValue({ file });

        // Auto-completar título si está vacío
        if (!this.uploadForm.get('title')?.value) {
            const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remover extensión
            this.uploadForm.patchValue({ title: fileName });
        }

        // Obtener duración automáticamente
        this.uploadService.getAudioDuration(file)
            .then(duration => {
                console.log('⏱️ Audio duration:', duration, 'seconds');
            })
            .catch(error => {
                console.warn('⚠️ Could not get audio duration:', error);
            });
    }

    // Subir canción
    onSubmit(): void {
        if (!this.uploadForm.valid || !this.selectedFile) {
            console.warn('⚠️ Form invalid or no file selected');
            return;
        } const formData = this.uploadForm.value;
        const songData: SongUploadData = {
            title: formData.title.trim(),
            artist: formData.artist.trim(),
            album: formData.album?.trim() || undefined,
            artist_nickname: formData.artist_nickname?.trim() || undefined,
            nationality: formData.nationality?.trim() || undefined,
            cover_url: formData.cover_url?.trim() || undefined,
            file: this.selectedFile
        };

        console.log('📤 Starting upload:', songData); this.uploadService.uploadSong(songData).subscribe({
            next: (response) => {
                if (response) {
                    console.log('✅ Upload successful:', response);
                    this.resetForm();

                    // Mostrar mensaje de éxito
                    alert('¡Canción subida exitosamente! La lista se actualizará automáticamente.');

                    // Actualizar lista de canciones
                    this.refreshTracksList();
                }
            },
            error: (error) => {
                console.error('❌ Upload failed:', error);
                // Mostrar mensaje de error
                alert(`Error al subir la canción: ${error.message || 'Error desconocido'}`);
            }
        });
    }

    // Resetear formulario
    resetForm(): void {
        this.uploadForm.reset();
        this.selectedFile = null;
        this.uploadService.clearUploadState();
    }

    // Cancelar subida
    cancelUpload(): void {
        // TODO: Implementar cancelación de subida
        this.resetForm();
    }    // Actualizar lista de canciones
    private refreshTracksList(): void {
        // Notificar a todos los componentes que escuchan que las canciones han cambiado
        console.log('🔄 MusicUpload: Triggering tracks refresh after upload');
        this.tracksService.refreshTracks();
    }

    // Getters para validación
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

    // Formatear tamaño de archivo
    formatFileSize(bytes: number): string {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}
