import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TrackModel } from '@core/models/tracks.model';
import { MultimediaService } from '@core/services/multimedia.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-card-player',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './card-player.component.html',
  styleUrl: './card-player.component.css'
})
export class CardPlayerComponent implements OnInit, OnDestroy {
  @Input() mode: 'small' | 'big' = 'small';
  @Input() track!: TrackModel;

  isPlaying: boolean = false;
  currentTrack: TrackModel | null = null;

  private destroy$ = new Subject<void>();

  constructor(private multimediaService: MultimediaService) { }

  ngOnInit(): void {
    // Suscribirse al estado del reproductor
    this.multimediaService.currentTrack
      .pipe(takeUntil(this.destroy$))
      .subscribe(track => {
        this.currentTrack = track;
      });

    this.multimediaService.isPlaying
      .pipe(takeUntil(this.destroy$))
      .subscribe(playing => {
        // Solo actualizar si es la canción actual
        if (this.isCurrentTrack()) {
          this.isPlaying = playing;
        } else {
          this.isPlaying = false;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  isCurrentTrack(): boolean {
    return this.currentTrack?._id === this.track._id;
  }

  async togglePlay(): Promise<void> {
    try {
      if (this.isCurrentTrack() && this.isPlaying) {
        // Si es la canción actual y está sonando, pausar
        this.multimediaService.pause();
      } else {
        // Si no es la canción actual o está pausada, reproducir
        console.log('🎵 Playing track from card:', this.track.name);

        this.multimediaService.setTrack(this.track);
        await this.multimediaService.play();
      }
    } catch (error) {
      console.error('❌ Failed to toggle play:', error);
    }
  }

  // ✅ Método para manejar errores de imagen
  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    if (target) {
      target.src = 'https://i.pinimg.com/736x/69/d5/3e/69d53ef9520b57a5e2af1b1387807fc7.jpg';
    }
  }
}