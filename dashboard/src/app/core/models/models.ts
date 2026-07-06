export type ActivityType = 'cours' | 'conference' | 'halaqa' | 'evenement' | 'autre';

export interface Activity {
  id: number;
  mosque_id: number;
  title: string;
  description: string | null;
  type: ActivityType;
  date: string;
  time: string;
  capacity: number;
  registered_count: number;
  is_paid: boolean;
  price: number | null;
  speaker: string | null;
  location: string | null;
  livestream_url: string | null;
  created_at: string;
}

export interface ActivityPayload {
  title: string;
  description?: string | null;
  type: ActivityType;
  date: string;
  time: string;
  capacity: number;
  is_paid: boolean;
  price?: number | null;
  speaker?: string | null;
  location?: string | null;
  livestream_url?: string | null;
}

export interface RecentActivity {
  id: number;
  title: string;
  date: string;
  time: string;
  registered_count: number;
  capacity: number;
  type: ActivityType;
}

export interface Member {
  id: number;
  mosque_id: number;
  telegram_id: string;
  first_name: string;
  username: string | null;
  joined_at: string;
  prayer_times?: boolean;
  jumua?: boolean;
  courses?: boolean;
  conferences?: boolean;
  announcements?: boolean;
  hajj_umrah?: boolean;
}

export type ContentType = 'hadith' | 'verset' | 'rappel' | 'dua';

export interface ContentItem {
  id: number;
  mosque_id: number;
  type: ContentType;
  content_ar: string | null;
  content_fr: string | null;
  content_en: string | null;
  source: string | null;
  scheduled_date: string;
  sent_at: string | null;
  created_at: string;
}

export interface ContentPayload {
  type: ContentType;
  content_ar?: string | null;
  content_fr?: string | null;
  content_en?: string | null;
  source?: string | null;
  scheduled_date: string;
}

export interface ContentTemplate {
  content_ar?: string;
  content_fr?: string;
  source?: string;
  type?: ContentType;
}

export interface ContentTemplates {
  hadiths?: ContentTemplate[];
  versets?: ContentTemplate[];
}

export type DonationType = 'general' | 'projet' | 'zakat' | 'bourse';

export interface DonationCampaign {
  id: number;
  mosque_id: number;
  title: string;
  description: string | null;
  type: DonationType;
  goal_amount: number | null;
  collected_amount: number;
  payment_url: string | null;
  orange_money_number: string | null;
  mtn_momo_number: string | null;
  is_active: boolean;
  created_at: string;
}

export interface DonationCampaignPayload {
  title: string;
  description?: string | null;
  type: DonationType;
  goal_amount?: number | null;
  payment_url?: string | null;
  orange_money_number?: string | null;
  mtn_momo_number?: string | null;
}

export interface Announcement {
  id: number;
  mosque_id: number;
  title: string;
  body: string;
  sent_at: string | null;
  created_at: string;
}

export interface AnnouncementPayload {
  title: string;
  body: string;
  send_now: boolean;
}

export interface DashboardStats {
  total_members: number;
  activities_this_month: number;
  total_registrations: number;
  total_donations: number;
}

export interface Mosque {
  id: number;
  name: string;
  city: string;
  country: string;
  slug: string;
  onboarding_completed: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  mosque: Mosque;
}

export interface SignupPayload {
  mosque_name: string;
  city: string;
  country: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export const PRAYER_NAMES = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'] as const;
export type PrayerName = (typeof PRAYER_NAMES)[number];

export interface NextPrayer {
  name: PrayerName;
  time: string;
}

export interface Weather {
  temperature: number;
  icon: string;
  condition: string;
}

export interface WeatherAlert {
  message: string;
  expected_time: string;
}

export interface PrayerTimes {
  timings: Record<PrayerName, string>;
  sunrise: string | null;
  next_prayer: NextPrayer;
  gregorian_date: string;
  hijri_date: string;
  weather: Weather | null;
  weather_alert: WeatherAlert | null;
}

export type InstallationType = 'mosque' | 'ecole' | 'salle_priere' | 'domicile' | 'magasin';

export const INSTALLATION_TYPES: { value: InstallationType; label: string; icon: string }[] = [
  { value: 'mosque', label: 'Mosquée', icon: 'mosque' },
  { value: 'ecole', label: 'École', icon: 'school' },
  { value: 'salle_priere', label: 'Salle de prière', icon: 'self_improvement' },
  { value: 'domicile', label: 'Domicile', icon: 'home' },
  { value: 'magasin', label: 'Magasin', icon: 'storefront' },
];

export const AMENITIES: { key: string; label: string }[] = [
  { key: 'women_space', label: 'Espace pour femmes' },
  { key: 'ablution_room', label: "Salle d'ablutions" },
  { key: 'adult_courses', label: 'Cours pour adultes' },
  { key: 'kids_courses', label: 'Cours pour enfants' },
  { key: 'disabled_access', label: 'Accès handicapés' },
  { key: 'library', label: 'Bibliothèque' },
  { key: 'braille_quran', label: 'Coran pour les malvoyants' },
  { key: 'janaza_prayer', label: 'Salât al-Janaza' },
  { key: 'eid_prayer', label: "Salat Al-Aïd" },
  { key: 'ramadan_iftar', label: 'Iftar Ramadan' },
  { key: 'parking', label: 'Parking' },
  { key: 'bike_parking', label: 'Stationnement vélo' },
  { key: 'ev_charging', label: 'Recharge de voiture électrique' },
];

export interface MosqueProfile {
  id: number;
  name: string;
  city: string;
  country: string;
  slug: string;
  installation_type: InstallationType | null;
  address: string | null;
  postal_code: string | null;
  association_name: string | null;
  phone: string | null;
  email: string | null;
  website: string | null;
  payment_url: string | null;
  amenities: string[];
  construction_year: number | null;
  capacity_women: number | null;
  capacity_men: number | null;
  history: string | null;
  other_info: string | null;
  exterior_photo_url: string | null;
  interior_photo_url: string | null;
  logo_url: string | null;
  onboarding_completed: boolean;
}

export interface MosqueProfilePayload {
  installation_type?: InstallationType;
  name?: string;
  address?: string;
  city?: string;
  postal_code?: string;
  country?: string;
  association_name?: string | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  payment_url?: string | null;
  amenities?: string[];
  construction_year?: number | null;
  capacity_women?: number | null;
  capacity_men?: number | null;
  history?: string | null;
  other_info?: string | null;
}

export type PhotoKind = 'exterior' | 'interior' | 'logo';
