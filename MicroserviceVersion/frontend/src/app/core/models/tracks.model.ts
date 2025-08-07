import { ArtistModel } from "./artist.model";

export interface TrackModel {
    _id: number;
    name: string;
    album: string;
    artist: string;
    cover_url: string;
    url: string; // URL del archivo MP3
    duration?: number; // ✅ Agregar duración
    created_at?: string; // ✅ Agregar fecha de creación
    explicit?: boolean;
}