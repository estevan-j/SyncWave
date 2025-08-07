import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TracksPageComponent } from './pages/tracks-page/tracks-page.component';
import { MusicAdminPageComponent } from './pages/music-admin-page/music-admin-page.component';

const routes: Routes = [
  {
    path: '',
    component: TracksPageComponent,
    //outlet: 'child'
  },
  {
    path: 'admin',
    component: MusicAdminPageComponent
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TracksRoutingModule { }
