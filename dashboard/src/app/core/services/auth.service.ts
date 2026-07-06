import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { tap } from 'rxjs/operators';
import { environment } from '../../../environments/environment';
import { AuthResponse, LoginPayload, Mosque, SignupPayload } from '../models/models';

const TOKEN_KEY = 'mosqueebot_token';
const MOSQUE_KEY = 'mosqueebot_mosque';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  readonly mosque = signal<Mosque | null>(this._loadStoredMosque());

  private _loadStoredMosque(): Mosque | null {
    const raw = localStorage.getItem(MOSQUE_KEY);
    return raw ? (JSON.parse(raw) as Mosque) : null;
  }

  private _store(auth: AuthResponse): void {
    localStorage.setItem(TOKEN_KEY, auth.access_token);
    localStorage.setItem(MOSQUE_KEY, JSON.stringify(auth.mosque));
    this.mosque.set(auth.mosque);
  }

  login(payload: LoginPayload) {
    return this.http
      .post<AuthResponse>(`${this.base}/auth/login`, payload)
      .pipe(tap((auth) => this._store(auth)));
  }

  signup(payload: SignupPayload) {
    return this.http
      .post<AuthResponse>(`${this.base}/auth/signup`, payload)
      .pipe(tap((auth) => this._store(auth)));
  }

  markOnboardingCompleted(): void {
    const mosque = this.mosque();
    if (!mosque) return;
    const updated = { ...mosque, onboarding_completed: true };
    localStorage.setItem(MOSQUE_KEY, JSON.stringify(updated));
    this.mosque.set(updated);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(MOSQUE_KEY);
    this.mosque.set(null);
  }

  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  botLink(botUsername: string): string | null {
    const mosque = this.mosque();
    return mosque ? `https://t.me/${botUsername}?start=${mosque.slug}` : null;
  }
}
