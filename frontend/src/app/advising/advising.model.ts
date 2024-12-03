/**
 * @author Ife Babarinde
 * @copyright 2024
 * @license MIT
 */

import { Profile } from '../models.module';
import { Organization } from '../organization/organization.model';
import { PublicProfile } from '../profile/profile.service';

export enum RegistrationType {
  STUDENT,
  ADVISOR
}

export interface DropInRegistration {
  id: number | null;
  event_id: number;
  user_id: number;
  event: Event | null;
  user: Profile | null;
  is_advisor: boolean | null;
}

export interface DropInOverviewJson {
  id: number;
  name: string;
  start: string;
  end: string;
  location: string;
  description: string;
  public: boolean;
  number_registered: number;
  registration_limit: number;
  advisor_id: number;
  advisor_slug: string;
  advisor_name: string;
  organizers: PublicProfile[];
  user_registration_type: RegistrationType | null;
  image_url: string | null;
  override_registration_url: string | null;
}

export interface DropInOverview {
  id: number | null;
  name: string;
  start: Date;
  end: Date;
  location: string;
  description: string;
  public: boolean;
  number_registered: number;
  advisor_id: number;
  registration_limit: number;
  advisor_slug: string;
  advisor_name: string;
  organizers: PublicProfile[];
  user_registration_type: RegistrationType | null;
  image_url: string | null;
  override_registration_url: string | null;
}

export interface AdvisingEventDraft {
  id: number | null;
  name: string;
  start: Date;
  end: Date;
  location: string;
  description: string;
  public: boolean;
  registration_limit: number;
  advisor_slug: string;
  organizers: PublicProfile[];
  image_url: string | null;
  override_registration_url: string | null;
}

export const eventOverviewToDraft = (
  overview: DropInOverview
): AdvisingEventDraft => {
  return {
    id: overview.id,
    name: overview.name,
    start: overview.start,
    end: overview.end,
    location: overview.location,
    description: overview.description,
    public: overview.public,
    registration_limit: overview.registration_limit,
    advisor_slug: overview.advisor_slug,
    organizers: overview.organizers,
    image_url: overview.image_url,
    override_registration_url: overview.override_registration_url
  };
};

export interface DropInStatusOverviewJson {
  featured: DropInOverviewJson | null;
  registered: DropInOverviewJson[];
}
export interface DropInStatusOverview {
  featured: DropInOverview | null;
  registered: DropInOverview[];
}

export const parseDropInOverviewJson = (
  responseModel: DropInOverviewJson
): DropInOverview => {
  return Object.assign({}, responseModel, {
    start: new Date(responseModel.start),
    end: new Date(responseModel.end)
  });
};

export const parseDropInStatusOverviewJson = (
  responseModel: DropInStatusOverviewJson
): DropInStatusOverview => {
  return Object.assign({}, responseModel, {
    featured: responseModel.featured
      ? parseDropInOverviewJson(responseModel.featured!)
      : null,
    registered: responseModel.registered.map((registered) =>
      parseDropInOverviewJson(registered)
    )
  });
};

// reccuring weekly?
// completes the event then changes date to the upcoming time
// advising meeting table and scheduled meeting table and points to meta data and points to them for the next meeting
// rows for each meeting for the same meeting
// Widget set reminders button
//
