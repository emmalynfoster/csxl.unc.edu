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
import { DropInOverview, DropInStatusOverview } from '../advising.model';
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
    Paginated<DropInOverview, TimeRangePaginationParams> | undefined
  > = signal(undefined);
  private previousParams: TimeRangePaginationParams = DEFAULT_TIME_RANGE_PARAMS;

  // Cant add until we have events appearing
  /** Stores a reactive mapping of days to events on the active page. */
  // protected eventsByDate: Signal<[string, DropInOverview[]][]> = computed(
  //   () => {
  //     return this.groupAdvisingEventsPipe.transform(this.page()?.items ?? []);
  //   }
  // );

  /** Stores reactive date signals for the bounds of pagination. */
  public startDate: WritableSignal<Date> = signal(new Date());
  public endDate: WritableSignal<Date> = signal(
    new Date(new Date().setDate(new Date().getDate() + 7))
  );
  public filterQuery: WritableSignal<string> = signal('');

  /** Stores the event status in a reactive object. */
  public eventStatus: WritableSignal<DropInStatusOverview | undefined> =
    signal(undefined);

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
    private profileService: ProfileService
    // Cant add until you have events showing up
    // protected groupAdvisingEventsPipe: GroupAdvisingEventsPipe
  ) {
    const data = this.route.snapshot.data as {
      profile: Profile | undefined;
    };
    this.profile = data.profile;
    this.advisingService
      .getEventStatus(data.profile !== undefined)
      .subscribe((status) => {
        this.eventStatus.set(status);
      });
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
      .subscribe((events) => {
        this.page.set(events);
      });
    this.advisingService
      .getEventStatus(this.profile !== undefined)
      .subscribe((status) => {
        this.eventStatus.set(status);
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

// export class AdvisingPageComponent implements OnInit {
//   /** Properties */
//   public documents: WritableSignal<AdvisingDocument[]> = signal([]);
//   public events: WritableSignal<AdvisingEvent[]> = signal([]);
//   public searchResults: WritableSignal<AdvisingSearchResult[]> = signal([]);
//   public searchQuery: WritableSignal<string> = signal('');
//   public isAuthenticated: WritableSignal<boolean> = signal(false);
//   public userProfile: Signal<Profile | undefined> = signal(undefined);

//   /** Constructor */
//   constructor(
//     private advisingService: AdvisingService,
//     private profileService: ProfileService,
//     private route: ActivatedRoute,
//     private router: Router,
//     private datePipe: DatePipe
//   ) {}

//   ngOnInit(): void {
//     // Load user profile
//     this.profileService.getProfile().subscribe(
//       (profile) => {
//         this.userProfile.set(profile);
//         this.isAuthenticated.set(!!profile);
//       },
//       (error) => console.error('Error fetching profile:', error)
//     );

//     // Load initial documents and events
//     this.loadDocuments();
//     this.loadEvents();

//     // Respond to route parameter changes, if any
//     this.route.params.subscribe((params) => {
//       const documentId = params['documentId'];
//       if (documentId) {
//         this.loadDocumentDetails(documentId);
//       }
//     });
//   }

//   /** Load advising documents */
//   loadDocuments(): void {
//     this.advisingService.getAdvisingDocuments().subscribe(
//       (documents) => this.documents.set(documents),
//       (error) => console.error('Error loading documents:', error)
//     );
//   }

//   /** Load drop-in events for current week */
//   loadEvents(): void {
//     this.advisingService.getDropInEvents().subscribe(
//       (events) => this.events.set(events),
//       (error) => console.error('Error loading events:', error)
//     );
//   }

//   /** Search for advising documents */
//   searchDocuments(): void {
//     if (this.searchQuery()) {
//       this.advisingService.searchDocuments(this.searchQuery()).subscribe(
//         (results) => this.searchResults.set(results),
//         (error) => console.error('Error performing search:', error)
//       );
//     }
//   }

//   /** Handle search input change */
//   onSearchInputChange(query: string): void {
//     this.searchQuery.set(query);
//     this.searchDocuments();
//   }

//   /** Navigate to event registration page */
//   TODO: Implement advisor registration
//   goToAdvisorRegistration(eventId: number): void {
//     this.router.navigate(['/events', eventId, 'register']);
//   }

//   /** Load document details if navigated to with an ID */
//   loadDocumentDetails(documentId: string): void {
//     this.advisingService.getDocumentById(documentId).subscribe(
//       (document) => {
//         // Open document details modal or navigate to a document detail page
//         console.log('Document details:', document);
//       },
//       (error) => console.error('Error loading document details:', error)
//     );
//   }
// }
