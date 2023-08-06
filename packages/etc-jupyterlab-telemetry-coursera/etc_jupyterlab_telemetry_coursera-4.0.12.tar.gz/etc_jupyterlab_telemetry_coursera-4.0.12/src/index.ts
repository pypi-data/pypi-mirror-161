import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';

import { IETCJupyterLabTelemetryLibraryFactory } from '@educational-technology-collective/etc_jupyterlab_telemetry_library';

import { IETCJupyterLabNotebookStateProvider } from '@educational-technology-collective/etc_jupyterlab_notebook_state_provider';

import { IValidateButtonExtension } from '@educational-technology-collective/etc_jupyterlab_nbgrader_validate';

import { requestAPI } from './handler';

import { ETCJupyterLabTelemetryValidateButton } from './etc_jupyterlab_telemetry_validate_button';
import { INotebookEventMessage } from '@educational-technology-collective/etc_jupyterlab_telemetry_library/lib/types';

const PLUGIN_ID = '@educational-technology-collective/etc_jupyterlab_telemetry_coursera:plugin';

export class AWSAPIGatewayAdapter {

  private _userId: Promise<string>;
  private _etcJupyterLabNotebookStateProvider: IETCJupyterLabNotebookStateProvider;

  constructor(
    { etcJupyterLabNotebookStateProvider }:
      { etcJupyterLabNotebookStateProvider: IETCJupyterLabNotebookStateProvider }
  ) {

    this._etcJupyterLabNotebookStateProvider = etcJupyterLabNotebookStateProvider;

    this._userId = (async () => {

      try { // to get the user id.
        return await requestAPI<any>('workspace_id');
      } catch (e) {
        console.error(`Error on GET id.\n${e}`);
        return 'UNDEFINED';
      }
      //  This request is specific to the Coursera environment; hence, it may not be relevant in other contexts.
      //  The request for the `id` resource will return the value of the WORKSPACE_ID environment variable that is assigned on the server.
    })();
  }

  async adaptMessage(sender: any, data: INotebookEventMessage) {

    try {

      let notebookPath = data.notebookPanel.context.path;

      if (data['eventName'] == 'save_notebook') {

        var message: any = {
          'event_name': data.eventName,
          'cells': data.cells,
          'notebook': data.notebookPanel.content.model?.toJSON(),
          ...{
            user_id: await this._userId,
            notebook_path: notebookPath
          }
        }
      }
      else {
        
        let notebookState = this._etcJupyterLabNotebookStateProvider.getNotebookState({
          notebookPanel: data.notebookPanel
        });

        var message: any = {
          'event_name': data.eventName,
          'cells': data.cells,
          ...notebookState,
          ...{
            user_id: await this._userId,
            notebook_path: notebookPath
          }
        }
      }

      if (data.meta) {

        message['meta'] = data.meta;
      }

      console.log('Request', message);

      let response = await requestAPI<any>('s3', { method: 'POST', body: JSON.stringify(message) });

      message = { ...message };

      delete message.notebook;
      delete message.cells;
      delete message?.meta

      console.log('Response', {
        'response': response,
        'message': message
      });
    }
    catch (e) {

      console.error(e);
    }
  }
}

/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_telemetry_coursera extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: PLUGIN_ID,
  autoStart: true,
  requires: [
    INotebookTracker,
    IETCJupyterLabNotebookStateProvider,
    IETCJupyterLabTelemetryLibraryFactory,
    IValidateButtonExtension
  ],
  activate: (
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    etcJupyterLabNotebookStateProvider: IETCJupyterLabNotebookStateProvider,
    etcJupyterLabTelemetryLibraryFactory: IETCJupyterLabTelemetryLibraryFactory,
    validateButtonExtension: IValidateButtonExtension,
  ) => {

    let messageAdapter: AWSAPIGatewayAdapter;

    let telemetry = (async () => {
      try {

        await app.started;

        const VERSION = await requestAPI<string>('version')

        console.log(`${PLUGIN_ID}, ${VERSION}`);

        let result = await requestAPI<any>('telemetry');

        console.log('telemetry', result);

        if (!result.telemetry) {

          notebookTracker.widgetAdded.disconnect(onWidgetAdded, this);
        }

        return result.telemetry;
      }
      catch (e) {
        console.error(e);
        notebookTracker.widgetAdded.disconnect(onWidgetAdded, this);
        return false;
      }
    })();


    async function onWidgetAdded(sender: INotebookTracker, notebookPanel: NotebookPanel) {
      //  Handlers must be attached immediately in order to detect early events, hence we do not want to await the appearance of the Notebook.

      if (await telemetry) {

        if (!messageAdapter) {
          messageAdapter = new AWSAPIGatewayAdapter({ etcJupyterLabNotebookStateProvider });
        }

        etcJupyterLabNotebookStateProvider.addNotebookPanel({ notebookPanel });

        let etcJupyterLabTelemetryLibrary = etcJupyterLabTelemetryLibraryFactory.create({ notebookPanel });

        etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardCopied.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardCut.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardPasted.connect(messageAdapter.adaptMessage, messageAdapter);

        etcJupyterLabTelemetryLibrary.notebookVisibilityEvent.notebookVisible.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookVisibilityEvent.notebookHidden.connect(messageAdapter.adaptMessage, messageAdapter);

        etcJupyterLabTelemetryLibrary.notebookOpenEvent.notebookOpened.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookCloseEvent.notebookClosed.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookSaveEvent.notebookSaved.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.notebookScrollEvent.notebookScrolled.connect(messageAdapter.adaptMessage, messageAdapter);

        etcJupyterLabTelemetryLibrary.activeCellChangeEvent.activeCellChanged.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.cellAddEvent.cellAdded.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.cellRemoveEvent.cellRemoved.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.cellExecutionEvent.cellExecuted.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryLibrary.cellErrorEvent.cellErrored.connect(messageAdapter.adaptMessage, messageAdapter);

        let etcJupyterLabTelemetryValidateButton = new ETCJupyterLabTelemetryValidateButton({
          notebookPanel,
          validateButtonExtension
        });

        etcJupyterLabTelemetryValidateButton.validateButtonClicked.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryValidateButton.validationResultsDisplayed.connect(messageAdapter.adaptMessage, messageAdapter);
        etcJupyterLabTelemetryValidateButton.validationResultsDismissed.connect(messageAdapter.adaptMessage, messageAdapter);
      }
    }

    notebookTracker.widgetAdded.connect(onWidgetAdded, this);
  }
};

export default plugin;
