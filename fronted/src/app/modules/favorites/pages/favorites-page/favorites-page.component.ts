import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';  // Importa CommonModule
import { RouterModule } from '@angular/router';
import { PlayListHeaderComponent } from '@shared/components/play-list-header/play-list-header.component';
import { PlayListBodyComponent } from '@shared/components/play-list-body/play-list-body.component';

@Component({
  selector: 'app-favorites-page',
  standalone: true, // En este caso es stanalone true
  imports: [CommonModule, RouterModule, PlayListHeaderComponent, PlayListBodyComponent ], 
  templateUrl: './favorites-page.component.html',
  styleUrl: './favorites-page.component.css'
})
export class FavoritesPageComponent implements OnInit{

  constructor() {

  }

  ngOnInit(): void {
      
  }
}
