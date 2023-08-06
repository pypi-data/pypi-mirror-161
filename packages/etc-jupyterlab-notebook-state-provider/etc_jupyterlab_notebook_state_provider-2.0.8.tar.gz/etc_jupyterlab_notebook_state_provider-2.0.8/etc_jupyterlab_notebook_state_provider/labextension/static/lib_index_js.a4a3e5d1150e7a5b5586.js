"use strict";
(self["webpackChunk_educational_technology_collective_etc_jupyterlab_notebook_state_provider"] = self["webpackChunk_educational_technology_collective_etc_jupyterlab_notebook_state_provider"] || []).push([["lib_index_js"],{

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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'etc-jupyterlab-notebook-state-provider', // API Namespace
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
/* harmony export */   "ETCJupyterLabNotebookState": () => (/* binding */ ETCJupyterLabNotebookState),
/* harmony export */   "ETCJupyterLabNotebookStateProvider": () => (/* binding */ ETCJupyterLabNotebookStateProvider),
/* harmony export */   "IETCJupyterLabNotebookStateProvider": () => (/* binding */ IETCJupyterLabNotebookStateProvider),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__);


class ETCJupyterLabNotebookState {
    constructor({ notebookPanel }) {
        this._notebookPanel = notebookPanel;
        this._notebook = notebookPanel.content;
        this._nbFormatNotebook = null;
        this._cellState = new WeakMap();
        this._seq = 0;
        this._session_id = _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.UUID.uuid4();
        (async () => {
            var _a;
            await notebookPanel.revealed;
            this.updateCellState();
            //  The notebook loaded; hence, update the cell state.
            (_a = notebookPanel.content.model) === null || _a === void 0 ? void 0 : _a.cells.changed.connect((sender, args) => {
                this.updateCellState();
                //  A cell event happened; hence, update the cell state.
            }, this);
        })();
    }
    updateCellState() {
        this._notebook.widgets.forEach((cell) => {
            if (!this._cellState.has(cell)) {
                this._cellState.set(cell, { changed: true, output: this.createCellOutput(cell) });
                //  It's a new cell; hence, the changed state is set to true.
                ////  This is a new cell; hence, add handlers that check for changes in the inputs and outputs.
                cell.inputArea.model.value.changed.connect((sender, args) => {
                    let state = this._cellState.get(cell);
                    if (state !== undefined) {
                        state.changed = true;
                        //  The input area changed; hence, the changed state is set to true.
                    }
                });
                if (cell.model.type == 'code') {
                    cell.model.outputs.changed.connect((sender, args) => {
                        if (args.type == 'add') {
                            //  An output has been added to the cell; hence, compare the current state with the new state.
                            let state = this._cellState.get(cell);
                            if (state !== undefined) {
                                let output = this.createCellOutput(cell);
                                if (output !== (state === null || state === void 0 ? void 0 : state.output)) {
                                    //  The output has changed; hence, set changed to true and update the output state.
                                    state.changed = true;
                                    state.output = output;
                                }
                                else {
                                    //  The output hasn't changed; hence, leave the state as is.
                                }
                            }
                        }
                    });
                }
            }
        });
    }
    createCellOutput(cell) {
        //  Combine the cell outputs into a string in order to check for changes.
        let output = '';
        if (cell.model.type == 'code') {
            let outputs = cell.model.outputs;
            for (let index = 0; index < outputs.length; index++) {
                for (let key of Object.keys(outputs.get(index).data).sort()) {
                    output = output + JSON.stringify(outputs.get(index).data[key]);
                }
            }
            return output;
        }
        return '';
    }
    getNotebookState() {
        var _a;
        this._nbFormatNotebook = ((_a = this._notebook.model) === null || _a === void 0 ? void 0 : _a.toJSON()) || this._nbFormatNotebook;
        for (let index = 0; index < this._notebook.widgets.length; index++) {
            let cell = this._notebook.widgets[index];
            let cellState = this._cellState.get(cell);
            if (cellState === undefined) {
                throw new Error(`The cell at index ${index} is not tracked.`);
            }
            if (cellState.changed === false) {
                //  The cell has not changed; hence, the notebook format cell will contain just its id.
                this._nbFormatNotebook.cells[index] = { id: this._notebook.widgets[index].model.id };
            }
            else {
                this._nbFormatNotebook.cells[index]['id'] = this._notebook.widgets[index].model.id;
                //  This just ensures that the id was copied over in the call to toJSON.
            }
            //  Because it is possible for this to throw, as an extra precaution we don't
            //  mark the cells as unchanged at this point; we do it in the following for loop
            //  in order to ensure that it's *all or nothing* i.e., a transaction. 
        }
        for (let index = 0; index < this._notebook.widgets.length; index++) {
            let cell = this._notebook.widgets[index];
            let cellState = this._cellState.get(cell);
            if (cellState !== undefined) {
                cellState.changed = false;
            }
            //  The cell state is going to be captured; hence, set the state to not changed.
            //  Because it's possible for the first for loop to throw, we need to be
            //  certain that all the cells were processed prior to making any changes 
            //  to their state; hence, this operation is done in this loop separate from 
            //  the first loop above.
        }
        let state = {
            session_id: this._session_id,
            seq: this._seq,
            notebook: this._nbFormatNotebook
        };
        this._seq = this._seq + 1;
        //  We've made changes to the state at this point. *All* sequences must be logged in order to 
        //  reconstruct a notebook; hence, it's really important that nothing throws between now and 
        //  recording the message.
        return state;
    }
}
class ETCJupyterLabNotebookStateProvider {
    constructor() {
        this._notebookPanelMap = new WeakMap();
    }
    getNotebookState({ notebookPanel }) {
        let notebookState = this._notebookPanelMap.get(notebookPanel);
        return notebookState === null || notebookState === void 0 ? void 0 : notebookState.getNotebookState();
    }
    addNotebookPanel({ notebookPanel }) {
        let etcJupyterLabNotebookState = new ETCJupyterLabNotebookState({ notebookPanel });
        this._notebookPanelMap.set(notebookPanel, etcJupyterLabNotebookState);
    }
}
const PLUGIN_ID = '@educational-technology-collective/etc_jupyterlab_notebook_state_provider:plugin';
const IETCJupyterLabNotebookStateProvider = new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_0__.Token(PLUGIN_ID);
/**
 * Initialization data for the @educational-technology-collective/etc_jupyterlab_notebook_state extension.
 */
const plugin = {
    id: PLUGIN_ID,
    autoStart: true,
    provides: IETCJupyterLabNotebookStateProvider,
    activate: async (app) => {
        try {
            const VERSION = await (0,_handler__WEBPACK_IMPORTED_MODULE_1__.requestAPI)('version');
            console.log(`${PLUGIN_ID}, ${VERSION}`);
        }
        catch (e) {
            console.error(e);
        }
        finally {
            return new ETCJupyterLabNotebookStateProvider();
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.a4a3e5d1150e7a5b5586.js.map