import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AdvisingService } from '../advising.service';
import { DocumentSection, DocumentDetails } from '../advising.model';
import { MarkdownDirective } from 'src/app/shared/directives/markdown.directive';

@Component({
  selector: 'app-advising-search',
  templateUrl: './advising-search.component.html',
  styleUrl: './advising-search.component.css'
})
export class AdvisingSearchComponent implements OnInit {
  public query: string = '';
  public searchBarQuery: string = '';

  // for adding full text search results
  public searchResults: any[] = [];
  documentDetailsMap: { [key: number]: DocumentDetails } = {};

  constructor(
    private route: ActivatedRoute,
    protected router: Router,
    public advisingService: AdvisingService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.query = params['query'];
      this.searchBarQuery = this.query;
      console.log('Search query:', this.query);
      this.performSearch(this.query);
    });
  }

  performSearch(query: string): void {
    this.advisingService.search(query).subscribe((results) => {
      this.searchResults = results;
      const documentIds = [
        ...new Set(results.map((result) => result.document_id))
      ];
      documentIds.forEach((documentId) => {
        this.advisingService
          .getDocumentById(documentId)
          .subscribe((details) => {
            this.documentDetailsMap[documentId] = details;
          });
      });
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
