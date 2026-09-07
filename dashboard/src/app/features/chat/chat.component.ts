import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ChatService } from '../../core/services/chat.service';

interface Message {
  role: 'user' | 'bot';
  text: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule, MatCardModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss',
})
export class ChatComponent {
  private chatService = inject(ChatService);

  question = signal('');
  loading = signal(false);
  messages = signal<Message[]>([
    {
      role: 'bot',
      text: 'Salaam! Pose ta question en poular ou en français. Exemple : "Munyal" ou "2:255".',
    },
  ]);

  canSend = computed(() => this.question().trim().length > 0 && !this.loading());

  send(): void {
    const q = this.question().trim();
    if (!q || this.loading()) return;

    this.messages.update((items) => [...items, { role: 'user', text: q }]);
    this.question.set('');
    this.loading.set(true);

    this.chatService.askQuran(q).subscribe({
      next: (response) => {
        const answer = response.answer || 'Je n’ai pas trouvé de réponse fiable pour cette demande.';
        this.messages.update((items) => [...items, { role: 'bot', text: answer }]);
      },
      error: () => {
        this.messages.update((items) => [
          ...items,
          { role: 'bot', text: '❌ Une erreur est survenue. Vérifie ta question et réessaie.' },
        ]);
      },
      complete: () => this.loading.set(false),
    });
  }

  onKeydown(event: any): void {
    const isModifierPressed = event.shiftKey || event.metaKey || event.ctrlKey;
    if (!isModifierPressed) {
      event.preventDefault();
      this.send();
    }
  }
}
