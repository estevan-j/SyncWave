import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { MediaPlayerComponent } from '@shared/components/media-player/media-player.component';
import { SideBarComponent } from '@shared/components/side-bar/side-bar.component';


@Component({
  selector: 'app-home-page',
  standalone: true, // Colocar standalone true para componentes indenpendientes 
  imports: [ SideBarComponent, MediaPlayerComponent, RouterModule],
  templateUrl: './home-page.component.html',
  styleUrl: './home-page.component.css'
})
export class HomePageComponent implements OnInit {

  constructor(){}

  ngOnInit(): void {
      
  }

}
