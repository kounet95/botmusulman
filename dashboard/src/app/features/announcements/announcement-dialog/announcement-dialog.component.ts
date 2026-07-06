import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatButtonModule } from '@angular/material/button';
import { AnnouncementPayload } from '../../../core/models/models';

@Component({
  selector: 'app-announcement-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatButtonModule,
  ],
  templateUrl: './announcement-dialog.component.html',
  styleUrl: './announcement-dialog.component.scss',
})
export class AnnouncementDialogComponent {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<AnnouncementDialogComponent>);

  form = this.fb.nonNullable.group({
    title: ['', Validators.required],
    body: ['', Validators.required],
    send_now: [false],
  });

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload: AnnouncementPayload = {
      title: value.title,
      body: value.body,
      send_now: value.send_now,
    };
    this.dialogRef.close(payload);
  }
}
