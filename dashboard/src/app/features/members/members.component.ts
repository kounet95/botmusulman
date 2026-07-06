import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MembersService } from '../../core/services/members.service';
import { Member } from '../../core/models/models';

const NOTIF_KEYS = ['prayer_times', 'jumua', 'courses', 'conferences', 'announcements'] as const;

@Component({
  selector: 'app-members',
  standalone: true,
  imports: [DatePipe, MatTableModule, MatCardModule, MatChipsModule],
  templateUrl: './members.component.html',
  styleUrl: './members.component.scss',
})
export class MembersComponent {
  private membersService = inject(MembersService);

  members = signal<Member[]>([]);
  loading = signal(true);
  displayedColumns = ['name', 'username', 'telegram_id', 'joined', 'notifications'];

  constructor() {
    this.membersService.list().subscribe((members) => {
      this.members.set(members);
      this.loading.set(false);
    });
  }

  activeNotifications(member: Member): number {
    return NOTIF_KEYS.filter((key) => member[key] !== false).length;
  }
}
