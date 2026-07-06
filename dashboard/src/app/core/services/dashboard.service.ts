import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { DashboardStats, RecentActivity } from '../models/models';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  getStats() {
    return this.http.get<DashboardStats>(`${this.base}/dashboard/stats`);
  }

  getRecentActivities() {
    return this.http.get<RecentActivity[]>(`${this.base}/dashboard/activities/recent`);
  }
}
