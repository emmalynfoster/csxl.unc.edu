/**
 *
 * @author Emmalyn Foster, Ife Babarinde
 *
 */

import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

/* Angular Material Modules */
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatChipsModule } from '@angular/material/chips';

/* UI Widgets */
import { RouterModule } from '@angular/router';
import { SharedModule } from '../shared/shared.module';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { AdvisingPageComponent } from './advising-page/advising-page.component';
import { AdvisingRoutingModule } from './advising-routing.module';
import { AdvisingEventsComponent } from './advising-events/advising-events.component';
import { GroupAdvisingEventsPipe } from './pipes/group-advising-events.pipe';
import { DropInCardWidget } from './widgets/drop-in-card/drop-in-card.widget';

import { DatePipe } from '@angular/common';

@NgModule({
  declarations: [
    AdvisingPageComponent,
    AdvisingEventsComponent,
    GroupAdvisingEventsPipe,
    DropInCardWidget
  ],
  imports: [
    CommonModule,
    MatTabsModule,
    MatTableModule,
    MatCardModule,
    MatChipsModule,
    MatDialogModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatPaginatorModule,
    MatListModule,
    MatAutocompleteModule,
    FormsModule,
    ReactiveFormsModule,
    MatIconModule,
    MatTooltipModule,
    RouterModule,
    SharedModule,
    MatSlideToggleModule,
    AdvisingRoutingModule
  ],
  providers: [DatePipe, GroupAdvisingEventsPipe]
})
export class AdvisingModule {}
