/**
 * @author Emmalyn Foster
 */

import {
    Component,
    Signal,
    signal,
    effect,
    WritableSignal,
    computed
  } from '@angular/core';
  
  import { ActivatedRoute, Router } from '@angular/router';
  import { Profile, ProfileService } from 'src/app/profile/profile.service';
  import { DatePipe } from '@angular/common';
  
  import {
    DEFAULT_TIME_RANGE_PARAMS,
    Paginated,
    TimeRangePaginationParams
  } from 'src/app/pagination';

  import { profileResolver } from 'src/app/profile/profile.resolver';
  
  @Component({
    selector: 'app-advising-page',
    templateUrl: './advising-page.component.html',
    styleUrl: './advising-page.component.css'
  })
  export class AdvisingPageComponent {
    /** Route information to be used in App Routing Module */
    public static Route = {
      path: '',
      title: 'Advising',
      component: AdvisingPageComponent,
      canActivate: [],
      resolve: {
        profile: profileResolver
      }
    };
}