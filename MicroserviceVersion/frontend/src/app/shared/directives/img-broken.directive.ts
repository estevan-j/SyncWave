import { Directive, ElementRef, HostListener, Input } from '@angular/core';


@Directive({
  selector: 'img[appImgBroken]',
  standalone: true
})
export class ImgBrokenDirective {
  @Input() customImg: string=''
  //host Host HOST
  @HostListener('error') handleError(): void{
    const elNative = this.elHost.nativeElement;
    console.log('🔴 Esta imagen revento ->', this.elHost);
    //elNative.src='images/imgbroken.jpg'
    //elNative.src='https://i.pinimg.com/736x/69/d5/3e/69d53ef9520b57a5e2af1b1387807fc7.jpg'
    elNative.src=this.customImg
  }

  constructor(private elHost: ElementRef) { 
    console.log(this.elHost);
  }

}