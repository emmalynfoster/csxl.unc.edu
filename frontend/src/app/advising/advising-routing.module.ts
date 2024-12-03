/**
 * @author Emmalyn Foster
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdvisingPageComponent } from './advising-page/advising-page.component';
import { EventEditorComponent } from './event-editor/event-editor.component';
import { AdvisingEventsComponent } from './advising-events/advising-events.component';

const routes: Routes = [
  AdvisingPageComponent.Route,
  // EventEditorComponent.Route,
  AdvisingEventsComponent.Route
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdvisingRoutingModule {}
