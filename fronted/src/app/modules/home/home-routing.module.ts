import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './page/home-page/home-page.component';
import { TracksModule } from '@modules/tracks/tracks.module';


const routes: Routes = [
  {
    path: 'tracks',
    loadChildren:()=> import('@modules/tracks/tracks.module').then(m=>m.TracksModule)
  },
  {
    path: 'favorites',
    loadChildren:()=> import('@modules/favorites/favorites.module').then(m=>m.FavoritesModule)
  },
  {
    path: 'history',
    loadChildren:()=> import('@modules/history/history.module').then(m=>m.HistoryModule)
  }
  
];


/*
const routes: Routes = [ // Renombrado para mayor claridad
  {
    path: '', // Esta es la ruta base DENTRO de HomeModule.
              // Como HomeModule se carga en '/home', este '' corresponde a 'localhost:4200/home'.
    component: HomePageComponent,
    children: [ // Estas rutas se renderizarán dentro del <router-outlet> de HomePageComponent
      {
        path: 'tracks', // Accedido como localhost:4200/home/tracks
        loadChildren:()=> import('@modules/tracks/tracks.module').then(m=>m.TracksModule)
      },
      {
        path: 'favorites', // Accedido como localhost:4200/home/favorites
        loadChildren:()=> import('@modules/favorites/favorites.module').then(m=>m.FavoritesModule)
      },
      {
        path: 'history', // Accedido como localhost:4200/home/history
        loadChildren:()=> import('@modules/history/history.module').then(m=>m.HistoryModule)
      },
      {
        // Ruta por defecto para '/home'. Si el usuario navega a '/home',
        // puedes redirigirlo a una sub-sección por defecto, por ejemplo 'tracks'.
        path: '',
        redirectTo: 'tracks',
        pathMatch: 'full'
      }
    ]
  }
];
*/

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class HomeRoutingModule { }
