import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { Profile } from '../models.module';
import {
  DEFAULT_TIME_RANGE_PARAMS,
  Paginated,
  PaginationParams,
  Paginator,
  TimeRangePaginationParams,
  TimeRangePaginator
} from '../pagination';
import {
  DropInOverview,
  DropInRegistration,
  DropInOverviewJson,
  DropInStatusOverview,
  DropInStatusOverviewJson,
  parseDropInOverviewJson,
  parseDropInStatusOverviewJson,
  AdvisingEventDraft
  // AdvisingDocument,
  // AdvisingEvent,
  // AdvisingSearchResult,
  // parseAdvisingDocumentJSON,
  // parseAdvisingEventJSON,
  // parseAdvisingSearchResultJSON
} from './advising.model';
// import { environment } from '../environments/environment'; // Assuming API URLs are stored here

const MOCK_USERS: Profile[] = [
  {
    id: 1,
    pid: 1001,
    onyen: 'asmith',
    first_name: 'Alice',
    last_name: 'Smith',
    email: 'alice.smith@example.com',
    pronouns: 'she/her',
    registered: true,
    role: 2,
    permissions: [], // Example permissions
    github: 'https://github.com/asmith',
    github_id: 101,
    github_avatar: 'https://avatars.githubusercontent.com/u/101?v=4',
    accepted_community_agreement: true,
    bio: 'Software developer with a passion for education.',
    linkedin: 'https://linkedin.com/in/asmith',
    website: 'https://alice.dev'
  },
  {
    id: 2,
    pid: 1002,
    onyen: 'bjohnson',
    first_name: 'Bob',
    last_name: 'Johnson',
    email: 'bob.johnson@example.com',
    pronouns: 'he/him',
    registered: true,
    role: 1,
    permissions: [],
    github: 'https://github.com/bjohnson',
    github_id: 102,
    github_avatar: 'https://avatars.githubusercontent.com/u/102?v=4',
    accepted_community_agreement: true,
    bio: 'Tech enthusiast and open-source contributor.',
    linkedin: 'https://linkedin.com/in/bjohnson',
    website: null
  },
  {
    id: 3,
    pid: 1003,
    onyen: 'cbrown',
    first_name: 'Charlie',
    last_name: 'Brown',
    email: 'charlie.brown@example.com',
    pronouns: 'they/them',
    registered: false,
    role: 3,
    permissions: [],
    github: 'https://github.com/cbrown',
    github_id: 103,
    github_avatar: 'https://avatars.githubusercontent.com/u/103?v=4',
    accepted_community_agreement: false,
    bio: 'Community manager and avid writer.',
    linkedin: 'https://linkedin.com/in/cbrown',
    website: 'https://charliebrown.dev'
  },
  {
    id: 4,
    pid: 1004,
    onyen: 'dlee',
    first_name: 'Dana',
    last_name: 'Lee',
    email: 'dana.lee@example.com',
    pronouns: null,
    registered: true,
    role: 1,
    permissions: [],
    github: null,
    github_id: null,
    github_avatar: null,
    accepted_community_agreement: true,
    bio: 'New member exploring software development.',
    linkedin: null,
    website: null
  },
  {
    id: 5,
    pid: 1005,
    onyen: 'ewilliams',
    first_name: 'Elliot',
    last_name: 'Williams',
    email: 'elliot.williams@example.com',
    pronouns: 'he/him',
    registered: false,
    role: 2,
    permissions: [],
    github: 'https://github.com/ewilliams',
    github_id: 105,
    github_avatar: 'https://avatars.githubusercontent.com/u/105?v=4',
    accepted_community_agreement: true,
    bio: 'UX designer turned developer.',
    linkedin: 'https://linkedin.com/in/ewilliams',
    website: 'https://elliotwilliams.dev'
  }
];

class MockPaginator<T> {
  constructor(private data: T[]) {}

  loadPage(params: PaginationParams): Paginated<T, PaginationParams> {
    const { page, size } = params;
    const startIndex = (page - 1) * size;
    const endIndex = startIndex + size;

    return {
      items: this.data.slice(startIndex, endIndex),
      length: this.data.length,
      params
    };
  }
}

export interface EventRegistration {
  eventId: number;
  userId: number;
  registrationDate: string;
  status: string; // Example: "confirmed", "pending", etc.
}

@Injectable({
  providedIn: 'root'
})
export class AdvisingService {
  // Some examples I was trying to test:
  // private docsFolderId = environment.googleDocsFolderId; // ID for Google Docs folder
  // private calendarId = environment.googleCalendarId; // Calendar ID for advising events

  private isUserAuthenticated = new BehaviorSubject<boolean>(false);
  private advisingEventsPaginator: TimeRangePaginator<DropInOverview> =
    new TimeRangePaginator<DropInOverview>('/api/events/paginate');
  private unauthenticatedEventsPaginator: TimeRangePaginator<DropInOverview> =
    new TimeRangePaginator<DropInOverview>(
      '/api/events/unauthenticated/paginate'
    );

  constructor(private http: HttpClient) {}

  getRegisteredUsersForEvent(
    event: DropInOverview,
    params: PaginationParams
  ): Observable<Paginated<Profile, PaginationParams>> {
    const paginator: MockPaginator<Profile> = new MockPaginator<Profile>(
      MOCK_USERS
    );
    return of(paginator.loadPage(params)); // Use `of` to simulate an Observable
  }

  registerForEvent(eventId: number): Observable<EventRegistration> {
    // Simulated user ID and registration details
    const mockResponse: EventRegistration = {
      eventId,
      userId: 123, // Mocked user ID
      registrationDate: new Date().toISOString(), // Current date-time as ISO string
      status: 'confirmed' // Example registration status
    };

    // Return the mock response as an observable
    return of(mockResponse);
  }
  unregisterForEvent(eventId: number): Observable<EventRegistration> {
    // Simulated response for unregistering
    const mockResponse: EventRegistration = {
      eventId,
      userId: 123, // Mocked user ID
      registrationDate: new Date().toISOString(), // Date of original registration
      status: 'unregistered' // Updated status to indicate unregistration
    };

    // Return the mock response as an observable
    return of(mockResponse);
  }

  // // Full-text search in advising documents
  // searchDocuments(query: string): Observable<AdvisingSearchResult[]> {
  //   return this.http
  //     .get<
  //       AdvisingSearchResult[]
  //     >(`/api/advising/search?query=${encodeURIComponent(query)}`)
  //     .pipe(map((results) => results.map(parseAdvisingSearchResultJSON)));
  // }

  // // Retrieves drop-in events from Google Calendar for the current week
  // getDropInEvents(weekOffset: number = 0): Observable<AdvisingEvent[]> {
  //   return this.http
  //     .get<
  //       AdvisingEvent[]
  //     >(`/api/advising/calendar?calendarId=${this.calendarId}&weekOffset=${weekOffset}`)
  //     .pipe(map((events) => events.map(parseAdvisingEventJSON)));
  // }

  // // Retrieves advising document by ID, if we want viewing individual documents
  // getDocumentById(docId: string): Observable<AdvisingDocument> {
  //   return this.http
  //     .get<AdvisingDocument>(`/api/advising/documents/${docId}`)
  //     .pipe(map(parseAdvisingDocumentJSON));
  // }

  // Toggle user authentication status
  toggleAuthenticationStatus(): void {
    this.isUserAuthenticated.next(!this.isUserAuthenticated.value);
  }
  getEvents(
    params: TimeRangePaginationParams = DEFAULT_TIME_RANGE_PARAMS,
    authenticated: boolean
  ) {
    if (authenticated) {
      return this.advisingEventsPaginator.loadPage(
        params,
        parseDropInOverviewJson
      );
    } else {
      return this.unauthenticatedEventsPaginator.loadPage(
        params,
        parseDropInOverviewJson
      );
    }
  }

  /**
   * Here im thinking we create an id for every google calendar event
   * and then get the event based on its id
   *
   * Gets an event based on its id.
   * @param id: ID for the event.
   * @returns {Observable<Event | undefined>}
   */
  getEvent(id: number): Observable<DropInOverview | undefined> {
    return this.http
      .get<DropInOverviewJson>('/api/events/' + id)
      .pipe(map((eventJson) => parseDropInOverviewJson(eventJson)));
  }

  getEventStatus(authenticated: boolean): Observable<DropInStatusOverview> {
    return this.http
      .get<DropInStatusOverviewJson>(
        `/api/events/${!authenticated ? 'unauthenticated/' : ''}status`
      )
      .pipe(map(parseDropInStatusOverviewJson));
  }
}
