import { Component, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { DashboardService } from '../../core/services/dashboard.service';
import { DashboardStats, RecentActivity } from '../../core/models/models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    RouterLink,
    DecimalPipe,
    MatCardModule,
    MatTableModule,
    MatProgressBarModule,
    MatChipsModule,
    MatButtonModule,
  ],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
  private dashboardService = inject(DashboardService);

  stats = signal<DashboardStats | null>(null);
  upcoming = signal<RecentActivity[]>([]);
  loading = signal(true);
  displayedColumns = ['title', 'when', 'type', 'registered', 'progress'];

  constructor() {
    this.dashboardService.getStats().subscribe((stats) => this.stats.set(stats));
    this.dashboardService.getRecentActivities().subscribe((activities) => {
      this.upcoming.set(activities);
      this.loading.set(false);
    });
  }

  fillRate(a: RecentActivity): number {
    return a.capacity ? Math.round((a.registered_count / a.capacity) * 100) : 0;
  }
}
