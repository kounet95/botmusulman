import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '../services/notification.service';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);

  return next(req).pipe(
    catchError((err) => {
      const message = err?.error?.detail || err?.message || 'Une erreur est survenue';
      notifications.error(message);
      return throwError(() => err);
    })
  );
};
