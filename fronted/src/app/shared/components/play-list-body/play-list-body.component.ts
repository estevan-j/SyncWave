import { Component, OnInit } from '@angular/core';
import * as dataRaw from '../../../data/tracks.json'
import { TrackModel } from '@core/models/tracks.model';
import { CommonModule } from '@angular/common'; // Añade esta línea
import { OrderlistPipe } from '@shared/pipe/orderlist.pipe';

@Component({
  selector: 'app-play-list-body',
  standalone: true, // Asegúrate que esto esté presente
  imports: [CommonModule, OrderlistPipe],
  templateUrl: './play-list-body.component.html',
  styleUrl: './play-list-body.component.css'
})
export class PlayListBodyComponent implements OnInit{
  //Puede ser de esta manera tambien tracks: TrackModel[]=[]
  tracks: Array<TrackModel>=[]
  optionSort: {property: string | null, order:string} = {property: null, order: 'asc'}

  constructor(){

  }

  ngOnInit(): void {
      const {data} : any = (dataRaw as any).default
      this.tracks = data;
  }

  changeSort(property: string): void{
    const {order} = this.optionSort
    this.optionSort={
      property:property,
      order: order == 'asc'? 'desc': 'asc'
    }
    console.log(this.optionSort);
  }

}
