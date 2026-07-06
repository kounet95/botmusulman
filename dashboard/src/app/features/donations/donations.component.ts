import { Component, inject, signal } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDialog } from '@angular/material/dialog';
import { DonationsService } from '../../core/services/donations.service';
import { NotificationService } from '../../core/services/notification.service';
import { DonationCampaign } from '../../core/models/models';
import { DonationDialogComponent } from './donation-dialog/donation-dialog.component';
import {
  ConfirmDialogComponent,
  ConfirmDialogData,
} from '../../shared/confirm-dialog/confirm-dialog.component';

@Component({
  selector: 'app-donations',
  standalone: true,
  imports: [
    MatTableModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressBarModule,
  ],
  templateUrl: './donations.component.html',
  styleUrl: './donations.component.scss',
})
export class DonationsComponent {
  private donationsService = inject(DonationsService);
  private notifications = inject(NotificationService);
  private dialog = inject(MatDialog);

  campaigns = signal<DonationCampaign[]>([]);
  loading = signal(true);
  displayedColumns = ['title', 'collected', 'goal', 'progress', 'status', 'actions'];

  constructor() {
    this.refresh();
  }

  refresh(): void {
    this.loading.set(true);
    this.donationsService.list().subscribe((campaigns) => {
      this.campaigns.set(campaigns);
      this.loading.set(false);
    });
  }

  progress(c: DonationCampaign): number {
    return c.goal_amount ? Math.round((c.collected_amount / c.goal_amount) * 100) : 0;
  }

  openCreate(): void {
    const ref = this.dialog.open(DonationDialogComponent, { width: '600px' });
    ref.afterClosed().subscribe((payload) => {
      if (!payload) return;
      this.donationsService.create(payload).subscribe(() => {
        this.notifications.success('Collecte créée ✅');
        this.refresh();
      });
    });
  }

  toggle(campaign: DonationCampaign): void {
    this.donationsService.toggle(campaign.id).subscribe(() => {
      this.notifications.success('Statut modifié');
      this.refresh();
    });
  }

  remove(campaign: DonationCampaign): void {
    const ref = this.dialog.open<ConfirmDialogComponent, ConfirmDialogData, boolean>(
      ConfirmDialogComponent,
      {
        data: {
          title: 'Supprimer cette collecte ?',
          message: `« ${campaign.title} » sera définitivement supprimée.`,
        },
      }
    );
    ref.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.donationsService.delete(campaign.id).subscribe(() => {
        this.notifications.success('Collecte supprimée');
        this.refresh();
      });
    });
  }
}
