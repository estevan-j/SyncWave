import { ElementRef } from '@angular/core';
import { ImgBrokenDirective } from './img-broken.directive';

describe('ImgBrokenDirective', () => {
  it('should create an instance', () => {
    // Creamos un mock de ElementRef con un elemento img simulado
    const mockElementRef = {
      nativeElement: document.createElement('img')
    } as ElementRef;

    // Pasamos el mock al constructor
    const directive = new ImgBrokenDirective(mockElementRef);

    expect(directive).toBeTruthy();
  });
});
