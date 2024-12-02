/**
 * The Event Editor Component allows users to edit information
 * about advising sessions that are publically displayed on the Advising page.
 *
 */

// Ill continue working on this if we need it?

import { Component } from '@angular/core';
import { ActivatedRoute, Route, Router } from '@angular/router';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { AdvisingService } from '../advising.service';

@Component({
  selector: 'app-event-editor',
  templateUrl: './event-editor.component.html',
  styleUrl: './event-editor.component.css'
})
export class EventEditorComponent {}
