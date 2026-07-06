import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Activity, ActivityPayload } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ActivitiesService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  list() {
    return this.http.get<Activity[]>(`${this.base}/activities/`);
  }

  create(payload: ActivityPayload) {
    return this.http.post<Activity>(`${this.base}/activities/`, payload);
  }

  update(id: number, payload: Partial<ActivityPayload>) {
    return this.http.patch<Activity>(`${this.base}/activities/${id}`, payload);
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}/activities/${id}`);
  }
}
