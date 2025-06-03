import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { HomeRoutingModule } from './home-routing.module';
import { SharedModule } from '@shared/shared.module';
import { HomePageComponent } from './page/home-page/home-page.component';


@NgModule({
  declarations: [
    //Si es standalone=true no se declara en esta seccion
  ],
  imports: [
    CommonModule,
    HomeRoutingModule,
    SharedModule,
    RouterModule,
    HomePageComponent
  ]
})
export class HomeModule { }
