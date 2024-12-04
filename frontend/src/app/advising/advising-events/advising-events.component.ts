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
import { DropIn } from '../advising.model';
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
  /** Route information to be used in Advising Routing Module */
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
  public event: WritableSignal<DropIn>;


  /** Constructs the Event Detail component. */
  constructor(
    private route: ActivatedRoute,
    private profileService: ProfileService,
    protected snackBar: MatSnackBar,
    private advisingService: AdvisingService
  ) {
    this.profile = this.profileService.profile()!;

    const data = this.route.snapshot.data as {
      event: DropIn;
    };

    this.event = signal(data.event);
  }
  ngOnInit(): void {
    throw new Error('Method not implemented.');
  }

  handlePageEvent(e: PageEvent) {

  }
}
