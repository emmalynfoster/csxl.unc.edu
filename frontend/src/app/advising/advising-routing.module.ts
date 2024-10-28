/**
 * @author Emmalyn Foster
 */

import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AdvisingPageComponent } from './advising-page/advising-page.component';

const routes: Routes = [
    AdvisingPageComponent.Route
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdvisingRoutingModule {}
