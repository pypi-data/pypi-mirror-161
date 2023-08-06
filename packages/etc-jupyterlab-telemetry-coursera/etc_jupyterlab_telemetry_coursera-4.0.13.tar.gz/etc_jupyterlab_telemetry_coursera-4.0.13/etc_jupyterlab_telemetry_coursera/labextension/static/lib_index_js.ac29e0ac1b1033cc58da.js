"use strict";
(self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_coursera"] = self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_coursera"] || []).push([["lib_index_js"],{

/***/ "./lib/etc_jupyterlab_telemetry_validate_button.js":
/*!*********************************************************!*\
  !*** ./lib/etc_jupyterlab_telemetry_validate_button.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ETCJupyterLabTelemetryValidateButton": () => (/* binding */ ETCJupyterLabTelemetryValidateButton)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

class ETCJupyterLabTelemetryValidateButton {
    constructor({ notebookPanel, validateButtonExtension }) {
        this._validateButtonClicked = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._validationResultsDisplayed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._validationResultsDismissed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._validateButtonExtension = validateButtonExtension;
        this._validateButtonExtension.validateButtonClicked.connect(this.onValidateButtonClicked, this);
        this._validateButtonExtension.validationResultsDisplayed.connect(this.onValidationResultsDisplayed, this);
        this._validateButtonExtension.validationResultsDismissed.connect(this.onValidationResultsDismissed, this);
    }
    onValidateButtonClicked(sender, args) {
        if (this._notebookPanel === args.notebook_panel) {
            this._validateButtonClicked.emit({
                event_name: args.name,
                notebookPanel: this._notebookPanel
            });
        }
    }
    onValidationResultsDisplayed(sender, args) {
        if (this._notebookPanel === args.notebook_panel) {
            this._validationResultsDisplayed.emit({
                event_name: args.name,
                message: args.message,
                notebookPanel: this._notebookPanel
            });
        }
    }
    onValidationResultsDismissed(sender, args) {
        if (this._notebookPanel === args.notebook_panel) {
            this._validationResultsDismissed.emit({
                event_name: args.name,
                message: args.message,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get validateButtonClicked() {
        return this._validateButtonClicked;
    }
    get validationResultsDisplayed() {
        return this._validationResultsDisplayed;
    }
    get validationResultsDismissed() {
        return this._validationResultsDismissed;
    }
}


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'etc-jupyterlab-telemetry-coursera', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "AWSAPIGatewayAdapter": () => (/* binding */ AWSAPIGatewayAdapter),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_telemetry_library__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @educational-technology-collective/etc_jupyterlab_telemetry_library */ "webpack/sharing/consume/default/@educational-technology-collective/etc_jupyterlab_telemetry_library");
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_telemetry_library__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_educational_technology_collective_etc_jupyterlab_telemetry_library__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @educational-technology-collective/etc_jupyterlab_notebook_state_provider */ "webpack/sharing/consume/default/@educational-technology-collective/etc_jupyterlab_notebook_state_provider");
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_nbgrader_validate__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @educational-technology-collective/etc_jupyterlab_nbgrader_validate */ "webpack/sharing/consume/default/@educational-technology-collective/etc_jupyterlab_nbgrader_validate");
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_nbgrader_validate__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_educational_technology_collective_etc_jupyterlab_nbgrader_validate__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _etc_jupyterlab_telemetry_validate_button__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./etc_jupyterlab_telemetry_validate_button */ "./lib/etc_jupyterlab_telemetry_validate_button.js");






const PLUGIN_ID = '@educational-technology-collective/etc_jupyterlab_telemetry_coursera:plugin';
class AWSAPIGatewayAdapter {
    constructor({ etcJupyterLabNotebookStateProvider }) {
        this._etcJupyterLabNotebookStateProvider = etcJupyterLabNotebookStateProvider;
        this._userId = (async () => {
            try { // to get the user id.
                return await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('workspace_id');
            }
            catch (e) {
                console.error(`Error on GET id.\n${e}`);
                return 'UNDEFINED';
            }
            //  This request is specific to the Coursera environment; hence, it may not be relevant in other contexts.
            //  The request for the `id` resource will return the value of the WORKSPACE_ID environment variable that is assigned on the server.
        })();
    }
    async adaptMessage(sender, data) {
        var _a;
        try {
            let notebookPath = data.notebookPanel.context.path;
            if (data['eventName'] == 'save_notebook') {
                data.meta = (_a = data.notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.toJSON();
            }
            let notebookState = this._etcJupyterLabNotebookStateProvider.getNotebookState({
                notebookPanel: data.notebookPanel
            });
            var message = Object.assign(Object.assign({ 'event_name': data.eventName, 'cells': data.cells }, notebookState), {
                user_id: await this._userId,
                notebook_path: notebookPath
            });
            if (data.meta) {
                message['meta'] = data.meta;
            }
            console.log('Request', message);
            let response = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('s3', { method: 'POST', body: JSON.stringify(message) });
            message = Object.assign({}, message);
            delete message.notebook;
            delete message.cells;
            message === null || message === void 0 ? true : delete message.meta;
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
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    requires: [
        _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker,
        _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__.IETCJupyterLabNotebookStateProvider,
        _educational_technology_collective_etc_jupyterlab_telemetry_library__WEBPACK_IMPORTED_MODULE_1__.IETCJupyterLabTelemetryLibraryFactory,
        _educational_technology_collective_etc_jupyterlab_nbgrader_validate__WEBPACK_IMPORTED_MODULE_3__.IValidateButtonExtension
    ],
    activate: (app, notebookTracker, etcJupyterLabNotebookStateProvider, etcJupyterLabTelemetryLibraryFactory, validateButtonExtension) => {
        let messageAdapter;
        let telemetry = (async () => {
            try {
                await app.started;
                const VERSION = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('version');
                console.log(`${PLUGIN_ID}, ${VERSION}`);
                let result = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('telemetry');
                console.log('telemetry', result);
                if (!result.telemetry) {
                    notebookTracker.widgetAdded.disconnect(onWidgetAdded, undefined);
                }
                return result.telemetry;
            }
            catch (e) {
                console.error(e);
                notebookTracker.widgetAdded.disconnect(onWidgetAdded, undefined);
                return false;
            }
        })();
        async function onWidgetAdded(sender, notebookPanel) {
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
                let etcJupyterLabTelemetryValidateButton = new _etc_jupyterlab_telemetry_validate_button__WEBPACK_IMPORTED_MODULE_5__.ETCJupyterLabTelemetryValidateButton({
                    notebookPanel,
                    validateButtonExtension
                });
                etcJupyterLabTelemetryValidateButton.validateButtonClicked.connect(messageAdapter.adaptMessage, messageAdapter);
                etcJupyterLabTelemetryValidateButton.validationResultsDisplayed.connect(messageAdapter.adaptMessage, messageAdapter);
                etcJupyterLabTelemetryValidateButton.validationResultsDismissed.connect(messageAdapter.adaptMessage, messageAdapter);
            }
        }
        notebookTracker.widgetAdded.connect(onWidgetAdded, undefined);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.ac29e0ac1b1033cc58da.js.map