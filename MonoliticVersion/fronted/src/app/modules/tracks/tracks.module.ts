import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TracksRoutingModule } from './tracks-routing.module';
import { TracksPageComponent } from './pages/tracks-page/tracks-page.component';
import { SharedModule } from '@shared/shared.module';
import { SectionGenericComponent } from '@shared/components/section-generic/section-generic.component';


@NgModule({
  declarations: [
    //No se declara si es standalone
  ],
  imports: [
    CommonModule,
    TracksRoutingModule,
    SharedModule,
    TracksPageComponent,
    //SectionGenericComponent
    
  ],
  exports: [
    CommonModule,
    TracksRoutingModule,
    //SharedModule,
    //TracksPageComponent
    
  ]
})
export class TracksModule { }
