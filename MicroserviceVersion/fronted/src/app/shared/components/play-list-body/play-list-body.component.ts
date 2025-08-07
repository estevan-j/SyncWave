import { Component, OnInit, OnDestroy } from '@angular/core';
import { TrackModel } from '@core/models/tracks.model';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { OrderlistPipe } from '@shared/pipe/orderlist.pipe';
import { TracksService } from '@core/services/tracks.service';
import { MultimediaService } from '@core/services/multimedia.service';
import { FavoritesService } from '@core/services/favorites.service';
import { MusicUploadService, SongUploadData } from '@core/services/music-upload.service';
import { Subject, takeUntil, combineLatest, Observable } from 'rxjs';

@Component({
  selector: 'app-play-list-body',
  standalone: true,
  imports: [CommonModule, FormsModule, OrderlistPipe],
  templateUrl: './play-list-body.component.html',
  styleUrl: './play-list-body.component.css'
})
export class PlayListBodyComponent implements OnInit, OnDestroy {
  tracks: Array<TrackModel> = [];
  optionSort: { property: string | null, order: string } = { property: null, order: 'asc' };
  loading: boolean = false;
  error: string | null = null;
  currentTrack: TrackModel | null = null;
  favoriteIds: number[] = [];

  // Estado de edición
  editingTrack: TrackModel | null = null;
  editForm: any = {};

  private destroy$ = new Subject<void>();

  constructor(
    private tracksService: TracksService,
    private multimediaService: MultimediaService,
    private favoritesService: FavoritesService,
    private musicUploadService: MusicUploadService,
    private http: HttpClient
  ) { }

  ngOnInit(): void {
    console.log('🎵 PlayListBodyComponent initialized - Loading tracks from API');
    this.loadTracks();

    // Suscribirse a la canción actual
    this.multimediaService.currentTrack
      .pipe(takeUntil(this.destroy$))
      .subscribe(track => {
        this.currentTrack = track;
      });

    // Suscribirse a los favoritos del usuario
    this.favoritesService.getUserFavorites()
      .pipe(takeUntil(this.destroy$))
      .subscribe(favorites => {
        console.log('🔥 Favorites updated:', favorites);
        this.favoriteIds = favorites;
      });

    // Suscribirse a actualizaciones de canciones
    this.tracksService.tracksRefresh$
      .pipe(takeUntil(this.destroy$))
      .subscribe(shouldRefresh => {
        if (shouldRefresh) {
          console.log('🔄 PlayListBody: Tracks refresh triggered, reloading...');
          this.loadTracks();
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadTracks(): void {
    this.loading = true;
    this.error = null;

    this.tracksService.getAllTracks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tracks) => {
          console.log('✅ PlayListBody - Tracks loaded:', tracks?.length || 0);
          this.tracks = tracks || [];
          this.loading = false;
        },
        error: (error) => {
          console.error('❌ PlayListBody - Error loading tracks:', error);
          this.error = 'Error al cargar las canciones';
          this.loading = false;
          this.tracks = [];
        }
      });
  }

  // ✅ Método para reproducir track
  playTrack(track: TrackModel): void {
    console.log('🎵 Playing track from playlist:', track.name);
    this.multimediaService.setTrack(track);
    this.multimediaService.play();
  }

  // ✅ Método para verificar track actual
  isCurrentTrack(track: TrackModel): boolean {
    return this.currentTrack?._id === track._id;
  }

  // ✅ Método para cambiar ordenamiento
  changeSort(property: string): void {
    const { order } = this.optionSort;
    this.optionSort = {
      property: property,
      order: order === 'asc' ? 'desc' : 'asc'
    };
    console.log('🔄 Sort changed:', this.optionSort);
  }

  // ✅ Método para reintentar carga
  retryLoad(): void {
    console.log('🔄 PlayListBody - Retry loading tracks');
    this.loadTracks();
  }

  // ✅ Método para formatear duración
  formatDuration(seconds: number | undefined): string {
    if (!seconds || isNaN(seconds)) return '--:--';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  // ✅ Método para formatear fecha
  formatDate(dateString: string | undefined): string {
    if (!dateString) return 'Sin fecha';

    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES');
    } catch {
      return 'Sin fecha';
    }
  }

  // 🔥 Métodos para manejar favoritos
  isFavorite(track: TrackModel): boolean {
    return this.favoriteIds.includes(track._id);
  }

  toggleFavorite(track: TrackModel): void {
    console.log('🔥 Toggling favorite for track:', track.name, 'ID:', track._id);

    this.favoritesService.toggleFavorite(track._id).subscribe({
      next: (isFavorite) => {
        console.log('✅ Favorite toggled:', isFavorite ? 'Added' : 'Removed');
      },
      error: (error) => {
        console.error('❌ Error toggling favorite:', error);
        // TODO: Mostrar mensaje de error al usuario
      }
    });
  }

  /**
   * Iniciar edición de canción
   */
  startEdit(track: TrackModel, event: Event): void {
    event.stopPropagation();
    console.log('✏️ Starting edit for:', track.name);

    this.editingTrack = track;
    this.editForm = {
      title: track.name,
      artist: track.artist,
      album: track.album,
      cover_url: track.cover_url
    };
  }

  /**
   * Cancelar edición
   */
  cancelEdit(): void {
    console.log('❌ Cancelling edit form');
    this.editingTrack = null;
    this.editForm = {};
    this.error = null; // Limpiar errores al cancelar
  }

  /**
   * Guardar cambios usando MusicUploadService - SOLO METADATOS
   */
  saveEdit(): void {
    if (!this.editingTrack) return;

    console.log('💾 Saving metadata changes for:', this.editingTrack.name);

    const updateData: Partial<SongUploadData> = {
      title: this.editForm.title,
      artist: this.editForm.artist,
      album: this.editForm.album,
      cover_url: this.editForm.cover_url
    };

    this.musicUploadService.updateSongMetadata(Number(this.editingTrack._id), updateData)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response: any) => {
          console.log('✅ Song metadata updated successfully:', response);

          if (response && (response.success !== false)) {
            // ✅ 1. CERRAR el formulario de edición PRIMERO
            this.cancelEdit();
            console.log('📝 Edit form closed after successful update');

            // ✅ 2. RECARGAR las canciones desde el servidor
            this.loadTracks();
            console.log('🔄 Tracks reloaded after successful update');

            // ✅ 3. NOTIFICAR a otros componentes que las canciones han cambiado
            this.tracksService.refreshTracks();
            console.log('� Other components notified of track changes');

            // ✅ 4. Mensaje de éxito (opcional)
            console.log('✅ Song updated successfully and UI refreshed');
          } else {
            this.error = response?.message || 'Error al actualizar la información de la canción';
            console.error('❌ Update failed:', this.error);
          }
        },
        error: (error: any) => {
          console.error('❌ Error updating song metadata:', error);
          this.error = error.error?.message || error.message || 'Error al actualizar la información de la canción';
          // No cerrar el formulario en caso de error para que el usuario pueda reintentarlo
        }
      });
  }

  /**
   * Eliminar canción usando MusicUploadService
   */
  deleteSong(track: TrackModel, event: Event): void {
    event.stopPropagation();

    const confirmMessage = `¿Estás seguro de que quieres eliminar "${track.name}" permanentemente? Esta acción no se puede deshacer.`;

    if (confirm(confirmMessage)) {
      console.log('🗑️ Deleting song:', track.name);

      this.musicUploadService.deleteSong(Number(track._id))
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response: any) => {
            console.log('✅ Song deleted successfully:', response);

            if (response && (response.success !== false)) {
              // ✅ 1. CERRAR cualquier formulario de edición abierto
              if (this.editingTrack && this.editingTrack._id === track._id) {
                this.cancelEdit();
                console.log('📝 Edit form closed after deletion');
              }

              // ✅ 2. Remover de favoritos si está en favoritos
              if (this.isFavorite(track)) {
                this.favoritesService.removeFromFavorites(Number(track._id))
                  .pipe(takeUntil(this.destroy$))
                  .subscribe({
                    next: () => {
                      console.log('✅ Song removed from favorites');
                    },
                    error: (error: any) => {
                      console.error('❌ Error removing from favorites:', error);
                    }
                  });
              }

              // ✅ 3. RECARGAR las canciones desde el servidor
              this.loadTracks();
              console.log('🔄 Tracks reloaded after successful deletion');

              // ✅ 4. NOTIFICAR a otros componentes que las canciones han cambiado
              this.tracksService.refreshTracks();
              console.log('📡 Other components notified of track deletion');

              // ✅ 5. Limpiar errores
              this.error = null;

              console.log('✅ Song deleted successfully and UI refreshed');
            } else {
              this.error = response?.message || 'Error al eliminar la canción';
              console.error('❌ Deletion failed:', this.error);
            }
          },
          error: (error: any) => {
            console.error('❌ Error deleting song:', error);
            this.error = error.error?.message || error.message || 'Error al eliminar la canción';
          }
        });
    }
  }

  /**
   * Helper para manejar errores de imagen
   */
  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = 'assets/img/default-cover.png';
  }

  /**
   * Helper para ocultar imagen en caso de error
   */
  onImageErrorHide(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.style.display = 'none';
  }
}