import { Routes } from '@angular/router';
import { ShellComponent } from './layout/shell/shell.component';
import { authGuard } from './core/guards/auth.guard';
import { onboardingGuard } from './core/guards/onboarding.guard';

export const routes: Routes = [
  {
    path: 'login',
    title: 'Connexion',
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'signup',
    title: 'Créer une mosquée',
    loadComponent: () => import('./features/auth/signup/signup.component').then((m) => m.SignupComponent),
  },
  {
    path: 'screen',
    title: "Écran d'affichage",
    canActivate: [authGuard],
    loadComponent: () => import('./features/screen/screen.component').then((m) => m.ScreenComponent),
  },
  {
    path: 'onboarding',
    title: 'Compléter votre profil',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/onboarding/onboarding.component').then((m) => m.OnboardingComponent),
  },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard, onboardingGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        title: 'Tableau de bord',
        loadComponent: () =>
          import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
      },
      {
        path: 'activities',
        title: 'Activités & Cours',
        loadComponent: () =>
          import('./features/activities/activities.component').then((m) => m.ActivitiesComponent),
      },
      {
        path: 'members',
        title: 'Membres',
        loadComponent: () =>
          import('./features/members/members.component').then((m) => m.MembersComponent),
      },
      {
        path: 'content',
        title: 'Contenu programmé',
        loadComponent: () =>
          import('./features/content/content.component').then((m) => m.ContentComponent),
      },
      {
        path: 'donations',
        title: 'Dons & Collectes',
        loadComponent: () =>
          import('./features/donations/donations.component').then((m) => m.DonationsComponent),
      },
      {
        path: 'announcements',
        title: 'Annonces',
        loadComponent: () =>
          import('./features/announcements/announcements.component').then(
            (m) => m.AnnouncementsComponent
          ),
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
