import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvisingSearchComponent } from './advising-search.component';

describe('AdvisingSearchComponent', () => {
  let component: AdvisingSearchComponent;
  let fixture: ComponentFixture<AdvisingSearchComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdvisingSearchComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdvisingSearchComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
