import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SectionGenericComponent } from '@shared/components/section-generic/section-generic.component';
import { RouterModule, ActivatedRoute } from '@angular/router';
import { TrackModel } from '@core/models/tracks.model';
import { TracksService } from '@core/services/tracks.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-tracks-page',
  standalone: true,
  imports: [CommonModule, SectionGenericComponent, RouterModule],
  templateUrl: './tracks-page.component.html',
  styleUrl: './tracks-page.component.css'
})
export class TracksPageComponent implements OnInit, OnDestroy {

  mockTracksList: Array<TrackModel> = [];
  loading: boolean = false;
  error: string | null = null;
  searchTerm: string = '';
  isSearchMode: boolean = false;

  private destroy$ = new Subject<void>();

  constructor(
    private tracksService: TracksService,
    private route: ActivatedRoute
  ) {
    console.warn('🏗️ TracksPageComponent constructor called');
  } ngOnInit(): void {
    console.warn('🚀 TracksPageComponent ngOnInit - Starting initialization');
    this.checkForSearchParams();
    this.loadInitialTracks();

    // Suscribirse a actualizaciones de canciones
    this.tracksService.tracksRefresh$
      .pipe(takeUntil(this.destroy$))
      .subscribe(shouldRefresh => {
        if (shouldRefresh) {
          console.log('🔄 TracksPage: Tracks refresh triggered, reloading...');
          if (!this.isSearchMode) {
            this.loadTracks();
          }
        }
      });
  }
  ngOnDestroy(): void {
    console.log('🔥 TracksPageComponent destroyed');
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Verificar si hay parámetros de búsqueda en la URL
   */
  private checkForSearchParams(): void {
    this.route.queryParams
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        if (params['search']) {
          this.searchTerm = params['search'];
          this.isSearchMode = true;
          this.performSearch(this.searchTerm);
        } else {
          this.isSearchMode = false;
        }
      });
  }

  /**
   * Cargar tracks iniciales si no hay búsqueda
   */
  private loadInitialTracks(): void {
    if (!this.isSearchMode) {
      this.loadTracks();
    }
  }

  /**
   * Realizar búsqueda
   */
  private performSearch(searchTerm: string): void {
    console.log('🔍 Performing search for:', searchTerm);
    this.loading = true;
    this.error = null;

    this.tracksService.searchTracksOnServer({
      query: searchTerm
    })
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tracks) => {
          console.log(`✅ Search results for "${searchTerm}":`, tracks.length, 'tracks');
          this.mockTracksList = tracks;
          this.loading = false;

          if (tracks.length === 0) {
            this.error = `No se encontraron resultados para "${searchTerm}"`;
          }
        },
        error: (error) => {
          console.error('❌ Search error:', error);
          this.error = `Error al buscar "${searchTerm}": ${error.message || 'Error de conexión'}`;
          this.loading = false;
          this.mockTracksList = [];
        }
      });
  }

  private loadTracks(): void {
    console.warn('📡 loadTracks() called - Loading from API');
    this.loading = true;
    this.error = null;

    console.log('🔄 Calling tracksService.getAllTracks()');
    this.tracksService.getAllTracks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tracks) => {
          console.log('✅ Tracks received successfully from API:', tracks);
          console.log('📊 Number of tracks received:', tracks?.length || 0);

          this.mockTracksList = tracks || [];
          this.loading = false;

          if (!tracks || tracks.length === 0) {
            console.warn('⚠️ API returned empty tracks array');
            this.error = 'No se encontraron canciones en el servidor';
          } else {
            console.log('✅ Tracks loaded from API successfully');
          }
        },
        error: (error) => {
          console.error('❌ Error loading tracks from API:', error);
          console.error('🔍 Error details:', {
            message: error.message,
            status: error.status,
            statusText: error.statusText,
            url: error.url,
            name: error.name
          });

          this.error = `Error al cargar las canciones: ${error.message || 'Error de conexión con el servidor'}`;
          this.loading = false;
          this.mockTracksList = [];
        }
      });
  }
  retryLoad(): void {
    console.log('🔄 Retry button clicked');
    this.error = null;

    if (this.isSearchMode && this.searchTerm) {
      console.log('🔍 Retrying search for:', this.searchTerm);
      this.performSearch(this.searchTerm);
    } else {
      console.log('📡 Retrying normal track load');
      this.loadTracks();
    }
  }

  // Método para probar la conexión con el backend
  testBackendConnection(): void {
    console.log('🧪 Testing backend connection...');
    this.loading = true;
    this.error = null;

    this.tracksService.getAllTracks()
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (tracks) => {
          console.log('✅ Backend connection successful:', tracks);
          alert(`Backend conectado correctamente. Canciones encontradas: ${tracks?.length || 0}`);
          this.mockTracksList = tracks || [];
          this.loading = false;
        },
        error: (error) => {
          console.error('❌ Backend connection failed:', error);
          alert(`Error de conexión: ${error.message}`);
          this.error = 'Error de conexión con el backend';
          this.loading = false;
        }
      });
  }
}