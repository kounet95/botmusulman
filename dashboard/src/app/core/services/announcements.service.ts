import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Announcement, AnnouncementPayload } from '../models/models';

@Injectable({ providedIn: 'root' })
export class AnnouncementsService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  list() {
    return this.http.get<Announcement[]>(`${this.base}/announcements/`);
  }

  create(payload: AnnouncementPayload) {
    return this.http.post<Announcement>(`${this.base}/announcements/`, payload);
  }
}
