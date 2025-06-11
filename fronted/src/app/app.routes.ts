import { Routes } from '@angular/router';
import { NgModule } from '@angular/core';
import { RouterModule } from '@angular/router';


export const routes: Routes = [
    {
        path: '', // Redirigir a login cuando se accede a localhost:4200
        redirectTo: '/auth/login',
        pathMatch: 'full'
    },
    {
        path: 'auth', // Rutas de autenticación
        loadChildren: () => import(`./modules/auth/auth.module`).then(m => m.AuthModule)
    }, {
        path: 'home', // Ruta para la página principal con reproductor
        loadChildren: () => import(`./modules/home/home.module`).then(m => m.HomeModule)
    }
];

/*
export const routes: Routes = [
    {
        path: 'auth', //Cuando ponemos una ruta hacemos referencia a localhost:4200/auth
        loadChildren: ()=>import(`./modules/auth/auth.module`).then(m=>m.AuthModule)
    },
    
   {
        path: 'home', // Ruta explícita para la sección principal/home
        loadChildren: () => import(`./modules/home/home.module`).then(m => m.HomeModule)
   },
   {
        path: '', // Cuando se accede a localhost:4200 (raíz)
        redirectTo: 'home', // Redirige a /home
        pathMatch: 'full' // Importante para que la redirección funcione correctamente con rutas vacías
    },
];

*/

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutes { }