import { Component, inject, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog } from '@angular/material/dialog';
import { ContentService } from '../../core/services/content.service';
import { NotificationService } from '../../core/services/notification.service';
import { ContentItem } from '../../core/models/models';
import { ContentDialogComponent } from './content-dialog/content-dialog.component';
import {
  ConfirmDialogComponent,
  ConfirmDialogData,
} from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-content',
  standalone: true,
  imports: [MatTableModule, MatCardModule, MatButtonModule, MatIconModule, MatChipsModule],
  templateUrl: './content.component.html',
  styleUrl: './content.component.scss',
})
export class ContentComponent {
  private contentService = inject(ContentService);
  private notifications = inject(NotificationService);
  private dialog = inject(MatDialog);

  items = signal<ContentItem[]>([]);
  loading = signal(true);
  displayedColumns = ['type', 'content', 'source', 'date', 'actions'];

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.contentService.list().subscribe((items) => {
      this.items.set(items);
      this.loading.set(false);
    });
  }

  openCreate(): void {
    const ref = this.dialog.open(ContentDialogComponent, { width: '600px' });
    ref.afterClosed().subscribe((payload) => {
      if (!payload) return;
      this.contentService.create(payload).subscribe(() => {
        this.notifications.success('Contenu ajouté ✅');
        this.refresh();
      });
    });
  }

  remove(item: ContentItem): void {
    const ref = this.dialog.open<ConfirmDialogComponent, ConfirmDialogData, boolean>(
      ConfirmDialogComponent,
      { data: { title: 'Supprimer ce contenu ?', message: 'Cette action est irréversible.' } }
    );
    ref.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.contentService.delete(item.id).subscribe(() => {
        this.notifications.success('Contenu supprimé');
        this.refresh();
      });
    });
  }
}
