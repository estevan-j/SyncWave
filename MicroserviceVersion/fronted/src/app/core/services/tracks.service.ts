import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';
import { TrackModel } from '@core/models/tracks.model';
import { AuthService } from '@core/services/auth.service';
import { environment } from '../../../environments/environment';

@Injectable({
    providedIn: 'root'
})
export class TracksService {
    private readonly API_URL = `${environment.musicsApiUrl}/api/musics`;

    private tracksRefreshSubject = new BehaviorSubject<boolean>(false);
    public tracksRefresh$ = this.tracksRefreshSubject.asObservable();

    constructor(private http: HttpClient, private authService: AuthService) { }

    private getAuthHeaders(): HttpHeaders {
        const token = this.authService.getToken();
        return new HttpHeaders({
            'Authorization': `Bearer ${token}`
        });
    }

    getAllTracks(): Observable<TrackModel[]> {
        const headers = this.getAuthHeaders();
        return this.http.get<any>(`${this.API_URL}`, { headers }).pipe(
            map(response => {
                let songs: any[] = [];
                if (response && response.data && Array.isArray(response.data)) {
                    songs = response.data;
                } else if (response && response.songs && Array.isArray(response.songs)) {
                    songs = response.songs;
                } else if (Array.isArray(response)) {
                    songs = response;
                } else {
                    return [];
                }
                return songs.map((song: any) => ({
                    _id: song.id || song._id || Math.random(),
                    name: song.title || song.name || 'Título desconocido',
                    artist: song.artist || 'Artista desconocido',
                    album: song.album || 'Album desconocido',
                    cover_url: song.cover_url || song.image_url || song.cover || 'assets/img/default-cover.png',
                    url: song.file_path || song.url || '',
                    duration: song.duration || 0,
                    created_at: song.created_at || new Date().toISOString(),
                    explicit: song.explicit || false
                }));
            })
        );
    }

    getTrackById(id: string): Observable<TrackModel> {
        const headers = this.getAuthHeaders();
        return this.http.get<TrackModel>(`${this.API_URL}/tracks/${id}`, { headers });
    }

    searchTracks(query: string): Observable<TrackModel[]> {
        const headers = this.getAuthHeaders();
        return this.http.get<TrackModel[]>(`${this.API_URL}/search?q=${query}`, { headers });
    }

    searchTracksOnServer(searchParams: { query?: string; title?: string; artist?: string; }): Observable<TrackModel[]> {
        let params = new URLSearchParams();
        if (searchParams.query && searchParams.query.trim().length >= 2) params.append('q', searchParams.query.trim());
        if (searchParams.title && searchParams.title.trim().length >= 2) params.append('title', searchParams.title.trim());
        if (searchParams.artist && searchParams.artist.trim().length >= 2) params.append('artist', searchParams.artist.trim());
        if (params.toString() === '') {
            return new Observable(observer => { observer.next([]); observer.complete(); });
        }
        const searchUrl = `${this.API_URL}/search?${params.toString()}`;
        const headers = this.getAuthHeaders();
        return this.http.get<any>(searchUrl, { headers }).pipe(
            map(response => {
                let songs: any[] = [];
                if (response && response.data && Array.isArray(response.data)) {
                    songs = response.data;
                } else if (Array.isArray(response)) {
                    songs = response;
                } else {
                    return [];
                }
                return songs.map((song: any) => ({
                    _id: song.id || song._id || Math.random(),
                    name: song.title || song.name || 'Título desconocido',
                    artist: song.artist || 'Artista desconocido',
                    album: song.album || 'Album desconocido',
                    cover_url: song.cover_url || song.image_url || song.cover || 'assets/img/default-cover.png',
                    url: song.file_path || song.url || '',
                    duration: song.duration || 0,
                    created_at: song.created_at || new Date().toISOString(),
                    explicit: song.explicit || false
                }));
            })
        );
    }

    refreshTracks(): void {
        this.tracksRefreshSubject.next(true);
    }
}