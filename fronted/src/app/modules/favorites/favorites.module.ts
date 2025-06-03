import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FavoritesRoutingModule } from './favorites-routing.module';
import { SharedModule } from '@shared/shared.module';
import { FavoritesPageComponent } from './pages/favorites-page/favorites-page.component';


@NgModule({
  declarations: [], //Solo se declara cuando es stanalone
  imports: [
    CommonModule,
    FavoritesRoutingModule,
    SharedModule,
    RouterModule,
    FavoritesPageComponent
  ]
})
export class FavoritesModule { }
