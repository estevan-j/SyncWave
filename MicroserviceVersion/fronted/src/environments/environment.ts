export const environment = {
    production: false,
    apiUrl: 'http://localhost:5000', // URL de desarrollo para users/auth
    musicsApiUrl: 'http://localhost:5001', // URL específica para el microservicio de musics
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