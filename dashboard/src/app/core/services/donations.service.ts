import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { DonationCampaign, DonationCampaignPayload } from '../models/models';

@Injectable({ providedIn: 'root' })
export class DonationsService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  list() {
    return this.http.get<DonationCampaign[]>(`${this.base}/donations/campaigns`);
  }

  create(payload: DonationCampaignPayload) {
    return this.http.post<DonationCampaign>(`${this.base}/donations/campaigns`, payload);
  }

  toggle(id: number) {
    return this.http.patch<{ is_active: boolean }>(`${this.base}/donations/campaigns/${id}/toggle`, {});
  }

  delete(id: number) {
    return this.http.delete<void>(`${this.base}/donations/campaigns/${id}`);
  }
}
