import { Component, ElementRef, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, NavigationEnd } from '@angular/router';
import { TracksService } from '@core/services/tracks.service';
import { TrackModel } from '@core/models/tracks.model';
import { MultimediaService } from '@core/services/multimedia.service';
import { debounceTime, distinctUntilChanged, switchMap, filter } from 'rxjs/operators';
import { Subject, Subscription, fromEvent } from 'rxjs';

@Component({
  selector: 'app-header-user',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './header-user.component.html',
  styleUrl: './header-user.component.css'
})
export class HeaderUserComponent implements OnInit, OnDestroy {
  @ViewChild('searchInput') searchInput!: ElementRef;

  // Propiedades para búsqueda
  searchResults: TrackModel[] = [];
  isSearching = false;
  showSearchResults = false;
  private searchTerms = new Subject<string>();
  private subscriptions: Subscription[] = [];

  constructor(
    private router: Router,
    private tracksService: TracksService,
    private multimediaService: MultimediaService
  ) { } ngOnInit(): void {
    this.setupSearch();
    this.setupRouterListener();
    this.setupGlobalClickListener();
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach(sub => sub.unsubscribe());
    this.searchTerms.complete();
  }  /**
   * Escuchar cambios de ruta para ocultar resultados de búsqueda
   */
  private setupRouterListener(): void {
    const routerSub = this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        console.log('🌐 Route changed, hiding search results');
        this.showSearchResults = false;
        this.searchResults = [];
        this.isSearching = false;
        // También limpiar el input si es necesario
        if (this.searchInput) {
          this.searchInput.nativeElement.blur();
        }
      });
    this.subscriptions.push(routerSub);
  }

  /**
   * Configurar la búsqueda con debounce para optimizar las llamadas al servidor
   */
  private setupSearch(): void {
    const searchSub = this.searchTerms.pipe(
      debounceTime(300), // Esperar 300ms después de que el usuario pare de escribir
      distinctUntilChanged(), // Solo buscar si el término cambió
      switchMap((term: string) => {
        if (term.trim().length < 2) {
          this.showSearchResults = false;
          return [];
        }

        this.isSearching = true;
        return this.tracksService.searchTracksOnServer({ query: term });
      })
    ).subscribe({
      next: (results) => {
        this.searchResults = results;
        this.showSearchResults = results.length > 0;
        this.isSearching = false;
        console.log('🔍 Search completed. Results:', results.length);
      },
      error: (error) => {
        console.error('❌ Search error:', error);
        this.searchResults = [];
        this.showSearchResults = false;
        this.isSearching = false;
      }
    });

    this.subscriptions.push(searchSub);
  }

  /**
   * Manejar cambios en el input de búsqueda
   */
  onSearchChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    const searchTerm = target.value;
    console.log('🔍 Search term changed:', searchTerm);
    this.searchTerms.next(searchTerm);
  }
  /**
   * Reproducir una canción desde los resultados de búsqueda
   */
  playTrack(track: TrackModel): void {
    console.log('▶️ Playing track from search:', track.name);
    this.multimediaService.setTrack(track);
    this.hideSearchResultsImmediate();
  }
  /**
   * Ocultar resultados de búsqueda
   */
  hideSearchResults(): void {
    setTimeout(() => {
      this.showSearchResults = false;
    }, 200); // Pequeño delay para permitir clicks en resultados
  }

  /**
   * Ocultar resultados de búsqueda inmediatamente
   */
  hideSearchResultsImmediate(): void {
    this.showSearchResults = false;
    this.searchResults = [];
    this.isSearching = false;
  }

  /**
   * Mostrar resultados si hay alguno
   */
  showResults(): void {
    if (this.searchResults.length > 0) {
      this.showSearchResults = true;
    }
  }
  /**
   * Navegar a la página de búsqueda completa
   */
  goToSearch(): void {
    const searchTerm = this.searchInput.nativeElement.value;
    if (searchTerm.trim()) {
      this.router.navigate(['/tracks'], {
        queryParams: { search: searchTerm.trim() }
      });
      this.hideSearchResultsImmediate();
    }
  }
  /**
   * Manejar teclas especiales en el input de búsqueda
   */
  onSearchKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.goToSearch();
    } else if (event.key === 'Escape') {
      this.hideSearchResultsImmediate();
      this.searchInput.nativeElement.blur();
    }
  }
  /**
   * Limpiar búsqueda
   */
  clearSearch(): void {
    this.searchInput.nativeElement.value = '';
    this.searchResults = [];
    this.showSearchResults = false;
    this.isSearching = false;
  }

  /**
   * Configurar listener global para cerrar dropdown al hacer click fuera
   */
  private setupGlobalClickListener(): void {
    const globalClickSub = fromEvent(document, 'click').subscribe((event: Event) => {
      const target = event.target as HTMLElement;
      const searchContainer = target.closest('.search-container');

      if (!searchContainer && this.showSearchResults) {
        console.log('🌐 Click outside search, hiding results');
        this.hideSearchResultsImmediate();
      }
    });

    this.subscriptions.push(globalClickSub);
  }

  /**
   * Helper para manejar errores de imagen
   */
  onImageError(event: Event): void {
    const img = event.target as HTMLImageElement;
    img.src = 'assets/img/default-cover.png';
  }
}
