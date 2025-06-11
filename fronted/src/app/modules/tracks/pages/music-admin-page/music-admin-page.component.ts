import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MusicUploadComponent } from '@shared/components/music-upload/music-upload.component';

@Component({
    selector: 'app-music-admin-page',
    standalone: true,
    imports: [CommonModule, MusicUploadComponent],
    templateUrl: './music-admin-page.component.html',
    styleUrls: ['./music-admin-page.component.css']
})
export class MusicAdminPageComponent {

    constructor() { }

}
