/**
 * Advising Events component used
 * to show details on advising appointment
 *
 * @author Ife Babarinde
 * @copyright 2024
 * @license MIT
 */

import { Component, OnInit, WritableSignal, signal } from '@angular/core';
import { advisingResolver } from '../advising.resolver';
import { Profile, ProfileService } from 'src/app/profile/profile.service';
import {
  ActivatedRoute,
  ActivatedRouteSnapshot,
  ResolveFn
} from '@angular/router';
import { DropInOverview, RegistrationType } from '../advising.model';
import { Observable, of } from 'rxjs';
import { PermissionService } from 'src/app/permission.service';
import { NagivationAdminGearService } from 'src/app/navigation/navigation-admin-gear.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AdvisingService } from '../advising.service';
import { Paginated, PaginationParams } from 'src/app/pagination';
import { PageEvent } from '@angular/material/paginator';

/** Injects the event's name to adjust the title. */
let titleResolver: ResolveFn<string> = (route: ActivatedRouteSnapshot) => {
  return route.parent!.data['event'].name;
};

@Component({
  selector: 'app-advising-events',
  templateUrl: './advising-events.component.html',
  styleUrl: './advising-events.component.css'
})
export class AdvisingEventsComponent implements OnInit {
  /** Route information to be used in Event Routing Module */
  public static Route = {
    path: ':id',
    title: 'Advising Events',
    component: AdvisingEventsComponent,
    resolve: {
      event: advisingResolver
    },
    children: [
      { path: '', title: titleResolver, component: AdvisingEventsComponent }
    ]
  };

  /** Store the currently-logged-in user's profile.  */
  public profile: Profile;

  /** The event to show */
  public event: WritableSignal<DropInOverview>;

  /** Event registrations */
  public advisingRegistrationsPage: WritableSignal<
    Paginated<Profile, PaginationParams> | undefined
  > = signal(undefined);

  public advisingRegistrationDisplayedColumns: string[] = [
    'first_name',
    'last_name',
    'pronouns',
    'email'
  ];

  registrationType = RegistrationType;

  /** Constructs the Event Detail component. */
  constructor(
    private route: ActivatedRoute,
    private permissionService: PermissionService,
    private profileService: ProfileService,
    private gearService: NagivationAdminGearService,
    protected snackBar: MatSnackBar,
    private advisingService: AdvisingService
  ) {
    this.profile = this.profileService.profile()!;

    const data = this.route.snapshot.data as {
      event: DropInOverview;
    };

    this.event = signal(data.event);

    this.permissionService
      .check(
        'organization.events.edit',
        `organization/${this.event()?.advisor_id ?? '*'}`
      )
      .subscribe((permission) => {
        if (permission) {
          // Load user registrations:
          this.advisingService
            .getRegisteredUsersForEvent(this.event(), {
              page: 0,
              page_size: 25,
              order_by: 'first_name',
              filter: ''
            } as PaginationParams)
            .subscribe((page) => this.advisingRegistrationsPage.set(page));
        }
      });
  }

  ngOnInit() {
    this.gearService.showAdminGearByPermissionCheck(
      'events.*',
      '*',
      '',
      `/events/${this.event()?.advisor_slug}/${this.event()?.id}/edit`
    );
  }

  /** Registers a user for an event. */
  registerForEvent() {
    if (this.event().override_registration_url) {
      window.location.href = this.event().override_registration_url!;
      return;
    }

    this.advisingService.registerForEvent(this.event()!.id!).subscribe({
      next: () => {
        let newEvent = this.event();
        newEvent.user_registration_type = RegistrationType.STUDENT;
        newEvent.number_registered += 1;
        this.event.set(newEvent);

        this.snackBar.open(
          `Successfully registered for ${this.event()!.name}!`,
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
    let newEvent = this.event();
    newEvent.user_registration_type = null;
    newEvent.number_registered -= 1;
    this.event.set(newEvent);

    this.advisingService.unregisterForEvent(this.event()!.id!).subscribe({
      next: () => {
        this.snackBar.open(
          `Successfully unregistered for ${this.event()!.name}!`,
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

  handlePageEvent(e: PageEvent) {
    let paginationParams = this.advisingRegistrationsPage()!.params;
    paginationParams.page = e.pageIndex;
    paginationParams.page_size = e.pageSize;
    this.advisingService
      .getRegisteredUsersForEvent(this.event(), paginationParams)
      .subscribe((page) => this.advisingRegistrationsPage.set(page));
  }
}
