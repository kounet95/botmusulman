import { Component, OnDestroy, OnInit, inject, signal, computed } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import * as QRCode from 'qrcode';

import { PrayerTimesService } from '../../core/services/prayer-times.service';
import { ActivitiesService } from '../../core/services/activities.service';
import { ContentService } from '../../core/services/content.service';
import { AnnouncementsService } from '../../core/services/announcements.service';
import { DonationsService } from '../../core/services/donations.service';
import { AuthService } from '../../core/services/auth.service';
import { environment } from '../../../environments/environment';
import {
  Activity,
  Announcement,
  ContentItem,
  DonationCampaign,
  PRAYER_NAMES,
  PrayerName,
  PrayerTimes,
} from '../../core/models/models';

type IqamaMode = 'absolute' | 'offset';

interface PrayerRow {
  name: PrayerName;
  label: string;
  icon: string;
  time: string;
  iqamaLabel: string;
  isNext: boolean;
}

interface TickerCard {
  badge: string;
  title?: string;
  body: string;
  source?: string;
}

const PRAYER_LABELS: Record<PrayerName, string> = {
  Fajr: 'Fajr',
  Dhuhr: 'Dhuhr',
  Asr: 'Asr',
  Maghrib: 'Maghrib',
  Isha: 'Isha',
};

const PRAYER_ICONS: Record<PrayerName, string> = {
  Fajr: 'dark_mode',
  Dhuhr: 'light_mode',
  Asr: 'wb_twilight',
  Maghrib: 'wb_twilight',
  Isha: 'bedtime',
};

// Fajr et Dhuhr ont une Iqama à heure fixe (repère pratique pour les fidèles),
// les autres prières suivent un délai après l'Adhan — convention courante, non configurable pour l'instant.
const IQAMA_OFFSET_MIN: Record<PrayerName, number> = {
  Fajr: 20,
  Dhuhr: 10,
  Asr: 10,
  Maghrib: 5,
  Isha: 10,
};

const IQAMA_MODE: Record<PrayerName, IqamaMode> = {
  Fajr: 'absolute',
  Dhuhr: 'absolute',
  Asr: 'offset',
  Maghrib: 'offset',
  Isha: 'offset',
};

const CONTENT_LABELS: Record<string, string> = {
  hadith: '📖 Hadith',
  verset: '✨ Verset coranique',
  rappel: '💡 Rappel',
  dua: '🤲 Dua',
};

function pad2(n: number): string {
  return String(n).padStart(2, '0');
}

function parseTimeToday(time: string, now: Date): Date {
  const [h, m] = time.split(':').map(Number);
  const d = new Date(now);
  d.setHours(h, m, 0, 0);
  return d;
}

function formatTimePlusMinutes(time: string, minutes: number): string {
  const [h, m] = time.split(':').map(Number);
  const total = h * 60 + m + minutes;
  const hh = Math.floor(((total % 1440) + 1440) % 1440 / 60);
  const mm = ((total % 60) + 60) % 60;
  return `${pad2(hh)}:${pad2(mm)}`;
}

@Component({
  selector: 'app-screen',
  standalone: true,
  imports: [MatIconModule, MatProgressBarModule],
  templateUrl: './screen.component.html',
  styleUrl: './screen.component.scss',
})
export class ScreenComponent implements OnInit, OnDestroy {
  private prayerTimesService = inject(PrayerTimesService);
  private activitiesService = inject(ActivitiesService);
  private contentService = inject(ContentService);
  private announcementsService = inject(AnnouncementsService);
  private donationsService = inject(DonationsService);
  private authService = inject(AuthService);

  readonly mosque = this.authService.mosque;

  now = signal(new Date());
  prayerTimes = signal<PrayerTimes | null>(null);
  activities = signal<Activity[]>([]);
  donations = signal<DonationCampaign[]>([]);
  tickerCards = signal<TickerCard[]>([]);
  tickerIndex = signal(0);
  qrDataUrl = signal<string | null>(null);

  private clockTimer?: ReturnType<typeof setInterval>;
  private tickerTimer?: ReturnType<typeof setInterval>;
  private prayerRefreshTimer?: ReturnType<typeof setInterval>;
  private dataRefreshTimer?: ReturnType<typeof setInterval>;

  readonly prayerRows = computed<PrayerRow[]>(() => {
    const pt = this.prayerTimes();
    if (!pt) return [];
    return PRAYER_NAMES.map((name) => {
      const time = pt.timings[name];
      const offset = IQAMA_OFFSET_MIN[name];
      const iqamaLabel =
        IQAMA_MODE[name] === 'absolute' ? formatTimePlusMinutes(time, offset) : `+${offset}`;
      return {
        name,
        label: PRAYER_LABELS[name],
        icon: PRAYER_ICONS[name],
        time,
        iqamaLabel,
        isNext: pt.next_prayer.name === name,
      };
    });
  });

  readonly nextPrayerLabel = computed(() => {
    const pt = this.prayerTimes();
    return pt ? PRAYER_LABELS[pt.next_prayer.name] : '';
  });

  private readonly countdownSeconds = computed(() => {
    const pt = this.prayerTimes();
    if (!pt) return 0;
    const now = this.now();
    let target = parseTimeToday(pt.next_prayer.time, now);
    if (target <= now) target = new Date(target.getTime() + 24 * 60 * 60 * 1000);
    return Math.max(0, Math.floor((target.getTime() - now.getTime()) / 1000));
  });

  readonly countdownShort = computed(() => {
    const total = this.countdownSeconds();
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    return `${pad2(h)}:${pad2(m)}`;
  });

  readonly clockText = computed(() => {
    const n = this.now();
    return `${pad2(n.getHours())}:${pad2(n.getMinutes())}:${pad2(n.getSeconds())}`;
  });

  readonly activeDonations = computed(() => this.donations().filter((d) => d.is_active).slice(0, 2));
  readonly upcomingActivities = computed(() => this.activities().slice(0, 3));
  readonly currentTicker = computed(() => this.tickerCards()[this.tickerIndex()] ?? null);

  ngOnInit(): void {
    this.loadPrayerTimes();
    this.loadContentAndDonations();
    this.generateQr();

    this.clockTimer = setInterval(() => this.now.set(new Date()), 1000);
    this.tickerTimer = setInterval(() => {
      const cards = this.tickerCards();
      if (cards.length) this.tickerIndex.set((this.tickerIndex() + 1) % cards.length);
    }, 8000);
    this.prayerRefreshTimer = setInterval(() => this.loadPrayerTimes(), 60 * 60 * 1000);
    this.dataRefreshTimer = setInterval(() => this.loadContentAndDonations(), 5 * 60 * 1000);
  }

  ngOnDestroy(): void {
    clearInterval(this.clockTimer);
    clearInterval(this.tickerTimer);
    clearInterval(this.prayerRefreshTimer);
    clearInterval(this.dataRefreshTimer);
  }

  private loadPrayerTimes(): void {
    this.prayerTimesService.get().subscribe((pt) => this.prayerTimes.set(pt));
  }

  private loadContentAndDonations(): void {
    this.activitiesService.list().subscribe((activities) => this.activities.set(activities));
    this.donationsService.list().subscribe((donations) => this.donations.set(donations));

    this.contentService.list().subscribe((items: ContentItem[]) => {
      this.announcementsService.list().subscribe((announcements: Announcement[]) => {
        const contentCards: TickerCard[] = items.slice(0, 6).map((c) => ({
          badge: CONTENT_LABELS[c.type] || c.type,
          body: c.content_fr || c.content_ar || '',
          source: c.source || undefined,
        }));
        const announcementCards: TickerCard[] = announcements.slice(0, 4).map((a) => ({
          badge: '📢 Annonce',
          title: a.title,
          body: a.body,
        }));
        this.tickerCards.set([...announcementCards, ...contentCards]);
        this.tickerIndex.set(0);
      });
    });
  }

  private generateQr(): void {
    const link = this.authService.botLink(environment.botUsername);
    if (!link) return;
    QRCode.toDataURL(link, { width: 200, margin: 1, color: { dark: '#1c1c1c', light: '#ffffff' } })
      .then((url) => this.qrDataUrl.set(url))
      .catch(() => this.qrDataUrl.set(null));
  }
}
