import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';  // Importa CommonModule
import { SectionGenericComponent } from '@shared/components/section-generic/section-generic.component';
import { RouterModule } from '@angular/router';
import * as dataRaw from '../../../../data/tracks.json'
import { TrackModel } from '@core/models/tracks.model';

@Component({
  selector: 'app-tracks-page',
  standalone: true, // Asegúrate que esto esté presente
  // Agrega aquí otros componentes/directivas/pipes que necesites
  imports: [CommonModule, SectionGenericComponent, RouterModule ], 
  templateUrl: './tracks-page.component.html',
  styleUrl: './tracks-page.component.css'
})
export class TracksPageComponent implements OnInit{

  mockTracksList: Array<TrackModel> = [
    
  ]
  constructor(){
    
  }
  ngOnInit(): void {
    const {data}: any = (dataRaw as any).default
    this.mockTracksList = data;
  }
}
