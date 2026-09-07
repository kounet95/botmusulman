import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

export interface QuranChatResponse {
  answer: string;
  results: Array<{
    sourate: number;
    verset: number;
    sourate_nom: string;
    arabe: string;
    traduction: string;
  }>;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private http = inject(HttpClient);
  private base = environment.apiBase;

  askQuran(question: string) {
    return this.http.post<QuranChatResponse>(`${this.base}/chat/quran`, { question });
  }
}
