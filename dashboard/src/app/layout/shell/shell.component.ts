import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink, RouterLinkActive, RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { BreakpointObserver, Breakpoints } from '@angular/cdk/layout';
import { map, shareReplay, filter } from 'rxjs/operators';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';
import { environment } from '../../../environments/environment';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

interface NavSection {
  label: string;
  items: NavItem[];
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterLink,
    RouterLinkActive,
    RouterOutlet,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatMenuModule,
  ],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss',
})
export class ShellComponent {
  private breakpointObserver = inject(BreakpointObserver);
  private router = inject(Router);
  private authService = inject(AuthService);
  private notifications = inject(NotificationService);

  readonly mosque = this.authService.mosque;

  readonly navSections: NavSection[] = [
    {
      label: 'Principal',
      items: [
        { path: 'dashboard', label: 'Tableau de bord', icon: 'dashboard' },
        { path: 'activities', label: 'Activités & Cours', icon: 'event' },
        { path: 'members', label: 'Membres', icon: 'groups' },
      ],
    },
    {
      label: 'Communication',
      items: [
        { path: 'content', label: 'Contenu programmé', icon: 'menu_book' },
        { path: 'announcements', label: 'Annonces', icon: 'campaign' },
      ],
    },
    {
      label: 'Finance',
      items: [{ path: 'donations', label: 'Dons & Collectes', icon: 'volunteer_activism' }],
    },
  ];

  readonly isHandset$ = this.breakpointObserver.observe(Breakpoints.Handset).pipe(
    map((result) => result.matches),
    shareReplay(1)
  );

  readonly isHandset = toSignal(this.isHandset$, { initialValue: false });

  pageTitle = 'Tableau de bord';

  constructor() {
    this.router.events.pipe(filter((e) => e instanceof NavigationEnd)).subscribe(() => {
      let route = this.router.routerState.snapshot.root;
      while (route.firstChild) route = route.firstChild;
      this.pageTitle = (route.title as string) || 'Tableau de bord';
    });
  }

  copyBotLink(): void {
    const link = this.authService.botLink(environment.botUsername);
    if (!link) return;
    navigator.clipboard.writeText(link);
    this.notifications.success('Lien du bot copié !');
  }

  openScreen(): void {
    window.open('/screen', '_blank');
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
