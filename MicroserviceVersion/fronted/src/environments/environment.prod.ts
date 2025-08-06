export const environment = {
    production: true,
    apiUrl: 'https://your-production-api.com', // Tu URL de producción
    apiEndpoints: {
        auth: {
            login: '/api/users/login',
            signup: '/api/users/signup',
            logout: '/api/users/logout',
            verifyEmail: '/api/users/verify-email',
            resetPassword: '/api/users/reset-password'
        }
    }
};