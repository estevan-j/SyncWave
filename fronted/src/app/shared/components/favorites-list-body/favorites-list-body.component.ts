import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { TrackModel } from '@core/models/tracks.model';
import { FavoritesService } from '@core/services/favorites.service';
import { MultimediaService } from '@core/services/multimedia.service';
import { MusicUploadService } from '@core/services/music-upload.service';
import { TracksService } from '@core/services/tracks.service';
import { OrderlistPipe } from '@shared/pipe/orderlist.pipe';
import { Subject, takeUntil, forkJoin, Observable } from 'rxjs';

@Component({
  selector: 'app-favorites-list-body',
  standalone: true,
  imports: [CommonModule, FormsModule, OrderlistPipe],
  templateUrl: './favorites-list-body.component.html',
  styleUrl: './favorites-list-body.component.css'
})
export class FavoritesListBodyComponent implements OnInit, OnDestroy {
  favoritesList: TrackModel[] = [];
  loading = false;
  error: string | null = null;
  private destroy$ = new Subject<void>();

  // Estado de ordenamiento
  optionSort: { property: string | null, order: string } = { property: null, order: 'asc' };

  // Estado de edición
  editingTrack: TrackModel | null = null;
  editForm: any = {};

  // Track actual para comparación
  currentTrack: TrackModel | null = null; constructor(
    private favoritesService: FavoritesService,
    private multimediaService: MultimediaService,
    private musicUploadService: MusicUploadService,
    private tracksService: TracksService,
    private http: HttpClient
  ) { }
  ngOnInit(): void {
    console.log('🎵 FavoritesListBodyComponent initialized');
    this.loadFavorites();

    // Suscribirse al track actual
    this.multimediaService.currentTrack
      .pipe(takeUntil(this.destroy$))
      .subscribe(track => {
        this.currentTrack = track;
      });

    // Suscribirse a cambios en favoritos para recargar automáticamente
    this.favoritesService.getUserFavorites()
      .pipe(takeUntil(this.destroy$))
      .subscribe(favoriteIds => {
        // Solo recargar si la lista ya se había cargado antes
        if (this.favoritesList.length > 0 || favoriteIds.length > 0) {
          console.log('🔄 Favorites changed, reloading list...');
          this.loadFavorites();
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  /**
   * Cargar lista de favoritos
   */
  loadFavorites(): void {
    this.loading = true;
    this.error = null;

    // Obtener IDs de favoritos y todas las canciones
    forkJoin({
      favoriteIds: this.favoritesService.getUserFavorites(),
      allTracks: this.tracksService.getAllTracks()
    })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: ({ favoriteIds, allTracks }) => {
          console.log('✅ Favorite IDs:', favoriteIds);
          console.log('✅ All tracks:', allTracks.length);

          // Filtrar solo las canciones que están en favoritos
          this.favoritesList = allTracks.filter(track =>
            favoriteIds.includes(Number(track._id))
          );

          console.log('✅ Favorites loaded:', this.favoritesList.length);
          this.loading = false;
        },
        error: (error: any) => {
          console.error('❌ Error loading favorites:', error);
          this.error = 'Error al cargar favoritos';
          this.loading = false;
        }
      });
  }

  /**
   * Reproducir canción
   */
  playTrack(track: TrackModel): void {
    console.log('▶️ Playing track:', track.name);
    this.multimediaService.setTrack(track);
  }  /**
   * Verificar si es la canción actual
   */
  isCurrentTrack(track: TrackModel): boolean {
    return this.currentTrack?._id === track._id;
  }
  /**
   * Eliminar de favoritos
   */
  removeFavorite(track: TrackModel, event: Event): void {
    event.stopPropagation();

    if (confirm(`¿Estás seguro de que quieres quitar "${track.name}" de tus favoritos?`)) {
      console.log('💔 Removing from favorites:', track.name);

      this.favoritesService.removeFromFavorites(Number(track._id))
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            console.log('✅ Removed from favorites successfully');
            // Remover de la lista local
            this.favoritesList = this.favoritesList.filter(t => t._id !== track._id);
          },
          error: (error: any) => {
            console.error('❌ Error removing favorite:', error);
            this.error = 'Error al quitar de favoritos';
          }
        });
    }
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
    this.editingTrack = null;
    this.editForm = {};
  }
  /**
   * Guardar cambios (solo metadatos, sin archivo)
   */
  saveEdit(): void {
    if (!this.editingTrack) return;

    console.log('💾 Saving metadata changes for:', this.editingTrack.name);

    // Usar endpoint específico para actualizar solo metadatos
    this.updateSongMetadata(Number(this.editingTrack._id), {
      title: this.editForm.title,
      artist: this.editForm.artist,
      album: this.editForm.album,
      cover_url: this.editForm.cover_url
    })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (response) => {
          console.log('✅ Song metadata updated successfully:', response);

          // Actualizar en la lista local
          const index = this.favoritesList.findIndex(t => t._id === this.editingTrack!._id);
          if (index !== -1) {
            this.favoritesList[index] = {
              ...this.favoritesList[index],
              name: this.editForm.title,
              artist: this.editForm.artist,
              album: this.editForm.album,
              cover_url: this.editForm.cover_url
            };
          }

          this.cancelEdit();
        },
        error: (error) => {
          console.error('❌ Error updating song metadata:', error);
          this.error = 'Error al actualizar la información de la canción';
        }
      });
  }
  /**
   * Actualizar solo metadatos de la canción (sin archivo)
   */
  private updateSongMetadata(songId: number, metadata: any): Observable<any> {
    const API_URL = 'http://localhost:5000/api/music';
    return this.http.put(`${API_URL}/songs/${songId}/metadata`, metadata);
  }

  /**
   * Eliminar canción completamente
   */
  deleteSong(track: TrackModel, event: Event): void {
    event.stopPropagation();

    const confirmMessage = `¿Estás seguro de que quieres eliminar "${track.name}" permanentemente? Esta acción no se puede deshacer.`;

    if (confirm(confirmMessage)) {
      console.log('🗑️ Deleting song:', track.name);

      this.musicUploadService.deleteSong(Number(track._id))
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (response) => {
            console.log('✅ Song deleted successfully:', response);

            // Remover de favoritos primero
            this.favoritesService.removeFromFavorites(Number(track._id))
              .pipe(takeUntil(this.destroy$))
              .subscribe({
                next: () => {
                  // Remover de la lista local
                  this.favoritesList = this.favoritesList.filter(t => t._id !== track._id);
                  console.log('✅ Song removed from favorites and deleted');
                },
                error: (error) => {
                  console.error('❌ Error removing from favorites:', error);
                  // Aún así, remover de la lista local
                  this.favoritesList = this.favoritesList.filter(t => t._id !== track._id);
                }
              });
          },
          error: (error) => {
            console.error('❌ Error deleting song:', error);
            this.error = 'Error al eliminar la canción';
          }
        });
    }
  }

  /**
   * Cambiar ordenamiento
   */
  changeSort(property: string): void {
    const { order } = this.optionSort;
    this.optionSort = {
      property: property,
      order: order === 'asc' ? 'desc' : 'asc'
    };
    console.log('🔄 Sort changed:', this.optionSort);
  }

  /**
   * Reintentar carga
   */
  retryLoad(): void {
    console.log('🔄 Retry loading favorites');
    this.loadFavorites();
  }  /**
   * Formatear duración
   */
  formatDuration(seconds: any): string {
    if (!seconds || isNaN(seconds)) return '0:00';

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  /**
   * Formatear fecha
   */
  formatDate(dateString: any): string {
    if (!dateString) return 'Desconocida';

    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Fecha inválida';

      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return 'Fecha inválida';
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
