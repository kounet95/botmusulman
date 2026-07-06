import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { ContentItem, ContentPayload, ContentTemplates } from '../models/models';

@Injectable({ providedIn: 'root' })
export class ContentService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  list() {
    return this.http.get<ContentItem[]>(`${this.base}/content/`);
  }

  create(payload: ContentPayload) {
    return this.http.post<ContentItem>(`${this.base}/content/`, payload);
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}/content/${id}`);
  }

  getTemplates() {
    return this.http.get<ContentTemplates>(`${this.base}/content/templates`);
  }
}
