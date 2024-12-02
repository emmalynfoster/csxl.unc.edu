import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DropInOverview, RegistrationType } from '../../advising.model';
import { AdvisingService } from '../../advising.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Profile } from 'src/app/profile/profile.service';

@Component({
  selector: 'drop-in-card',
  templateUrl: './drop-in-card.widget.html',
  styleUrl: './drop-in-card.widget.css'
})
export class DropInCardWidget {
  @Input() profile: Profile | undefined;
  registrationType = RegistrationType;
  @Input() event!: DropInOverview;
  @Output() registrationChange = new EventEmitter<boolean>();

  now = new Date();

  constructor(
    protected advisingService: AdvisingService,
    protected snackBar: MatSnackBar
  ) {}

  /** Registers a user for an event. */
  registerForEvent() {
    if (this.event.override_registration_url) {
      window.location.href = this.event.override_registration_url!;
      return;
    }

    this.advisingService.registerForEvent(this.event.id!).subscribe({
      next: () => {
        this.registrationChange.emit(true);
        this.snackBar.open(
          `Successfully registered for ${this.event.name}!`,
          'Close',
          { duration: 15000 }
        );
      },
      error: () => {
        this.snackBar.open(
          `Error: Could not register. Please try again.`,
          'Close',
          { duration: 15000 }
        );
      }
    });
  }

  /** Unregisters a user from an evenet. */
  unregisterForEvent() {
    this.advisingService.unregisterForEvent(this.event.id!).subscribe({
      next: () => {
        this.registrationChange.emit(true);
        this.snackBar.open(
          `Successfully unregistered for ${this.event.name}!`,
          'Close',
          { duration: 15000 }
        );
      },
      error: () => {
        this.snackBar.open(
          `Error: Could not unregister. Please try again.`,
          'Close',
          { duration: 15000 }
        );
      }
    });
  }
}
