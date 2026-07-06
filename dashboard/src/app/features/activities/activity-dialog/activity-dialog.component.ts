import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { Activity, ActivityPayload, ActivityType } from '../../../core/models/models';

export interface ActivityDialogData {
  activity: Activity | null;
}

const ACTIVITY_TYPES: { value: ActivityType; label: string }[] = [
  { value: 'cours', label: '🎓 Cours régulier' },
  { value: 'conference', label: '🎤 Conférence' },
  { value: 'halaqa', label: '📖 Halaqa' },
  { value: 'evenement', label: '🗓️ Événement' },
  { value: 'autre', label: '🌟 Autre' },
];

@Component({
  selector: 'app-activity-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatButtonModule,
  ],
  templateUrl: './activity-dialog.component.html',
  styleUrl: './activity-dialog.component.scss',
})
export class ActivityDialogComponent {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ActivityDialogComponent>);
  data: ActivityDialogData = inject(MAT_DIALOG_DATA);

  readonly types = ACTIVITY_TYPES;
  readonly isEdit = !!this.data.activity;

  form = this.fb.nonNullable.group({
    title: [this.data.activity?.title ?? '', Validators.required],
    type: [this.data.activity?.type ?? ('cours' as ActivityType), Validators.required],
    speaker: [this.data.activity?.speaker ?? ''],
    date: [this.data.activity?.date ?? '', Validators.required],
    time: [this.data.activity?.time?.slice(0, 5) ?? '', Validators.required],
    capacity: [this.data.activity?.capacity ?? 30, [Validators.required, Validators.min(1)]],
    location: [this.data.activity?.location ?? 'Mosquée'],
    description: [this.data.activity?.description ?? ''],
    is_paid: [this.data.activity?.is_paid ?? false],
    price: [this.data.activity?.price ?? null],
    livestream_url: [this.data.activity?.livestream_url ?? ''],
  });

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload: ActivityPayload = {
      title: value.title,
      type: value.type,
      speaker: value.speaker || null,
      date: value.date,
      time: value.time,
      capacity: value.capacity,
      location: value.location || null,
      description: value.description || null,
      is_paid: value.is_paid,
      price: value.is_paid ? value.price : null,
      livestream_url: value.livestream_url || null,
    };
    this.dialogRef.close(payload);
  }
}
