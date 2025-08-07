import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { HistoryRoutingModule } from './history-routing.module';


@NgModule({
  declarations: [], //Solo se declara cuando es standalone
  imports: [
    CommonModule,
    HistoryRoutingModule
  ]
})
export class HistoryModule { }
