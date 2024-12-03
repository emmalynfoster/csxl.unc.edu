import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { AdvisingService } from './advising.service';
import { DropInOverview } from './advising.model';

export const advisingResolver: ResolveFn<DropInOverview | undefined> = (
  route,
  state
) => {
  if (route.paramMap.get('id') != 'new') {
    return inject(AdvisingService).getEvent(+route.paramMap.get('id')!);
  } else {
    return {
      id: null,
      name: '',
      start: new Date(),
      end: new Date(),
      location: '',
      description: '',
      public: true,
      number_registered: 0,
      registration_limit: 0,
      advisor_id: 0,
      advisor_slug: '',
      advisor_name: '',
      organizers: [],
      image_url: null,
      user_registration_type: null,
      override_registration_url: null
    };
  }
};
