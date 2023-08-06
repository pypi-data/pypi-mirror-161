"use strict";
(self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_library"] = self["webpackChunk_educational_technology_collective_etc_jupyterlab_telemetry_library"] || []).push([["lib_index_js"],{

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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'etc-jupyterlab-telemetry-library', // API Namespace
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
/* harmony export */   "IETCJupyterLabTelemetryLibraryFactory": () => (/* binding */ IETCJupyterLabTelemetryLibraryFactory),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @educational-technology-collective/etc_jupyterlab_notebook_state_provider */ "webpack/sharing/consume/default/@educational-technology-collective/etc_jupyterlab_notebook_state_provider");
/* harmony import */ var _educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _library__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./library */ "./lib/library.js");





const PLUGIN_ID = '@educational-technology-collective/etc_jupyterlab_telemetry_library:plugin';
const IETCJupyterLabTelemetryLibraryFactory = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_1__.Token(PLUGIN_ID);
class ETCJupyterLabTelemetryLibraryFactory {
    constructor({ config }) {
        this._config = config;
    }
    create({ notebookPanel }) {
        return new _library__WEBPACK_IMPORTED_MODULE_3__.ETCJupyterLabTelemetryLibrary({ notebookPanel, config: this._config });
    }
}
/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_telemetry_extension extension.
 */
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    provides: IETCJupyterLabTelemetryLibraryFactory,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.INotebookTracker],
    optional: [_educational_technology_collective_etc_jupyterlab_notebook_state_provider__WEBPACK_IMPORTED_MODULE_2__.IETCJupyterLabNotebookStateProvider],
    activate: async (app, notebookTracker, etcJupyterLabNotebookStateProvider) => {
        const VERSION = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("version");
        console.log(`${PLUGIN_ID}, ${VERSION}`);
        const CONFIG = await (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)("config");
        let etcJupyterLabTelemetryLibraryFactory = new ETCJupyterLabTelemetryLibraryFactory({ config: CONFIG });
        // // TEST
        // class MessageAdapter {
        //   constructor() { }
        //   log(sender: any, args: any) {
        //     let notebookPanel = args.notebookPanel;
        //     delete args.notebookPanel;
        //     let notebookState = etcJupyterLabNotebookStateProvider.getNotebookState({ notebookPanel: notebookPanel })
        //     let data = {
        //       ...args, ...notebookState
        //     }
        //     console.log("etc_jupyterlab_telemetry_extension", data);
        //   }
        // }
        // let messageAdapter = new MessageAdapter();
        // notebookTracker.widgetAdded.connect(async (sender: INotebookTracker, notebookPanel: NotebookPanel) => {
        //   etcJupyterLabNotebookStateProvider.addNotebookPanel({ notebookPanel });
        //   let etcJupyterLabTelemetryLibrary = etcJupyterLabTelemetryLibraryFactory.create({ notebookPanel });
        //   etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardCopied.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardCut.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookClipboardEvent.notebookClipboardPasted.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookVisibilityEvent.notebookVisible.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookVisibilityEvent.notebookHidden.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookOpenEvent.notebookOpened.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookCloseEvent.notebookClosed.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookSaveEvent.notebookSaved.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.notebookScrollEvent.notebookScrolled.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.activeCellChangeEvent.activeCellChanged.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellAddEvent.cellAdded.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellRemoveEvent.cellRemoved.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellExecutionEvent.cellExecuted.connect(messageAdapter.log);
        //   etcJupyterLabTelemetryLibrary.cellErrorEvent.cellErrored.connect(messageAdapter.log);
        // });
        // // TEST
        return etcJupyterLabTelemetryLibraryFactory;
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/library.js":
/*!************************!*\
  !*** ./lib/library.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ActiveCellChangeEvent": () => (/* binding */ ActiveCellChangeEvent),
/* harmony export */   "CellAddEvent": () => (/* binding */ CellAddEvent),
/* harmony export */   "CellErrorEvent": () => (/* binding */ CellErrorEvent),
/* harmony export */   "CellExecutionEvent": () => (/* binding */ CellExecutionEvent),
/* harmony export */   "CellRemoveEvent": () => (/* binding */ CellRemoveEvent),
/* harmony export */   "ETCJupyterLabTelemetryLibrary": () => (/* binding */ ETCJupyterLabTelemetryLibrary),
/* harmony export */   "NotebookClipboardEvent": () => (/* binding */ NotebookClipboardEvent),
/* harmony export */   "NotebookCloseEvent": () => (/* binding */ NotebookCloseEvent),
/* harmony export */   "NotebookOpenEvent": () => (/* binding */ NotebookOpenEvent),
/* harmony export */   "NotebookSaveEvent": () => (/* binding */ NotebookSaveEvent),
/* harmony export */   "NotebookScrollEvent": () => (/* binding */ NotebookScrollEvent),
/* harmony export */   "NotebookVisibilityEvent": () => (/* binding */ NotebookVisibilityEvent)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");



class ETCJupyterLabTelemetryLibrary {
    constructor({ notebookPanel, config }) {
        this.notebookClipboardEvent = new NotebookClipboardEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookVisibilityEvent = new NotebookVisibilityEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookCloseEvent = new NotebookCloseEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookOpenEvent = new NotebookOpenEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookSaveEvent = new NotebookSaveEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellExecutionEvent = new CellExecutionEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellErrorEvent = new CellErrorEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.notebookScrollEvent = new NotebookScrollEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.activeCellChangeEvent = new ActiveCellChangeEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellAddEvent = new CellAddEvent({
            notebookPanel: notebookPanel,
            config: config
        });
        this.cellRemoveEvent = new CellRemoveEvent({
            notebookPanel: notebookPanel,
            config: config
        });
    }
}
class NotebookEvent {
    constructor(notebookPanel) {
        this._notebookPanel = notebookPanel;
    }
    getVisibleCells() {
        let cells = [];
        let cell;
        let index;
        let id;
        let notebook = this._notebookPanel.content;
        for (index = 0; index < notebook.widgets.length; index++) {
            cell = notebook.widgets[index];
            let cellTop = cell.node.offsetTop;
            let cellBottom = cell.node.offsetTop + cell.node.offsetHeight;
            let viewTop = notebook.node.scrollTop;
            let viewBottom = notebook.node.scrollTop + notebook.node.clientHeight;
            if (cellTop > viewBottom || cellBottom < viewTop) {
                continue;
            }
            id = cell.model.id;
            cells.push({ id, index });
        }
        return cells;
    }
}
class NotebookClipboardEvent {
    constructor({ notebookPanel, config }) {
        this._notebookClipboardCopied = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookClipboardCut = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookClipboardPasted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        this.handleCopy = this.handleCopy.bind(this);
        this.handleCut = this.handleCut.bind(this);
        this.handlePaste = this.handlePaste.bind(this);
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_clipboard_event) {
            this._notebookPanel.node.addEventListener('copy', this.handleCopy, false);
            this._notebookPanel.node.addEventListener('cut', this.handleCut, false);
            this._notebookPanel.node.addEventListener('paste', this.handlePaste, false);
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
        this._notebookPanel.node.removeEventListener('copy', this.handleCopy, false);
        this._notebookPanel.node.removeEventListener('cut', this.handleCut, false);
        this._notebookPanel.node.removeEventListener('paste', this.handlePaste, false);
    }
    handleCopy(event) {
        var _a;
        let text = (_a = document.getSelection()) === null || _a === void 0 ? void 0 : _a.toString();
        let cell = this._notebookPanel.content.activeCell;
        let cells = [
            {
                id: cell === null || cell === void 0 ? void 0 : cell.model.id,
                index: this._notebook.widgets.findIndex((value) => value == cell)
            }
        ];
        this._notebookClipboardCopied.emit({
            eventName: 'clipboard_copy',
            cells: cells,
            notebookPanel: this._notebookPanel,
            selection: text
        });
    }
    handleCut(event) {
        var _a;
        let text = (_a = document.getSelection()) === null || _a === void 0 ? void 0 : _a.toString();
        let cell = this._notebookPanel.content.activeCell;
        let cells = [
            {
                id: cell === null || cell === void 0 ? void 0 : cell.model.id,
                index: this._notebook.widgets.findIndex((value) => value == cell)
            }
        ];
        this._notebookClipboardCut.emit({
            eventName: 'clipboard_cut',
            cells: cells,
            notebookPanel: this._notebookPanel,
            selection: text
        });
    }
    handlePaste(event) {
        let text = (event.clipboardData || window.clipboardData).getData('text');
        let cell = this._notebookPanel.content.activeCell;
        let cells = [
            {
                id: cell === null || cell === void 0 ? void 0 : cell.model.id,
                index: this._notebook.widgets.findIndex((value) => value == cell)
            }
        ];
        this._notebookClipboardPasted.emit({
            eventName: 'clipboard_paste',
            cells: cells,
            notebookPanel: this._notebookPanel,
            selection: text
        });
    }
    get notebookClipboardCopied() {
        return this._notebookClipboardCopied;
    }
    get notebookClipboardCut() {
        return this._notebookClipboardCut;
    }
    get notebookClipboardPasted() {
        return this._notebookClipboardPasted;
    }
}
class NotebookVisibilityEvent extends NotebookEvent {
    constructor({ notebookPanel, config }) {
        super(notebookPanel);
        this._notebookVisible = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookHidden = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._hiddenProperty = 'hidden';
        this._visibilityChange = 'visibilitychange';
        this._visibility = false;
        this._notebookPanel = notebookPanel;
        let notebook = this._notebook = notebookPanel.content;
        this.handleVisibilityChange = this.handleVisibilityChange.bind(this);
        this.handleFocus = this.handleFocus.bind(this);
        this.handleBlur = this.handleBlur.bind(this);
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_visibility_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    if (typeof document.hidden !== 'undefined') {
                        this._hiddenProperty = 'hidden';
                        this._visibilityChange = 'visibilitychange';
                    }
                    else if (typeof document.msHidden !== 'undefined') {
                        this._hiddenProperty = 'msHidden';
                        this._visibilityChange = 'msvisibilitychange';
                    }
                    else if (typeof document.webkitHidden !== 'undefined') {
                        this._hiddenProperty = 'webkitHidden';
                        this._visibilityChange = 'webkitvisibilitychange';
                    }
                    document.addEventListener(this._visibilityChange, this.handleVisibilityChange, false);
                    notebook.node.addEventListener('blur', this.handleBlur, true);
                    notebook.node.addEventListener('focus', this.handleFocus, true);
                    window.addEventListener('blur', this.handleBlur, true);
                    window.addEventListener('focus', this.handleFocus, true);
                    this.visibility = notebookPanel.content.isVisible;
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
        document.removeEventListener(this._visibilityChange, this.handleVisibilityChange, false);
        this._notebook.node.removeEventListener('blur', this.handleBlur, true);
        this._notebook.node.removeEventListener('focus', this.handleFocus, true);
        window.removeEventListener('blur', this.handleBlur, true);
        window.removeEventListener('focus', this.handleFocus, true);
    }
    handleVisibilityChange(event) {
        this.visibility = !document[this._hiddenProperty] && this._notebook.isVisible;
    }
    handleBlur(event) {
        if (event.currentTarget === window && event.target === window) {
            this.visibility = false;
        }
        else if (event.currentTarget === this._notebook.node) {
            this.visibility = this._notebook.isVisible;
        }
    }
    handleFocus(event) {
        this.visibility = this._notebook.isVisible;
    }
    set visibility(visibility) {
        if (this._visibility != visibility) {
            this._visibility = visibility;
            let cells = this.getVisibleCells();
            if (this._visibility === true) {
                this._notebookVisible.emit({
                    eventName: 'notebook_visible',
                    cells: cells,
                    notebookPanel: this._notebookPanel
                });
            }
            else if (this._visibility === false) {
                this._notebookHidden.emit({
                    eventName: 'notebook_hidden',
                    cells: cells,
                    notebookPanel: this._notebookPanel
                });
            }
        }
    }
    get notebookVisible() {
        return this._notebookVisible;
    }
    get notebookHidden() {
        return this._notebookHidden;
    }
}
class NotebookCloseEvent {
    constructor({ notebookPanel, config }) {
        this._notebookClosed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        if (config.notebook_close_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.disposed.connect(this.onNotebookDisposed, this);
                    notebookPanel.disposed.connect(this.onDisposed, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onNotebookDisposed() {
        let cells = this._notebook.widgets.map((cell, index) => ({ id: cell.model.id, index: index }));
        this._notebookClosed.emit({
            eventName: 'close_notebook',
            cells: cells,
            notebookPanel: this._notebookPanel
        });
    }
    get notebookClosed() {
        return this._notebookClosed;
    }
}
class NotebookSaveEvent {
    constructor({ notebookPanel, config }) {
        this._notebookSaved = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_save_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.context.saveState.connect(this.onSaveState, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onSaveState(context, saveState) {
        let cell;
        let cells;
        let index;
        if (saveState.match('completed')) {
            cells = [];
            for (index = 0; index < this._notebookPanel.content.widgets.length; index++) {
                cell = this._notebookPanel.content.widgets[index];
                if (this._notebookPanel.content.isSelectedOrActive(cell)) {
                    cells.push({ id: cell.model.id, index });
                }
            }
            this._notebookSaved.emit({
                eventName: 'save_notebook',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get notebookSaved() {
        return this._notebookSaved;
    }
}
class CellExecutionEvent {
    constructor({ notebookPanel, config }) {
        this._cellExecuted = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_execution_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.executed.connect(this.onExecuted, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onExecuted(_, args) {
        if (args.notebook.model === this._notebook.model) {
            let cells = [
                {
                    id: args.cell.model.id,
                    index: this._notebook.widgets.findIndex((value) => value == args.cell)
                }
            ];
            this._cellExecuted.emit({
                eventName: 'cell_executed',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellExecuted() {
        return this._cellExecuted;
    }
}
class NotebookScrollEvent extends NotebookEvent {
    constructor({ notebookPanel, config }) {
        super(notebookPanel);
        this._notebookScrolled = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._timeout = 0;
        this.onScrolled = this.onScrolled.bind(this);
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_scroll_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.content.node.addEventListener('scroll', this.onScrolled, false);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onScrolled(e) {
        e.stopPropagation();
        clearTimeout(this._timeout);
        this._timeout = setTimeout(() => {
            let cells = this.getVisibleCells();
            this._notebookScrolled.emit({
                eventName: 'scroll',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }, 1000);
    }
    get notebookScrolled() {
        return this._notebookScrolled;
    }
}
class ActiveCellChangeEvent {
    constructor({ notebookPanel, config }) {
        this._activeCellChanged = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_active_cell_change_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    notebookPanel.content.activeCellChanged.connect(this.onActiveCellChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onActiveCellChanged(send, args) {
        if (this._notebook.widgets.length > 1) {
            //  More than 1 cell is needed in order for this event to happen; hence, check the number of cells.
            let cells = [
                {
                    id: args.model.id,
                    index: this._notebook.widgets.findIndex((value) => value == args)
                }
            ];
            this._activeCellChanged.emit({
                eventName: 'active_cell_changed',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get activeCellChanged() {
        return this._activeCellChanged;
    }
}
class NotebookOpenEvent {
    constructor({ notebookPanel, config }) {
        this._notebookOpened = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._once = false;
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_open_event) {
            if (!this._once) {
                (async () => {
                    try {
                        await notebookPanel.revealed;
                        await this.emitNotebookOpened();
                    }
                    catch (e) {
                        console.error(e);
                    }
                })();
            }
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    async emitNotebookOpened() {
        let cells = this._notebook.widgets.map((cell, index) => ({ id: cell.model.id, index: index }));
        this._notebookOpened.emit({
            eventName: 'open_notebook',
            cells: cells,
            notebookPanel: this._notebookPanel,
            environ: await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('environ')
        });
        this._once = true;
    }
    get notebookOpened() {
        return this._notebookOpened;
    }
}
class CellAddEvent {
    constructor({ notebookPanel, config }) {
        this._cellAdded = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_add_event) {
            (async () => {
                var _a;
                try {
                    await notebookPanel.revealed;
                    (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(this.onCellsChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onCellsChanged(sender, args) {
        if (args.type == 'add') {
            let cells = [{ id: args.newValues[0].id, index: args.newIndex }];
            this._cellAdded.emit({
                eventName: 'add_cell',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellAdded() {
        return this._cellAdded;
    }
}
class CellRemoveEvent {
    constructor({ notebookPanel, config }) {
        this._cellRemoved = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_remove_event) {
            (async () => {
                var _a;
                try {
                    await notebookPanel.revealed;
                    (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect(this.onCellsChanged, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onCellsChanged(sender, args) {
        if (args.type == 'remove') {
            let cells = [{ id: args.oldValues[0].id, index: args.oldIndex }];
            this._cellRemoved.emit({
                eventName: 'remove_cell',
                cells: cells,
                notebookPanel: this._notebookPanel
            });
        }
    }
    get cellRemoved() {
        return this._cellRemoved;
    }
}
class CellErrorEvent {
    constructor({ notebookPanel, config }) {
        this._cellErrored = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal(this);
        this._notebookPanel = notebookPanel;
        notebookPanel.disposed.connect(this.onDisposed, this);
        if (config.notebook_cell_error_event) {
            (async () => {
                try {
                    await notebookPanel.revealed;
                    _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookActions.executed.connect(this.onExecuted, this);
                }
                catch (e) {
                    console.error(e);
                }
            })();
        }
    }
    onDisposed() {
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_1__.Signal.disconnectAll(this);
    }
    onExecuted(_, args) {
        if (!args.success || args.error) {
            let cells = [
                {
                    id: args.cell.model.id,
                    index: this._notebookPanel.content.widgets.findIndex((value) => value == args.cell)
                }
            ];
            this._cellErrored.emit({
                eventName: 'cell_errored',
                cells: cells,
                notebookPanel: this._notebookPanel,
                kernelError: args.error
            });
        }
    }
    get cellErrored() {
        return this._cellErrored;
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.969da09a6a07272b33b5.js.map