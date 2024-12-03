import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-advising-search',
  templateUrl: './advising-search.component.html',
  styleUrl: './advising-search.component.css'
})
export class AdvisingSearchComponent implements OnInit {
  public query: string = '';
  public searchBarQuery: string = '';

  // for adding full text search results
  public searchResults: any;

  constructor(
    private route: ActivatedRoute,
    protected router: Router
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.query = params['query'];
      this.searchBarQuery = this.query;
      // Perform search logic here using the query
      console.log('Search query:', this.query);
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
}
