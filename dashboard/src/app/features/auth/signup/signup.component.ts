import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
  ],
  template: `
    <div class="auth-page">
      <mat-card class="auth-card">
        <h1>🌙 MosquéeBot</h1>
        <p class="subtitle">Créer le compte de votre mosquée</p>

        <form [formGroup]="form" (ngSubmit)="submit()">
          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Nom de la mosquée</mat-label>
            <input matInput formControlName="mosque_name" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Ville</mat-label>
            <input matInput formControlName="city" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Pays (code, ex: CA, FR, GN)</mat-label>
            <input matInput formControlName="country" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Votre nom</mat-label>
            <input matInput formControlName="full_name" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Email</mat-label>
            <input matInput type="email" formControlName="email" autocomplete="email" />
          </mat-form-field>

          <mat-form-field appearance="outline" class="full-width">
            <mat-label>Mot de passe</mat-label>
            <input matInput type="password" formControlName="password" autocomplete="new-password" />
          </mat-form-field>

          <button mat-flat-button color="primary" class="full-width" type="submit" [disabled]="loading()">
            @if (loading()) {
              <mat-spinner diameter="20"></mat-spinner>
            } @else {
              Créer mon compte
            }
          </button>
        </form>

        <p class="switch">
          Déjà un compte ? <a routerLink="/login">Se connecter</a>
        </p>
      </mat-card>
    </div>
  `,
  styles: [`
    .auth-page { display: flex; align-items: center; justify-content: center; min-height: 100vh; padding: 16px; }
    .auth-card { max-width: 440px; width: 100%; padding: 24px; }
    .subtitle { color: rgba(0, 0, 0, 0.6); margin-bottom: 24px; }
    .full-width { width: 100%; margin-bottom: 8px; }
    .switch { text-align: center; margin-top: 16px; }
  `],
})
export class SignupComponent {
  private fb = inject(FormBuilder);
  private authService = inject(AuthService);
  private router = inject(Router);

  loading = signal(false);

  form = this.fb.nonNullable.group({
    mosque_name: ['', Validators.required],
    city: ['', Validators.required],
    country: ['GN', Validators.required],
    full_name: [''],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
  });

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.loading.set(true);
    this.authService.signup(this.form.getRawValue()).subscribe({
      next: () => this.router.navigateByUrl('/onboarding'),
      error: () => this.loading.set(false),
    });
  }
}
