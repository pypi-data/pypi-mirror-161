import { ISignal, Signal } from '@lumino/signaling';

import { NotebookPanel } from '@jupyterlab/notebook';

import { IValidateButtonExtension } from "@educational-technology-collective/etc_jupyterlab_nbgrader_validate";

export class ETCJupyterLabTelemetryValidateButton {

  private _notebookPanel: NotebookPanel;
  private _validateButtonExtension: IValidateButtonExtension;
  private _validateButtonClicked: Signal<ETCJupyterLabTelemetryValidateButton, any> = new Signal(this);
  private _validationResultsDisplayed: Signal<ETCJupyterLabTelemetryValidateButton, any> = new Signal(this);
  private _validationResultsDismissed: Signal<ETCJupyterLabTelemetryValidateButton, any> = new Signal(this);

  constructor(
    { notebookPanel, validateButtonExtension }:
      { notebookPanel: NotebookPanel, validateButtonExtension: IValidateButtonExtension}) {

    this._notebookPanel = notebookPanel;
    this._validateButtonExtension = validateButtonExtension;

    this._validateButtonExtension.validateButtonClicked.connect(this.onValidateButtonClicked, this);
    this._validateButtonExtension.validationResultsDisplayed.connect(this.onValidationResultsDisplayed, this);
    this._validateButtonExtension.validationResultsDismissed.connect(this.onValidationResultsDismissed, this);
  }

  private onValidateButtonClicked(sender: IValidateButtonExtension, args: any) {

    if (this._notebookPanel === args.notebook_panel) {

      this._validateButtonClicked.emit({
        event_name: args.name,
        notebookPanel: this._notebookPanel
      });
    }
  }

  private onValidationResultsDisplayed(sender: IValidateButtonExtension, args: any) {

    if (this._notebookPanel === args.notebook_panel) {

      this._validationResultsDisplayed.emit({
        event_name: args.name,
        message: args.message,
        notebookPanel: this._notebookPanel
      });

    }
  }

  private onValidationResultsDismissed(sender: IValidateButtonExtension, args: any) {

    if (this._notebookPanel === args.notebook_panel) {

      this._validationResultsDismissed.emit({
        event_name: args.name,
        message: args.message,
        notebookPanel: this._notebookPanel
      });

    }
  }

  get validateButtonClicked(): ISignal<ETCJupyterLabTelemetryValidateButton, any> {
    return this._validateButtonClicked
  }

  get validationResultsDisplayed(): ISignal<ETCJupyterLabTelemetryValidateButton, any> {
    return this._validationResultsDisplayed
  }

  get validationResultsDismissed(): ISignal<ETCJupyterLabTelemetryValidateButton, any> {
    return this._validationResultsDismissed
  }
}
