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
  DropInJson,
  DropIn,
  parseDropInJson,
  DocumentSection,
  DocumentDetails
} from './advising.model';

@Injectable({
  providedIn: 'root'
})
export class AdvisingService {
  private isUserAuthenticated = new BehaviorSubject<boolean>(false);
  private advisingEventsPaginator: TimeRangePaginator<DropIn> =
    new TimeRangePaginator<DropIn>('/api/drop-ins/paginate');

  constructor(private http: HttpClient) {}

  toggleAuthenticationStatus(): void {
    this.isUserAuthenticated.next(!this.isUserAuthenticated.value);
  }

  getEvents(
    params: TimeRangePaginationParams = DEFAULT_TIME_RANGE_PARAMS,
    authenticated: boolean
  ): Observable<Paginated<DropIn, TimeRangePaginationParams>> {
    if (authenticated) {
      return this.advisingEventsPaginator.loadPage(params, parseDropInJson);
    } else {
      return of({
        items: [],
        params,
        length: 0,
        message: 'User is not authenticated. Please log in to view events.'
      });
    }
  }

  /**Gets document sections based on the search query */
  search(search_query: string): Observable<DocumentSection[]> {
    return this.http.get<DocumentSection[]>(
      'api/documents/search/' + encodeURIComponent(search_query)
    );
  }

  /**Gets document details based on the document id */
  getDocumentById(id: number): Observable<DocumentDetails> {
    return this.http.get<DocumentDetails>('/api/documents/' + id);
  }

  /**
   * Gets an event based on its id.
   * @param id: ID for the event.
   * @returns {Observable<Event | undefined>}
   */
  getEvent(id: number): Observable<DropIn | undefined> {
    return this.http
      .get<DropInJson>('/api/drop-ins/' + id)
      .pipe(map((eventJson) => parseDropInJson(eventJson)));
  }
}
