import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { TrackModel } from '@core/models/tracks.model';

@Injectable({
    providedIn: 'root'
})
export class MultimediaService {

    private currentTrack$ = new BehaviorSubject<TrackModel | null>(null);
    private isPlaying$ = new BehaviorSubject<boolean>(false);
    private currentTime$ = new BehaviorSubject<number>(0);
    private duration$ = new BehaviorSubject<number>(0);
    private isLoading$ = new BehaviorSubject<boolean>(false);

    public audio: HTMLAudioElement = new Audio(); constructor() {
        this.audio.crossOrigin = 'anonymous'; // Enable cross-origin loading
        this.audio.preload = 'metadata'; // Preload metadata only
        this.listenAudioEvents();
    }

    get currentTrack(): Observable<TrackModel | null> {
        return this.currentTrack$.asObservable();
    }

    get isPlaying(): Observable<boolean> {
        return this.isPlaying$.asObservable();
    }

    get currentTime(): Observable<number> {
        return this.currentTime$.asObservable();
    }

    get duration(): Observable<number> {
        return this.duration$.asObservable();
    }

    get isLoading(): Observable<boolean> {
        return this.isLoading$.asObservable();
    }

    setTrack(track: TrackModel): void {
        console.log('🎵 Setting new track:', track.name);
        console.log('🎵 Track object:', track);

        // ✅ Usar file_path en lugar de url
        const audioUrl = track.url;
        console.log('🔗 Audio URL:', audioUrl);

        if (!audioUrl) {
            console.error('❌ No audio URL found in track:', track);
            return;
        }

        // Verify URL format
        if (!audioUrl.startsWith('http://') && !audioUrl.startsWith('https://')) {
            console.error('❌ Invalid URL format:', audioUrl);
            return;
        }

        this.currentTrack$.next(track);
        console.log('📡 Setting audio src to:', audioUrl);
        this.isLoading$.next(true);
        this.audio.src = audioUrl;
        this.audio.load();
        console.log('🔄 Audio load() called');
    }

    async play(): Promise<void> {
        try {
            await this.audio.play();
            this.isPlaying$.next(true);
            console.log('✅ Audio playing successfully');
        } catch (error: any) {
            console.error('❌ Play failed:', error);
            this.isPlaying$.next(false);

            if (error.name !== 'AbortError') {
                throw error;
            }
        }
    }

    pause(): void {
        this.audio.pause();
        this.isPlaying$.next(false);
    } togglePlay(): void {
        if (!this.audio.src) {
            console.warn('⚠️ No audio source set, cannot toggle play');
            return;
        }

        if (this.isPlaying$.value) {
            console.log('⏸️ Pausing audio');
            this.pause();
        } else {
            console.log('▶️ Playing audio');
            this.play().catch(error => {
                console.error('❌ Toggle play failed:', error);
            });
        }
    } seekTo(time: number): void {
        if (this.audio && !isNaN(time) && time >= 0 && time <= this.audio.duration) {
            console.log('🎯 Seeking to time:', time, 'seconds');
            this.audio.currentTime = time;
        } else {
            console.warn('⚠️ Invalid seek time:', time, 'duration:', this.audio?.duration);
        }
    }

    setVolume(volume: number): void {
        const normalizedVolume = Math.max(0, Math.min(1, volume / 100));
        console.log('🔊 Setting volume to:', normalizedVolume);
        this.audio.volume = normalizedVolume;
    }

    // 🧪 Test method to validate audio URL accessibility
    async testAudioUrl(url: string): Promise<boolean> {
        try {
            console.log('🧪 Testing audio URL:', url);
            const testAudio = new Audio();
            testAudio.crossOrigin = 'anonymous';

            return new Promise((resolve) => {
                testAudio.addEventListener('canplay', () => {
                    console.log('✅ Test audio can play');
                    resolve(true);
                });

                testAudio.addEventListener('error', (e) => {
                    console.error('❌ Test audio error:', e);
                    console.error('❌ Test audio error details:', testAudio.error);
                    resolve(false);
                });

                testAudio.src = url;
                testAudio.load();
            });
        } catch (error) {
            console.error('❌ Test audio exception:', error);
            return false;
        }
    }

    private listenAudioEvents(): void {
        this.audio.addEventListener('loadedmetadata', () => {
            console.log('📊 Audio metadata loaded, duration:', this.audio.duration);
            this.duration$.next(this.audio.duration || 0);
            this.isLoading$.next(false);
        });

        this.audio.addEventListener('timeupdate', () => {
            this.currentTime$.next(this.audio.currentTime);
        });

        this.audio.addEventListener('ended', () => {
            console.log('🔚 Audio ended');
            this.isPlaying$.next(false);
        }); this.audio.addEventListener('error', (e) => {
            console.error('❌ Audio error during playback:', e);
            console.error('❌ Error details:', this.audio.error);
            console.error('❌ Audio source:', this.audio.src);
            console.error('❌ Audio network state:', this.audio.networkState);
            console.error('❌ Audio ready state:', this.audio.readyState);
            this.isPlaying$.next(false);
            this.isLoading$.next(false);
        }); this.audio.addEventListener('canplay', () => {
            console.log('✅ Audio can play');
            this.isLoading$.next(false);
        });

        this.audio.addEventListener('loadstart', () => {
            console.log('📥 Audio load started');
        });

        this.audio.addEventListener('loadeddata', () => {
            console.log('📊 Audio data loaded');
        });

        this.audio.addEventListener('abort', () => {
            console.log('🚫 Audio load aborted');
        });

        this.audio.addEventListener('stalled', () => {
            console.log('⏳ Audio load stalled');
        });
    }
}