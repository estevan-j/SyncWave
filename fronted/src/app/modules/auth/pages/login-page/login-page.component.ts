import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';  // Importa CommonModule
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
// import { AuthService } from '@modules/auth/services/auth.service';


@Component({
  selector: 'app-login-page',
  imports: [CommonModule, ReactiveFormsModule],
  standalone: true,
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.css'
})
export class LoginPageComponent implements OnInit {
  
  formLogin: FormGroup = new FormGroup({});

  constructor(){

  }

  ngOnInit(): void { //Ciclo de vida principal
      this.formLogin = new FormGroup(
        {
          email: new FormControl('',[
            Validators.required,  //validadcion para que exista algo
            Validators.email      // validadcion para que lo ingresado sea un email
          ]),
          password: new FormControl('',[
            Validators.required,
            Validators.minLength(6),
            Validators.maxLength(12)
          ]),
        }
      )
  }

  sendLogin():void{
    const body = this.formLogin.value
    console.log('💥💥💥', body);
  }
  // sendLogin():void{
  //   const {email, password} = this.formLogin.value
  //   this.authService.sendCredentials(email,password)
  // }


}
