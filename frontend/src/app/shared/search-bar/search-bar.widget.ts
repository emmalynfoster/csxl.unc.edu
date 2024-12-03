import {
  Component,
  forwardRef,
  Input,
  Output,
  EventEmitter
} from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'search-bar',
  templateUrl: './search-bar.widget.html',
  styleUrls: ['./search-bar.widget.css'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SearchBar),
      multi: true
    }
  ]
})
export class SearchBar implements ControlValueAccessor {
  @Input() searchBarQuery: string = '';
  @Input() isAdvisingContext: boolean = false; // New flag for advising-specific behavior
  @Output() searchBarQueryChange = new EventEmitter<string>();

  private onChange: (value: string) => void = () => {};
  private onTouched: () => void = () => {};

  writeValue(value: string): void {
    this.searchBarQuery = value;
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState?(isDisabled: boolean): void {
    // Handle the disabled state if needed
  }

  onTextChanged(): void {
    this.searchBarQueryChange.emit(this.searchBarQuery);
    this.onChange(this.searchBarQuery);
    this.onTouched();
  }

  clearSearch(): void {
    // if (this.isAdvisingContext) {
    //   // Avoid clearing the input in advising context
    //   console.log('Advising context active. Skipping clear.');
    //   this.onTextChanged(); // Trigger the search instead
    //   return;
    // }

    // TODO: Bug here, the searchBarQuery is not being cleared when the clear button is clicked likely because of the advising context flag
    // Fixing this bug will require removing the advising context flag and adding a new flag to handle the search bar query clearing behavior
    // Need to look at search-bar.widget.html to see how the clear button is implemented

    if (!this.allowClearSearch()) {
      console.log('Clear search is disabled.');
      this.onTextChanged(); // Trigger the search action instead
      return;
    }

    this.searchBarQuery = ''; // Clear the input for non-advising contexts
    this.searchBarQueryChange.emit(this.searchBarQuery);
    this.onChange(this.searchBarQuery);
    this.onTouched();
  }

  allowClearSearch(): boolean {
    // Only allow clearing if not in advising context or other contexts where clearing is disabled
    return !this.isAdvisingContext;
  }
}
