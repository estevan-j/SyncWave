import { Component, OnInit, OnDestroy, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TrackModel } from '@core/models/tracks.model';
import { MultimediaService } from '@core/services/multimedia.service';
import { Subject, takeUntil } from 'rxjs';

@Component({
  selector: 'app-media-player',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './media-player.component.html',
  styleUrl: './media-player.component.css'
})
export class MediaPlayerComponent implements OnInit, OnDestroy {

  currentTrack: TrackModel | null = null;
  isPlaying: boolean = false;
  currentTime: number = 0;
  duration: number = 0;
  progressPercentage: number = 0;
  volume: number = 50;
  isMuted: boolean = false;
  isLoading: boolean = false;
  hasError: boolean = false;

  private destroy$ = new Subject<void>();

  constructor(private multimediaService: MultimediaService) { }

  ngOnInit(): void {
    // Suscribirse a los cambios del reproductor
    this.multimediaService.currentTrack
      .pipe(takeUntil(this.destroy$))
      .subscribe(track => {
        console.log('🎵 Current track changed:', track?.name);
        this.currentTrack = track;
        this.hasError = false;
        this.isLoading = !!track; // Show loading when a new track is set
      });

    this.multimediaService.isPlaying
      .pipe(takeUntil(this.destroy$))
      .subscribe(playing => {
        this.isPlaying = playing;
      });

    this.multimediaService.currentTime
      .pipe(takeUntil(this.destroy$))
      .subscribe(time => {
        this.currentTime = time;
        this.updateProgress();
      });

    this.multimediaService.duration
      .pipe(takeUntil(this.destroy$))
      .subscribe(duration => {
        this.duration = duration;
        this.updateProgress();
      });

    this.multimediaService.isLoading
      .pipe(takeUntil(this.destroy$))
      .subscribe(loading => {
        this.isLoading = loading;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
  // Control de reproducción
  togglePlay(): void {
    this.multimediaService.togglePlay();
  }

  // Navegación entre canciones (implementar según necesidades)
  previousTrack(): void {
    console.log('⏮️ Previous track - TODO: implement');
    // TODO: Implementar lógica para canción anterior
  }

  nextTrack(): void {
    console.log('⏭️ Next track - TODO: implement');
    // TODO: Implementar lógica para siguiente canción
  }

  // Navegación temporal precisa
  skipForward(seconds: number = 10): void {
    const newTime = Math.min(this.currentTime + seconds, this.duration);
    this.multimediaService.seekTo(newTime);
  }

  skipBackward(seconds: number = 10): void {
    const newTime = Math.max(this.currentTime - seconds, 0);
    this.multimediaService.seekTo(newTime);
  }

  // Ir a tiempo específico
  goToTime(minutes: number, seconds: number = 0): void {
    const totalSeconds = (minutes * 60) + seconds;
    if (totalSeconds <= this.duration) {
      this.multimediaService.seekTo(totalSeconds);
    }
  }

  // Control de volumen
  setVolume(event: any): void {
    const volume = event.target.value;
    this.volume = volume;
    this.multimediaService.setVolume(volume);

    if (this.isMuted && volume > 0) {
      this.isMuted = false;
    }
  }

  toggleMute(): void {
    this.isMuted = !this.isMuted;
    this.multimediaService.setVolume(this.isMuted ? 0 : this.volume);
  }
  // Búsqueda en la canción
  seekTo(event: MouseEvent): void {
    if (this.duration <= 0) {
      console.warn('⚠️ Cannot seek: duration not loaded');
      return;
    }

    const progressBar = event.currentTarget as HTMLElement;
    const rect = progressBar.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, clickX / rect.width));
    const newTime = percentage * this.duration;

    console.log('🎯 Seeking to:', newTime, 'seconds (', percentage * 100, '%)');
    this.multimediaService.seekTo(newTime);
  }

  // Métodos auxiliares
  private updateProgress(): void {
    if (this.duration > 0) {
      this.progressPercentage = (this.currentTime / this.duration) * 100;
    }
  }

  formatTime(time: number): string {
    if (!time || isNaN(time)) return '00:00';

    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }

  // ✅ Método para manejar errores de imagen
  onImageError(event: Event): void {
    const target = event.target as HTMLImageElement;
    if (target) {
      target.src = 'https://i.pinimg.com/736x/69/d5/3e/69d53ef9520b57a5e2af1b1387807fc7.jpg';
    }
  }

  // 🎹 Atajos de teclado
  @HostListener('window:keydown', ['$event'])
  handleKeyboardShortcut(event: KeyboardEvent): void {
    // Solo actuar si no estamos escribiendo en un input
    if ((event.target as HTMLElement).tagName === 'INPUT') return;

    switch (event.code) {
      case 'Space':
        event.preventDefault();
        this.togglePlay();
        break;
      case 'ArrowLeft':
        event.preventDefault();
        this.skipBackward(5);
        break;
      case 'ArrowRight':
        event.preventDefault();
        this.skipForward(5);
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.adjustVolume(10);
        break;
      case 'ArrowDown':
        event.preventDefault();
        this.adjustVolume(-10);
        break;
      case 'KeyM':
        event.preventDefault();
        this.toggleMute();
        break;
    }
  }

  // Ajustar volumen con incrementos
  adjustVolume(increment: number): void {
    const newVolume = Math.max(0, Math.min(100, this.volume + increment));
    this.volume = newVolume;
    this.multimediaService.setVolume(newVolume);

    if (this.isMuted && newVolume > 0) {
      this.isMuted = false;
    }
  }

  // Getter para mostrar datos por defecto cuando no hay track
  get displayTrack(): TrackModel {
    return this.currentTrack || {
      cover_url: 'https://i.scdn.co/image/ab67616d0000b27345ca41b0d2352242c7c9d4bc',
      album: 'Selecciona una canción',
      name: 'No hay canción seleccionada',
      artist: 'Artista desconocido',
      _id: 0
    } as TrackModel;
  }
}