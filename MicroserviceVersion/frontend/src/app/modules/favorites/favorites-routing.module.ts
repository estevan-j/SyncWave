import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FavoritesPageComponent } from './pages/favorites-page/favorites-page.component';
import { LikedSongsPageComponent } from './pages/liked-songs-page/liked-songs-page.component';

const routes: Routes = [
  {
    path: '',
    component: FavoritesPageComponent, // Tu biblioteca (mantiene el comportamiento original)
  },
  {
    path: 'liked-songs',
    component: LikedSongsPageComponent, // Canciones que te gustan (nueva funcionalidad)
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class FavoritesRoutingModule { }
