import { Component, Input } from '@angular/core';
import { DropInOverview } from 'src/app/advising/advising.model';
import { AdvisingService } from 'src/app/advising/advising.service';

@Component({
  selector: 'drop-in-registration-card',
  templateUrl: './drop-in-registration-card.widget.html',
  styleUrl: './drop-in-registration-card.widget.css'
})
export class DropInRegistrationCardWidget {
  @Input() event!: DropInOverview;

  constructor(protected advisingService: AdvisingService) {}
}
