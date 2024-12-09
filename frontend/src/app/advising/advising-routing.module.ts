/**
 * @author Ife Babarinde, Emmalyn Foster
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdvisingPageComponent } from './advising-page/advising-page.component';
import { AdvisingEventsComponent } from './advising-events/advising-events.component';

const routes: Routes = [
  AdvisingPageComponent.Route,
  AdvisingEventsComponent.Route
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdvisingRoutingModule {}
