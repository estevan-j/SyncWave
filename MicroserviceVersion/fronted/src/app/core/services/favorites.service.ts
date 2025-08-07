import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map, tap } from 'rxjs/operators';

export interface FavoriteResponse {
    success: boolean;
    message: string;
    data?: any;
}

@Injectable({
    providedIn: 'root'
})
export class FavoritesService {
    private readonly API_URL = 'http://localhost:5000/api/favorites';

    // Simulamos un user_id por ahora - en una app real vendría del servicio de autenticación
    private readonly USER_ID = 1;

    // Cache de favoritos del usuario
    private userFavorites$ = new BehaviorSubject<number[]>([]);

    constructor(private http: HttpClient) {
        this.loadUserFavorites();
    }

    /**
     * Obtener favoritos del usuario actual
     */
    getUserFavorites(): Observable<number[]> {
        return this.userFavorites$.asObservable();
    }

    /**
     * Cargar favoritos del usuario desde el backend
     */
    private loadUserFavorites(): void {
        this.http.get<any>(`${this.API_URL}/user/${this.USER_ID}`).pipe(
            map(response => {
                console.log('🔥 Favorites API response:', response);

                // Extraer los IDs de las canciones favoritas
                if (response && response.data && Array.isArray(response.data)) {
                    return response.data.map((favorite: any) => favorite.song_id);
                } else if (response && Array.isArray(response)) {
                    return response.map((favorite: any) => favorite.song_id);
                }
                return [];
            })
        ).subscribe({
            next: (favoriteIds) => {
                console.log('🔥 Loaded user favorites:', favoriteIds);
                this.userFavorites$.next(favoriteIds);
            },
            error: (error) => {
                console.error('❌ Error loading favorites:', error);
                this.userFavorites$.next([]);
            }
        });
    }

    /**
     * Verificar si una canción es favorita
     */
    isFavorite(songId: number): Observable<boolean> {
        return this.userFavorites$.pipe(
            map(favorites => favorites.includes(songId))
        );
    }

    /**
     * Agregar una canción a favoritos
     */
    addToFavorites(songId: number): Observable<FavoriteResponse> {
        console.log('➕ Adding song to favorites:', songId, 'for user:', this.USER_ID);

        return this.http.post<FavoriteResponse>(`${this.API_URL}/user/${this.USER_ID}/song/${songId}`, {}).pipe(
            tap(response => {
                if (response.success) {
                    const currentFavorites = this.userFavorites$.value;
                    if (!currentFavorites.includes(songId)) {
                        this.userFavorites$.next([...currentFavorites, songId]);
                        console.log('✅ Added to favorites locally');
                    }
                }
            })
        );
    }

    /**
     * Remover una canción de favoritos
     */
    removeFromFavorites(songId: number): Observable<FavoriteResponse> {
        console.log('➖ Removing song from favorites:', songId, 'for user:', this.USER_ID);

        return this.http.delete<FavoriteResponse>(`${this.API_URL}/user/${this.USER_ID}/song/${songId}`).pipe(
            tap(response => {
                if (response.success) {
                    const currentFavorites = this.userFavorites$.value;
                    this.userFavorites$.next(currentFavorites.filter(id => id !== songId));
                    console.log('✅ Removed from favorites locally');
                }
            })
        );
    }    /**
     * Toggle favorite status (agregar/remover)
     */
    toggleFavorite(songId: number): Observable<boolean> {
        const currentFavorites = this.userFavorites$.value;
        const isFavorite = currentFavorites.includes(songId);

        if (isFavorite) {
            return this.removeFromFavorites(songId).pipe(
                map(response => false) // Devolver false cuando se remueve
            );
        } else {
            return this.addToFavorites(songId).pipe(
                map(response => true) // Devolver true cuando se agrega
            );
        }
    }

    /**
     * Verificar en el servidor si una canción es favorita
     */
    checkFavoriteStatus(songId: number): Observable<boolean> {
        return this.http.get<any>(`${this.API_URL}/user/${this.USER_ID}/song/${songId}/check`).pipe(
            map(response => response && response.data && response.data.is_favorite === true)
        );
    }
}
