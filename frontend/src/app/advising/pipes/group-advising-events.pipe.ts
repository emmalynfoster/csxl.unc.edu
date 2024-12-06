import { Pipe, PipeTransform, inject } from '@angular/core';
import { DatePipe } from '@angular/common';
import { DropIn } from '../advising.model';

@Pipe({
  name: 'groupAdvisingEvents'
})
export class GroupAdvisingEventsPipe implements PipeTransform {
  datePipe = inject(DatePipe);

  transform(events: DropIn[]): [string, DropIn[]][] {
    // Initialize an empty map
    let groups: Map<string, DropIn[]> = new Map();

    // Transform the list of events based on the event filter pipe and query
    events.forEach((event) => {
      // Find the date to group by
      let dateString =
        this.datePipe.transform(event.start, 'EEEE, MMMM d, y') ?? '';
      // Add the event
      let newEventsList = groups.get(dateString) ?? [];
      newEventsList.push(event);
      groups.set(dateString, newEventsList);
    });

    // Return the groups
    return [...groups.entries()];
  }
}
