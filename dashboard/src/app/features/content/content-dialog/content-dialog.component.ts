import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { ContentService } from '../../../core/services/content.service';
import { ContentPayload, ContentTemplate, ContentType } from '../../../core/models/models';

const CONTENT_TYPES: { value: ContentType; label: string }[] = [
  { value: 'hadith', label: '📖 Hadith' },
  { value: 'verset', label: '✨ Verset coranique' },
  { value: 'rappel', label: '💡 Rappel spirituel' },
  { value: 'dua', label: '🤲 Dua' },
];

interface TemplateOption {
  label: string;
  template: ContentTemplate;
}

@Component({
  selector: 'app-content-dialog',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
  ],
  templateUrl: './content-dialog.component.html',
  styleUrl: './content-dialog.component.scss',
})
export class ContentDialogComponent {
  private fb = inject(FormBuilder);
  private dialogRef = inject(MatDialogRef<ContentDialogComponent>);
  private contentService = inject(ContentService);

  readonly types = CONTENT_TYPES;
  templateOptions = signal<TemplateOption[]>([]);

  form = this.fb.nonNullable.group({
    type: ['hadith' as ContentType, Validators.required],
    scheduled_date: ['', Validators.required],
    content_ar: [''],
    content_fr: ['', Validators.required],
    source: [''],
  });

  constructor() {
    this.contentService.getTemplates().subscribe((templates) => {
      const options: TemplateOption[] = [
        ...(templates.hadiths || []).map((t, i) => ({
          label: `Hadith ${i + 1}: ${(t.content_fr || '').substring(0, 50)}...`,
          template: { ...t, type: 'hadith' as ContentType },
        })),
        ...(templates.versets || []).map((t, i) => ({
          label: `Verset ${i + 1}: ${(t.content_fr || '').substring(0, 50)}...`,
          template: { ...t, type: 'verset' as ContentType },
        })),
      ];
      this.templateOptions.set(options);
    });
  }

  applyTemplate(option: TemplateOption): void {
    const t = option.template;
    this.form.patchValue({
      type: t.type || 'hadith',
      content_ar: t.content_ar || '',
      content_fr: t.content_fr || '',
      source: t.source || '',
    });
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload: ContentPayload = {
      type: value.type,
      content_ar: value.content_ar || null,
      content_fr: value.content_fr,
      source: value.source || null,
      scheduled_date: value.scheduled_date,
    };
    this.dialogRef.close(payload);
  }
}
