import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { AnnouncementsService } from '../../core/services/announcements.service';
import { NotificationService } from '../../core/services/notification.service';
import { Announcement } from '../../core/models/models';
import { AnnouncementDialogComponent } from './announcement-dialog/announcement-dialog.component';

@Component({
  selector: 'app-announcements',
  standalone: true,
  imports: [DatePipe, MatTableModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule],
  templateUrl: './announcements.component.html',
  styleUrl: './announcements.component.scss',
})
export class AnnouncementsComponent {
  private announcementsService = inject(AnnouncementsService);
  private notifications = inject(NotificationService);
  private dialog = inject(MatDialog);

  announcements = signal<Announcement[]>([]);
  loading = signal(true);
  displayedColumns = ['title', 'body', 'date', 'status'];

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.announcementsService.list().subscribe((announcements) => {
      this.announcements.set(announcements);
      this.loading.set(false);
    });
  }

  openCreate(): void {
    const ref = this.dialog.open(AnnouncementDialogComponent, { width: '600px' });
    ref.afterClosed().subscribe((payload) => {
      if (!payload) return;
      this.announcementsService.create(payload).subscribe(() => {
        this.notifications.success(
          payload.send_now ? 'Annonce envoyée à tous les membres ✅' : 'Annonce sauvegardée ✅'
        );
        this.refresh();
      });
    });
  }
}
