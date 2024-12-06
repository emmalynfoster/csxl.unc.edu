import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { AdvisingService } from './advising.service';
import { DropIn } from './advising.model';

export const advisingResolver: ResolveFn<DropIn | undefined> = (
  route,
  state
) => {
  if (route.paramMap.get('id') != 'new') {
    return inject(AdvisingService).getEvent(+route.paramMap.get('id')!);
  } else {
    return {
      id: null,
      title: '',
      start: new Date(),
      end: new Date(),
      link: '',
    };
  }
};
