import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Member } from '../models/models';

@Injectable({ providedIn: 'root' })
export class MembersService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  list() {
    return this.http.get<Member[]>(`${this.base}/members/`);
  }
}
