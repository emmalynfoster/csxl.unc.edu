import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvisingEventsComponent } from './advising-events.component';

describe('AdvisingEventsComponent', () => {
  let component: AdvisingEventsComponent;
  let fixture: ComponentFixture<AdvisingEventsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdvisingEventsComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(AdvisingEventsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
