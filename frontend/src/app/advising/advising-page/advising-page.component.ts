/**
 * @author Emmalyn Foster, Ife Babarinde
 */

import {
  Component,
  OnInit,
  WritableSignal,
  Signal,
  signal,
  effect,
  computed
} from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';
import { Profile, ProfileService } from 'src/app/profile/profile.service';
import { DropIn } from '../advising.model';
import { DatePipe } from '@angular/common';

import {
  DEFAULT_TIME_RANGE_PARAMS,
  Paginated,
  TimeRangePaginationParams
} from 'src/app/pagination';

import { AdvisingService } from 'src/app/advising/advising.service';
import { GroupAdvisingEventsPipe } from '../pipes/group-advising-events.pipe';
import { profileResolver } from 'src/app/profile/profile.resolver';

@Component({
  selector: 'app-advising-page',
  templateUrl: './advising-page.component.html',
  styleUrls: ['./advising-page.component.css']
})
export class AdvisingPageComponent {
  public static Route = {
    path: '',
    title: 'Advising',
    component: AdvisingPageComponent,
    canActivate: [],
    resolve: {
      profile: profileResolver
    }
  };

  /** Stores a reactive event pagination page. */
  public page: WritableSignal<
    Paginated<DropIn, TimeRangePaginationParams> | undefined
  > = signal(undefined);
  private previousParams: TimeRangePaginationParams = DEFAULT_TIME_RANGE_PARAMS;

  // Cant add until we have events appearing
  /** Stores a reactive mapping of days to events on the active page. */
  protected eventsByDate: Signal<[string, DropIn[]][]> = computed(
  () => {
    return this.groupAdvisingEventsPipe.transform(this.page()?.items ?? []);
     }
  );

  /** Stores reactive date signals for the bounds of pagination. */
  public startDate: WritableSignal<Date> = signal(new Date());
  public endDate: WritableSignal<Date> = signal(
    new Date(new Date().setDate(new Date().getDate() + 7))
  );
  public filterQuery: WritableSignal<string> = signal('');

  /** Store the content of the search bar */
  public searchBarQuery = '';

  /** Store the currently-logged-in user's profile.  */
  public profile: Profile | undefined;

  /** Constructor for the events page. */
  constructor(
    private route: ActivatedRoute,
    protected router: Router,
    public datePipe: DatePipe,
    public advisingService: AdvisingService,
    private profileService: ProfileService,
    // Cant add until you have events showing up
    protected groupAdvisingEventsPipe: GroupAdvisingEventsPipe
  ) {
    const data = this.route.snapshot.data as {
      profile: Profile | undefined;
    };
    this.profile = data.profile;
  }
  paginationTimeRangeEffect = effect(() => {
    // Update the parameters with the new date range
    let params = this.previousParams;
    params.range_start = this.startDate().toISOString();
    params.range_end = this.endDate().toISOString();
    params.filter = this.filterQuery();
    // Refresh the data
    this.advisingService
      .getEvents(params, this.profile !== undefined)
      .subscribe((events) => {
        this.page.set(events);
        this.previousParams = events.params;
        this.reloadQueryParams();
      });
  });

  /** Reloads the page and its query parameters to adjust to the next week. */
  nextPage() {
    this.startDate.set(
      new Date(this.startDate().setDate(this.startDate().getDate() + 7))
    );
    this.endDate.set(
      new Date(this.endDate().setDate(this.endDate().getDate() + 7))
    );
  }

  /** Reloads the page and its query parameters to adjust to the previous month. */
  previousPage() {
    this.startDate.set(
      new Date(this.startDate().setDate(this.startDate().getDate() - 7))
    );
    this.endDate.set(
      new Date(this.endDate().setDate(this.endDate().getDate() - 7))
    );
  }

  /** Reloads the data in the current page. */
  reloadPage() {
    this.advisingService
      .getEvents(this.previousParams, this.profile !== undefined)
      .subscribe((response) => {
        if ('message' in response) {
          console.warn(response.message); // Log or display the message as needed
        }
        this.page.set(response);
      });
  }
  

  /**
   * Reloads the page to update the query parameters and reload the data.
   * This is required so that the correct query parameters are reflected in the
   * browser's URL field.
   * @param startDate: The new start date
   * @param endDate: The new end date
   */
  reloadQueryParams() {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        start_date: this.startDate().toISOString(),
        end_date: this.endDate().toISOString()
      },
      queryParamsHandling: 'merge'
    });
  }

  /** Handler that runs when the search bar query changes.
   * @param query: Search bar query to filter the items
   */
  onSearch(event: Event) {
    console.log('Search triggered with query:', this.searchBarQuery);
    event.preventDefault();
    this.router.navigate(['/advising-search'], {
      queryParams: { query: this.searchBarQuery }
    });
  }

  /** Performs the redirection for the sign in button */
  signIn() {
    window.location.href = '/auth?continue_to=/advising';
  }
}
