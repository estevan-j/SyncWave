export const environment = {
    production: true,
    apiUrl: 'http://localhost:8090', // URL del API Gateway en producción (ajusta si usas Nginx o dominio público)
    apiEndpoints: {
        auth: {
            login: '/api/auth/login',
            signup: '/api/auth/signup',
            logout: '/api/auth/logout',
            verifyEmail: '/api/auth/verify-email',
            resetPassword: '/api/auth/reset-password'
        },
        musics: {
            getAll: '/api/musics/',
            getById: '/api/musics/', // se concatena el id
            create: '/api/musics/',
            update: '/api/musics/', // se concatena el id
            delete: '/api/musics/', // se concatena el id
            upload: '/api/musics/upload'
        }
    }
};