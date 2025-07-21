-- Script SQL para insertar datos de prueba en la base de datos MusicApp
-- Este archivo se ejecuta después del script de inicialización

-- Insertar solo usuario admin (sin username, con password)
INSERT INTO users (email, password) VALUES 
    ('admin@musicapp.com', 'admin123')
ON CONFLICT (email) DO NOTHING;

-- Insertar canciones basadas en tu JSON (con rutas corregidas a Flask backend)
INSERT INTO songs (title, artist, album, duration, file_path, cover_url, artist_name, artist_nickname, nationality) VALUES 
    ('Getting Over', 'David Guetta', 'One Love', 333, 'http://localhost:5000/assets/1_GettingOver_DavidGuetta.mp3', 
     'https://jenesaispop.com/wp-content/uploads/2009/09/guetta_onelove.jpg', 
     'David Guetta', 'David Guetta', 'FR'),
    
    ('Snow Tha Product || BZRP Music Sessions #39', 'Snow', 'BZRP Music Sessions', 333, 'http://localhost:5000/assets/2_SnowThaProduct_Snow.mp3',
     'https://is5-ssl.mzstatic.com/image/thumb/Features125/v4/9c/b9/d0/9cb9d017-fcf6-28c6-81d0-e9ac5b0f359e/pr_source.png/800x800cc.jpg',
     'Snow', 'Snow', 'US'),
    
    ('Calypso (Original Mix)', 'Round Table Knights', 'Round Table Knights', 333, 'http://localhost:5000/assets/3_Calypso_RoundTableKnights.mp3',
     'https://cdns-images.dzcdn.net/images/cover/1db3f8f185e68f26feaf0b9d72ff1645/350x350.jpg',
     'Round Table Knights', 'Round Table Knights', 'US'),
    
    ('Bad Habits', 'Ed Sheeran', 'Ed Sheeran', 333, 'http://localhost:5000/assets/4_BadHabits_EdSheeran.mp3',
     'https://www.lahiguera.net/musicalia/artistas/ed_sheeran/disco/11372/tema/25301/ed_sheeran_bad_habits-portada.jpg',
     'Ed Sheeran', 'Ed Sheeran', 'UK'),
    
    ('BEBE (Official Video)', 'Giolì & Assia', 'Giolì & Assia', 333, 'http://localhost:5000/assets/5_BEBE_Gioli&Assia.mp3',
     'https://i.scdn.co/image/ab67616d0000b27345ca41b0d2352242c7c9d4bc',
     'Giolì & Assia', 'Giolì & Assia', 'IT'),
    
    ('T.N.T. (Live At River Plate, December 2009)', 'AC/DC', 'AC/DC', 333, 'http://localhost:5000/assets/6_TNT_ACDC.mp3',
     'https://cdns-images.dzcdn.net/images/cover/ba5eaf2f3a49768164d0728b7ba64372/500x500.jpg',
     'AC/DC', 'AC/DC', 'US'),
    
    ('50 Cent - Candy Shop (feat. Olivia)', '50 Cent', '50 Cent', 333, 'http://localhost:5000/assets/7_CandyShop_50Cent.mp3',
     'https://i.scdn.co/image/ab67616d0000b27391f7222996c531b981e7bb3d',
     '50 Cent', '50 Cent', 'US'),
    
    ('Bésame💋', 'Valentino', 'Valentino Ft MTZ Manuel Turizo (Video Oficial)', 333, 'http://localhost:5000/assets/8_Besame_Valentino.mp3',
     'https://i1.sndcdn.com/artworks-000247627460-1hqnjr-t500x500.jpg',
     'Valentino', 'Valentino', 'CO')
ON CONFLICT DO NOTHING;

-- Insertar algunas canciones favoritas para el admin
INSERT INTO favorite_songs (user_id, song_id) VALUES 
    (1, 1), -- Getting Over
    (1, 4), -- Bad Habits
    (1, 6), -- T.N.T.
    (1, 7); -- Candy Shop

-- Insertar algunos mensajes de chat de prueba
INSERT INTO chat_messages (user_id, message, room) VALUES 
    (1, '¡Bienvenidos al chat de MusicApp! 🎵', 'general'),
    (1, 'He agregado algunas canciones increíbles', 'general'),
    (1, 'David Guetta siempre es una buena opción 🔥', 'electronic'),
    (1, '¿Cuál es su canción favorita?', 'general'),
    (1, 'El catálogo está listo para disfrutar', 'general');

