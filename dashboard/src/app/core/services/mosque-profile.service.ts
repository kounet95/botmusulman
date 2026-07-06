import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { MosqueProfile, MosqueProfilePayload, PhotoKind } from '../models/models';

@Injectable({ providedIn: 'root' })
export class MosqueProfileService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  getProfile() {
    return this.http.get<MosqueProfile>(`${this.base}/mosque/profile`);
  }

  updateProfile(payload: MosqueProfilePayload) {
    return this.http.patch<MosqueProfile>(`${this.base}/mosque/profile`, payload);
  }

  uploadPhoto(kind: PhotoKind, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{ url: string }>(`${this.base}/mosque/photo?kind=${kind}`, formData);
  }
}
