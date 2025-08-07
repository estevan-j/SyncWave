import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../../environments/environment'; // Asegúrate de que la ruta sea correcta

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly API_BASE_URL = environment.apiUrl; // Usa la variable del environment

  constructor(private http: HttpClient) { }

  post(endpoint: string, body: any) {
    return this.http.post(`${this.API_BASE_URL}${endpoint}`, body);
  }

  get(endpoint: string) {
    return this.http.get(`${this.API_BASE_URL}${endpoint}`);
  }

  put(endpoint: string, body: any) {
    return this.http.put(`${this.API_BASE_URL}${endpoint}`, body);
  }

  delete(endpoint: string) {
    return this.http.delete(`${this.API_BASE_URL}${endpoint}`);
  }

  postWithAuth(endpoint: string, body: any, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.API_BASE_URL}${endpoint}`, body, { headers });
  }

  getWithAuth(endpoint: string, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.get(`${this.API_BASE_URL}${endpoint}`, { headers });
  }

  putWithAuth(endpoint: string, body: any, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    });

    return this.http.put(`${this.API_BASE_URL}${endpoint}`, body, { headers });
  }

  deleteWithAuth(endpoint: string, token: string) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    return this.http.delete(`${this.API_BASE_URL}${endpoint}`, { headers });
  }
}