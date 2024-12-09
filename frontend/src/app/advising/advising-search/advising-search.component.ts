/**
 * @author Ife Babarinde, Emmalyn Foster
 */

import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AdvisingService } from '../advising.service';
import { DocumentDetails } from '../advising.model';

@Component({
  selector: 'app-advising-search',
  templateUrl: './advising-search.component.html',
  styleUrl: './advising-search.component.css'
})
export class AdvisingSearchComponent implements OnInit {
  public query: string = '';
  public searchBarQuery: string = '';

  // Grouped search results
  public groupedResults: { [documentId: number]: any[] } = {};
  public documentDetailsMap: { [key: number]: DocumentDetails } = {};

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
      // group search results by document (if documents are added to the folder)
      this.groupedResults = results.reduce(
        (acc: { [key: number]: any[] }, result) => {
          const documentId = result.document_id;
          if (!acc[documentId]) {
            acc[documentId] = [];
          }
          acc[documentId].push(result);
          return acc;
        },
        {}
      );

      // Get each document by id to display title and link
      Object.keys(this.groupedResults).forEach((documentId) => {
        this.advisingService
          .getDocumentById(+documentId) // Convert key back to number
          .subscribe((details) => {
            this.documentDetailsMap[+documentId] = details;
          });
      });
    });
  }

  get groupedResultsKeys(): string[] {
    return Object.keys(this.groupedResults);
  }

  onSearch(event: Event): void {
    console.log('Search triggered with query:', this.searchBarQuery);
    event.preventDefault();
    this.router.navigate(['/advising-search'], {
      queryParams: { query: this.searchBarQuery }
    });
  }
}
