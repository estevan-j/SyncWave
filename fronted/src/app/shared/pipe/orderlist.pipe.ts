import { Pipe, PipeTransform } from '@angular/core';
import { TrackModel } from '@core/models/tracks.model';

@Pipe({
  name: 'orderlist'
})
export class OrderlistPipe implements PipeTransform {

  transform(value: TrackModel[], args: string|null=null, sort:string='asc'): TrackModel[] {
    
    console.log('👉', value)
    console.log('🎅', args)
    console.log('👩‍💻', sort)
    
    return value;
  }

}
