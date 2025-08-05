import { Component, OnInit, OnDestroy, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FavoritesListBodyComponent } from '@shared/components/favorites-list-body/favorites-list-body.component';
import { FavoritesService } from '@core/services/favorites.service';
import { MultimediaService } from '@core/services/multimedia.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-liked-songs-page',
  standalone: true,
  imports: [CommonModule, RouterModule, FavoritesListBodyComponent],
  templateUrl: './liked-songs-page.component.html',
  styleUrl: './liked-songs-page.component.css'
})
export class LikedSongsPageComponent implements OnInit, OnDestroy {
  @ViewChild(FavoritesListBodyComponent) favoritesListComponent!: FavoritesListBodyComponent;

  favoritesCount = 0;
  private destroy$ = new Subject<void>();

  constructor(
    private favoritesService: FavoritesService,
    private multimediaService: MultimediaService
  ) { }

  ngOnInit(): void {
    console.log('🎵 Liked Songs Page initialized');
    this.loadFavoritesCount();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Cargar contador de favoritos
   */
  private loadFavoritesCount(): void {
    this.favoritesService.getUserFavorites()
      .pipe(takeUntil(this.destroy$))
      .subscribe(favorites => {
        this.favoritesCount = favorites.length;
        console.log('🔢 Favorites count updated:', this.favoritesCount);
      });
  }

  /**
   * Reproducir todas las canciones favoritas
   */
  playAll(): void {
    if (this.favoritesListComponent && this.favoritesListComponent.favoritesList.length > 0) {
      const firstTrack = this.favoritesListComponent.favoritesList[0];
      console.log('▶️ Playing all favorites, starting with:', firstTrack.name);
      this.multimediaService.setTrack(firstTrack);
    }
  }

  /**
   * Reproducir favoritos en modo aleatorio
   */
  playShuffled(): void {
    if (this.favoritesListComponent && this.favoritesListComponent.favoritesList.length > 0) {
      const tracks = [...this.favoritesListComponent.favoritesList];
      const randomIndex = Math.floor(Math.random() * tracks.length);
      const randomTrack = tracks[randomIndex];
      console.log('🔀 Playing favorites shuffled, starting with:', randomTrack.name);
      this.multimediaService.setTrack(randomTrack);
    }
  }
}
