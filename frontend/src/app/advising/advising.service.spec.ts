import { TestBed } from '@angular/core/testing';

import { AdvisingService } from './advising.service';

describe('AdvisingService', () => {
  let service: AdvisingService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AdvisingService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
