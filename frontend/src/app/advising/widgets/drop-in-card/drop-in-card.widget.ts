/**
 * @author Ife Babarinde, Emmalyn Foster
 */

import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DropIn } from '../../advising.model';
import { AdvisingService } from '../../advising.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Profile } from 'src/app/models.module';

@Component({
  selector: 'new-drop-in-card',
  templateUrl: './drop-in-card.widget.html',
  styleUrl: './drop-in-card.widget.css'
})
export class DropInCardWidget {
  @Input() profile: Profile | undefined;
  @Input() event!: DropIn;
  now = new Date();
  constructor(
    protected advisingService: AdvisingService,
    protected snackBar: MatSnackBar
  ) {}

  openLink(url: string): void {
    window.open(url, '_blank');
  }
}
