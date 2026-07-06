import { Component, inject, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatCardModule } from '@angular/material/card';
import { MatDialog } from '@angular/material/dialog';
import { ActivitiesService } from '../../core/services/activities.service';
import { NotificationService } from '../../core/services/notification.service';
import { Activity } from '../../core/models/models';
import {
  ActivityDialogComponent,
  ActivityDialogData,
} from './activity-dialog/activity-dialog.component';
import {
  ConfirmDialogComponent,
  ConfirmDialogData,
} from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-activities',
  standalone: true,
  imports: [MatTableModule, MatButtonModule, MatIconModule, MatChipsModule, MatCardModule],
  templateUrl: './activities.component.html',
  styleUrl: './activities.component.scss',
})
export class ActivitiesComponent {
  private activitiesService = inject(ActivitiesService);
  private notifications = inject(NotificationService);
  private dialog = inject(MatDialog);

  activities = signal<Activity[]>([]);
  loading = signal(true);
  displayedColumns = ['title', 'date', 'type', 'places', 'price', 'location', 'actions'];

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.activitiesService.list().subscribe((activities) => {
      this.activities.set(activities);
      this.loading.set(false);
    });
  }

  openCreate(): void {
    this.openDialog(null);
  }

  openEdit(activity: Activity): void {
    this.openDialog(activity);
  }

  private openDialog(activity: Activity | null): void {
    const ref = this.dialog.open(ActivityDialogComponent, {
      data: { activity } as ActivityDialogData,
      width: '600px',
    });
    ref.afterClosed().subscribe((payload) => {
      if (!payload) return;
      const request = activity
        ? this.activitiesService.update(activity.id, payload)
        : this.activitiesService.create(payload);
      request.subscribe(() => {
        this.notifications.success(activity ? 'Activité modifiée ✅' : 'Activité créée ✅');
        this.refresh();
      });
    });
  }

  remove(activity: Activity): void {
    const ref = this.dialog.open<ConfirmDialogComponent, ConfirmDialogData, boolean>(
      ConfirmDialogComponent,
      {
        data: {
          title: 'Supprimer cette activité ?',
          message: `« ${activity.title} » sera définitivement supprimée.`,
        },
      }
    );
    ref.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.activitiesService.delete(activity.id).subscribe(() => {
        this.notifications.success('Activité supprimée');
        this.refresh();
      });
    });
  }
}
