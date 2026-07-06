import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { DonationCampaignPayload, DonationType } from '../../../core/models/models';

const DONATION_TYPES: { value: DonationType; label: string }[] = [
  { value: 'general', label: '💚 Don général' },
  { value: 'projet', label: '💛 Projet spécifique' },
  { value: 'zakat', label: '🌙 Zakat' },
  { value: 'bourse', label: '📚 Bourse étudiants' },
];

@Component({
  selector: 'app-donation-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
  ],
  templateUrl: './donation-dialog.component.html',
  styleUrl: './donation-dialog.component.scss',
})
export class DonationDialogComponent {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<DonationDialogComponent>);

  readonly types = DONATION_TYPES;

  form = this.fb.nonNullable.group({
    title: ['', Validators.required],
    type: ['general' as DonationType, Validators.required],
    goal_amount: [null as number | null],
    description: [''],
    payment_url: [''],
    orange_money_number: [''],
    mtn_momo_number: [''],
  });

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload: DonationCampaignPayload = {
      title: value.title,
      type: value.type,
      goal_amount: value.goal_amount,
      description: value.description || null,
      payment_url: value.payment_url || null,
      orange_money_number: value.orange_money_number || null,
      mtn_momo_number: value.mtn_momo_number || null,
    };
    this.dialogRef.close(payload);
  }
}
