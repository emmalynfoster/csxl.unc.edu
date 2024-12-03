import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-advising-search',
  standalone: true,
  imports: [],
  templateUrl: './advising-search.component.html',
  styleUrl: './advising-search.component.css'
})
export class AdvisingSearchComponent implements OnInit {
  public query: string = '';

  constructor(private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe((params) => {
      this.query = params['query'];
      // Perform search logic here using the query
      console.log('Search query:', this.query);
    });
  }
}
