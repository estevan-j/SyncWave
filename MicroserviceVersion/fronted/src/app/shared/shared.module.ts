import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SideBarComponent } from './components/side-bar/side-bar.component';
import { MediaPlayerComponent } from './components/media-player/media-player.component';
import { HeaderUserComponent } from './components/header-user/header-user.component';
import { CardPlayerComponent } from './components/card-player/card-player.component';
import { SectionGenericComponent } from './components/section-generic/section-generic.component';
import { PlayListHeaderComponent } from './components/play-list-header/play-list-header.component';
import { PlayListBodyComponent } from './components/play-list-body/play-list-body.component';
import { RouterModule } from '@angular/router';
import { OrderlistPipe } from './pipe/orderlist.pipe';
import { ImgBrokenDirective } from './directives/img-broken.directive';


@NgModule({
  declarations: [
    //SideBarComponent, //SOLO compomentes NO standalone aqui
  ],
  imports: [
    CommonModule,
    SideBarComponent,
    MediaPlayerComponent,
    HeaderUserComponent,
    CardPlayerComponent,
    SectionGenericComponent, 
    PlayListHeaderComponent,
    PlayListBodyComponent,
    RouterModule,
    OrderlistPipe,
    ImgBrokenDirective
  ],
  exports:[
    SideBarComponent,
    MediaPlayerComponent,
    HeaderUserComponent,
    CardPlayerComponent,
    SectionGenericComponent,
    PlayListHeaderComponent,
    PlayListBodyComponent,
    OrderlistPipe,
    ImgBrokenDirective
  ]
})
export class SharedModule { }
