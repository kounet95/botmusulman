import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatStepperModule } from '@angular/material/stepper';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { MosqueProfileService } from '../../core/services/mosque-profile.service';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { COUNTRIES } from '../../core/constants/countries';
import { environment } from '../../../environments/environment';

function mediaUrl(url: string | null): string | null {
  return url ? `${environment.apiBase}${url}` : null;
}
import {
  AMENITIES,
  INSTALLATION_TYPES,
  InstallationType,
  MosqueProfilePayload,
  PhotoKind,
} from '../../core/models/models';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatCheckboxModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.scss',
})
export class OnboardingComponent {
  private fb = inject(FormBuilder);
  private mosqueProfileService = inject(MosqueProfileService);
  private authService = inject(AuthService);
  private notifications = inject(NotificationService);
  private router = inject(Router);

  readonly installationTypes = INSTALLATION_TYPES;
  readonly countries = COUNTRIES;
  readonly amenities = AMENITIES;

  saving = signal(false);
  uploading = signal<PhotoKind | null>(null);
  photoUrls = signal<Record<PhotoKind, string | null>>({ exterior: null, interior: null, logo: null });

  typeForm = this.fb.nonNullable.group({
    installation_type: ['mosque' as InstallationType, Validators.required],
  });

  infoForm = this.fb.nonNullable.group({
    name: ['', Validators.required],
    address: ['', Validators.required],
    city: ['', Validators.required],
    postal_code: ['', Validators.required],
    country: ['GN', Validators.required],
    association_name: [''],
    phone: [''],
    email: ['', Validators.email],
    website: [''],
    payment_url: [''],
  });

  detailsForm = this.fb.nonNullable.group({
    amenities: this.fb.nonNullable.array(this.amenities.map(() => false)),
    construction_year: [null as number | null],
    capacity_women: [null as number | null],
    capacity_men: [null as number | null],
    history: ['', Validators.maxLength(200)],
    other_info: ['', Validators.maxLength(200)],
  });

  constructor() {
    this.mosqueProfileService.getProfile().subscribe((profile) => {
      this.typeForm.patchValue({ installation_type: profile.installation_type ?? 'mosque' });
      this.infoForm.patchValue({
        name: profile.name,
        address: profile.address ?? '',
        city: profile.city,
        postal_code: profile.postal_code ?? '',
        country: profile.country || 'GN',
        association_name: profile.association_name ?? '',
        phone: profile.phone ?? '',
        email: profile.email ?? '',
        website: profile.website ?? '',
        payment_url: profile.payment_url ?? '',
      });
      this.detailsForm.patchValue({
        construction_year: profile.construction_year,
        capacity_women: profile.capacity_women,
        capacity_men: profile.capacity_men,
        history: profile.history ?? '',
        other_info: profile.other_info ?? '',
      });
      this.amenities.forEach((a, i) => {
        this.amenitiesArray.at(i).setValue(profile.amenities.includes(a.key));
      });
      this.photoUrls.set({
        exterior: mediaUrl(profile.exterior_photo_url),
        interior: mediaUrl(profile.interior_photo_url),
        logo: mediaUrl(profile.logo_url),
      });
    });
  }

  get amenitiesArray() {
    return this.detailsForm.controls.amenities;
  }

  private selectedAmenityKeys(): string[] {
    return this.amenities.filter((_, i) => this.amenitiesArray.at(i).value).map((a) => a.key);
  }

  saveStep(step: 'type' | 'info' | 'details'): void {
    const forms = { type: this.typeForm, info: this.infoForm, details: this.detailsForm };
    const form = forms[step];
    if (form.invalid) {
      form.markAllAsTouched();
      return;
    }

    let payload: MosqueProfilePayload;
    if (step === 'type') {
      payload = { installation_type: this.typeForm.getRawValue().installation_type };
    } else if (step === 'info') {
      const v = this.infoForm.getRawValue();
      payload = {
        name: v.name,
        address: v.address,
        city: v.city,
        postal_code: v.postal_code,
        country: v.country,
        association_name: v.association_name || null,
        phone: v.phone || null,
        email: v.email || null,
        website: v.website || null,
        payment_url: v.payment_url || null,
      };
    } else {
      const v = this.detailsForm.getRawValue();
      payload = {
        amenities: this.selectedAmenityKeys(),
        construction_year: v.construction_year,
        capacity_women: v.capacity_women,
        capacity_men: v.capacity_men,
        history: v.history || null,
        other_info: v.other_info || null,
      };
    }

    this.saving.set(true);
    this.mosqueProfileService.updateProfile(payload).subscribe({
      next: () => this.saving.set(false),
      error: () => this.saving.set(false),
    });
  }

  onPhotoSelected(kind: PhotoKind, event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    this.uploading.set(kind);
    this.mosqueProfileService.uploadPhoto(kind, file).subscribe({
      next: ({ url }) => {
        this.photoUrls.update((urls) => ({ ...urls, [kind]: mediaUrl(url) }));
        this.uploading.set(null);
      },
      error: () => this.uploading.set(null),
    });
  }

  get canFinish(): boolean {
    const urls = this.photoUrls();
    return !!urls.exterior && !!urls.interior;
  }

  finish(): void {
    if (!this.canFinish) {
      this.notifications.error('Les photos extérieure et intérieure sont obligatoires');
      return;
    }
    this.authService.markOnboardingCompleted();
    this.notifications.success('Profil de votre mawaqit complété ✅');
    this.router.navigateByUrl('/dashboard');
  }
}
