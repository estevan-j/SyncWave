import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';
import { TrackModel } from '@core/models/tracks.model';

@Injectable({
    providedIn: 'root'
})
export class TracksService {
    private readonly API_URL = 'http://localhost:5000/api/music';

    // Subject para notificar cuando las canciones necesitan actualizarse
    private tracksRefreshSubject = new BehaviorSubject<boolean>(false);
    public tracksRefresh$ = this.tracksRefreshSubject.asObservable();

    constructor(private http: HttpClient) { }

    getAllTracks(): Observable<TrackModel[]> {
        console.log('Calling API:', `${this.API_URL}/songs`);
        return this.http.get<any>(`${this.API_URL}/songs`).pipe(
            map(response => {
                console.log('Raw API response:', response);

                let songs: any[] = [];

                // Si el backend devuelve { data: [...] }
                if (response && response.data && Array.isArray(response.data)) {
                    console.log('Extracting data array:', response.data);
                    songs = response.data;
                }
                // Si el backend devuelve { songs: [...] }
                else if (response && response.songs && Array.isArray(response.songs)) {
                    console.log('Extracting songs array:', response.songs);
                    songs = response.songs;
                }
                // Si el backend devuelve directamente un array
                else if (Array.isArray(response)) {
                    console.log('Response is already an array:', response);
                    songs = response;
                }
                else {
                    console.warn('API response is not an array, returning empty array:', response);
                    return [];
                }

                // Transformar los datos del backend al formato esperado por el frontend
                const transformedTracks: TrackModel[] = songs.map((song: any) => {
                    console.log('🔄 Processing song:', song.title, 'with file_path:', song.file_path);

                    const track = {
                        _id: song.id || song._id || Math.random(), // Usar id del backend o generar uno
                        name: song.title || song.name || 'Título desconocido', // title -> name
                        artist: song.artist || 'Artista desconocido',
                        album: song.album || 'Album desconocido',
                        cover_url: song.cover_url || song.image_url || song.cover || 'assets/img/default-cover.png',
                        url: song.file_path || song.url || '', // Use file_path directly as it's already a complete URL
                        duration: song.duration || 0,
                        created_at: song.created_at || new Date().toISOString(),
                        explicit: song.explicit || false
                    };

                    console.log('✅ Transformed track:', track.name, 'with URL:', track.url);
                    return track;
                });

                console.log('Transformed tracks:', transformedTracks);
                return transformedTracks;
            })
        );
    }

    getTrackById(id: string): Observable<TrackModel> {
        return this.http.get<TrackModel>(`${this.API_URL}/tracks/${id}`);
    }

    searchTracks(query: string): Observable<TrackModel[]> {
        return this.http.get<TrackModel[]>(`${this.API_URL}/search?q=${query}`);
    }

    /**
     * Buscar canciones en el servidor usando diferentes criterios
     * Utiliza el endpoint del backend /songs/search
     */
    searchTracksOnServer(searchParams: {
        query?: string;
        title?: string;
        artist?: string;
    }): Observable<TrackModel[]> {
        console.log('🔍 Searching tracks on server with params:', searchParams);

        // Construir parámetros de consulta
        let params = new URLSearchParams();

        if (searchParams.query && searchParams.query.trim().length >= 2) {
            params.append('q', searchParams.query.trim());
        }

        if (searchParams.title && searchParams.title.trim().length >= 2) {
            params.append('title', searchParams.title.trim());
        }

        if (searchParams.artist && searchParams.artist.trim().length >= 2) {
            params.append('artist', searchParams.artist.trim());
        }

        // Validar que al menos un parámetro esté presente
        if (params.toString() === '') {
            console.warn('⚠️ No valid search parameters provided');
            return new Observable(observer => {
                observer.next([]);
                observer.complete();
            });
        }

        const searchUrl = `${this.API_URL}/songs/search?${params.toString()}`;
        console.log('🌐 Search URL:', searchUrl);

        return this.http.get<any>(searchUrl).pipe(
            map(response => {
                console.log('🔍 Search API response:', response);

                let songs: any[] = [];

                // Procesar respuesta similar a getAllTracks
                if (response && response.data && Array.isArray(response.data)) {
                    songs = response.data;
                } else if (Array.isArray(response)) {
                    songs = response;
                } else {
                    console.warn('Search API response is not an array:', response);
                    return [];
                }

                // Transformar datos igual que en getAllTracks
                const transformedTracks: TrackModel[] = songs.map((song: any) => {
                    console.log('🔄 Processing search result:', song.title);

                    return {
                        _id: song.id || song._id || Math.random(),
                        name: song.title || song.name || 'Título desconocido',
                        artist: song.artist || 'Artista desconocido',
                        album: song.album || 'Album desconocido',
                        cover_url: song.cover_url || song.image_url || song.cover || 'assets/img/default-cover.png',
                        url: song.file_path || song.url || '',
                        duration: song.duration || 0,
                        created_at: song.created_at || new Date().toISOString(),
                        explicit: song.explicit || false
                    };
                }); console.log('✅ Search results transformed:', transformedTracks.length, 'tracks');
                return transformedTracks;
            })
        );
    }

    /**
     * Notificar que las canciones necesitan actualizarse
     * Útil después de subir, editar o eliminar canciones
     */
    refreshTracks(): void {
        console.log('🔄 TracksService: Triggering tracks refresh');
        this.tracksRefreshSubject.next(true);
    }
}