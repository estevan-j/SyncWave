import { Pipe, PipeTransform } from '@angular/core';
import { TrackModel } from '@core/models/tracks.model';

@Pipe({
  name: 'orderlist'
})
export class OrderlistPipe implements PipeTransform {

  // transform(value: TrackModel[], args: string|null=null, sort:string='asc'): TrackModel[] {
    
  //   console.log('👉', value)
  //   console.log('🎅', args)
  //   console.log('👩‍💻', sort)
  //   // Se retorna value para agregar el listado de canciones
  //   return value;
  // }

  transform(value: Array<any>, args: string|null=null, sort:string='asc'): TrackModel[] {
    
    try{
      if(args==null){
         return value
      } else{
        const tmpList = value.sort((a,b)=>{
          if(a[args]<b[args]){
            return -1
          }
          else if (a[args]==b[args]){
            return 0
          }
          else if (a[args]> b[args]){
            return 1;
          }
          return 1
        });
        return (sort=='asc')? tmpList : tmpList.reverse()
      }

    }catch(e){
      console.log('Algo paso');
      return value
    }
    
    //return value;
  }

}
