import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; // Añade esta línea
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-side-bar',
  standalone: true, // Asegúrate que esto esté presente
  imports: [CommonModule, RouterModule], // Agrega aquí otros componentes/directivas/pipes que necesites
  templateUrl: './side-bar.component.html',
  styleUrl: './side-bar.component.css'
})
export class SideBarComponent implements OnInit {

  mainMenu: {
    defaultOptions: Array<any>, accessLink: Array<any>
  } = { defaultOptions: [], accessLink: [] }

  customOptions: Array<any> = []

  constructor(private router: Router) { }

  //Router Link

  ngOnInit(): void {
    //Rutas del side bar
    this.mainMenu.defaultOptions = [
      /*{
        name: 'Home',
        icon: 'uil uil-estate',
        router: ['/', 'auth']  
      },*/      {
        name: 'Home', //Se redirige al home principal (tracks)
        icon: 'uil uil-estate',
        router: ['/home']
      },
      {
        name: 'Buscar',  //Se redirige al historial de canciones
        icon: 'uil uil-search',
        router: ['/home/history']
      },{
        name: 'Tu biblioteca', //Se redirige al las canciones
        icon: 'uil uil-chart',
        router: ['/home/favorites'],        //query: { hola: 'mundo' }
      }
    ];

    this.mainMenu.accessLink = [
      {
        name: 'Crear lista',
        icon: 'uil-plus-square'      }, {
        name: 'Canciones que te gustan',
        icon: 'uil-heart-medical',
        router: ['/home/favorites/liked-songs']
      },
      {
        name: 'Subir música',
        icon: 'uil-cloud-upload',
        router: ['/home/tracks/admin']
      }
    ];

    this.customOptions = [
      {
        name: 'Mi lista º1',
        router: ['/']
      },
      {
        name: 'Mi lista º2',
        router: ['/']
      },
      {
        name: 'Mi lista º3',
        router: ['/']
      },
      {
        name: 'Mi lista º4',
        router: ['/']
      }
    ]
  }
  /*
  goTo($event:any):void{
    this.router.navigate(['/', 'favorites'],{
      queryParams:{
        key1:'valor1',
        key2:'valor2',
        key3:'valor3'
      }
    })
    console.log($event)
  }*/
}
