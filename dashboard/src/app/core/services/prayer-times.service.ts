import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { PrayerTimes } from '../models/models';

@Injectable({ providedIn: 'root' })
export class PrayerTimesService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  get() {
    return this.http.get<PrayerTimes>(`${this.base}/dashboard/prayer-times`);
  }
}
