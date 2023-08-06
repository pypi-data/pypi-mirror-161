"use strict";
(self["webpackChunkjupyterlab_crosscompute"] = self["webpackChunkjupyterlab_crosscompute"] || []).push([["lib_index_js"],{

/***/ "./lib/body.js":
/*!*********************!*\
  !*** ./lib/body.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "AutomationBody": () => (/* binding */ AutomationBody)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _constant__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./constant */ "./lib/constant.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _model__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./model */ "./lib/model.js");





class AutomationBody extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(commands, openFolder, openPath) {
        super();
        this._commands = commands;
        this._openFolder = openFolder;
        this._openPath = openPath;
        this._model = new _model__WEBPACK_IMPORTED_MODULE_2__.AutomationModel();
        this.id = 'crosscompute-automation';
        this.addClass('crosscompute-Automation');
        const title = this.title;
        title.icon = _constant__WEBPACK_IMPORTED_MODULE_3__.logoIcon;
        title.caption = 'CrossCompute Automation';
    }
    updateModel(model) {
        const { folder } = model;
        let shouldUpdate = false;
        if (this._model.folder !== folder) {
            shouldUpdate = true;
        }
        if (this.isHidden || !shouldUpdate) {
            return;
        }
        this._model.folder = folder;
        (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('launch?folder=' + folder)
            .then(d => {
            delete this._model.error;
            this._model.launch = d;
            this._model.changed.emit();
        })
            .catch(d => {
            this._model.error = d;
            this._model.changed.emit();
        });
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.UseSignal, { signal: this._model.changed, initialSender: this._model }, () => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(AutomationControl, { model: this._model, commands: this._commands, openFolder: this._openFolder, openPath: this._openPath }))));
    }
}
const AutomationControl = ({ model, commands, openFolder, openPath }) => {
    const { error } = model;
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
        error ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(ErrorContent, { model: model, openFolder: openFolder, openPath: openPath })) : (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(AutomationContent, { model: model, commands: commands, openFolder: openFolder, openPath: openPath })),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(AutomationReference, null)));
};
const ErrorContent = ({ model, openFolder, openPath }) => {
    const { error } = model;
    const message = error === null || error === void 0 ? void 0 : error.message;
    const code = error === null || error === void 0 ? void 0 : error.code;
    const path = error === null || error === void 0 ? void 0 : error.path;
    let content;
    switch (code) {
        case _constant__WEBPACK_IMPORTED_MODULE_3__.ErrorCode.configurationNotFound: {
            const { launch } = model;
            const { folder, name, version } = launch;
            content = folder ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", onClick: () => openFolder(folder) }, name ? `${name} ${version}` : 'Automation Folder')) : ('');
            break;
        }
        default: {
            content = path ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", onClick: () => openPath(path) }, message)) : (message);
        }
    }
    return react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null, content);
};
const AutomationContent = ({ model, commands, openFolder, openPath }) => {
    const { launch } = model;
    const { path, name, version } = launch;
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationInformation" },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationInformationHeader" },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationName" }, name || 'No Name'),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationVersion" }, version || 'No Version')),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationInformationBody" },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", onClick: () => openPath(path) }, "Automation Configuration"),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(BatchDefinitions, { model: model, openFolder: openFolder, openPath: openPath }),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(LaunchPanel, { model: model, commands: commands }))));
};
const BatchDefinitions = ({ model, openFolder, openPath }) => {
    const { launch } = model;
    const { folder, batches } = launch;
    return batches.length ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-BatchDefinitions" },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-BatchDefinitionsHeader" }, "Batch Definitions"),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("ul", null, batches.map((d, i) => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("li", { key: i },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", onClick: () => {
                    if (d.configuration) {
                        openPath(folder + '/' + d.configuration.path);
                    }
                    else {
                        openFolder(d.folder);
                    }
                } }, d.name || d.folder))))))) : (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null));
};
const LaunchPanel = ({ model, commands }) => {
    const { launch } = model;
    const { folder } = launch;
    const { uri, log, isReady } = launch;
    const formData = new FormData();
    formData.append('folder', folder);
    let launchIntervalId, logIntervalId;
    const clearIntervals = () => {
        clearInterval(launchIntervalId);
        clearInterval(logIntervalId);
    };
    const onClickStart = () => {
        commands.execute('docmanager:save-all');
        launch.isReady = false;
        model.changed.emit();
        (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('launch', { method: 'POST', body: formData })
            .then(d => {
            const { uri } = d;
            launch.uri = uri;
            model.changed.emit();
        })
            .catch(d => {
            model.error = d;
            model.changed.emit();
        });
    };
    const onClickStop = () => {
        clearIntervals();
        delete launch.isReady;
        delete launch.log;
        model.changed.emit();
        (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('launch', { method: 'DELETE', body: formData }).catch(d => {
            model.error = d;
            model.changed.emit();
        });
    };
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        if (isReady === false && uri) {
            launchIntervalId = setInterval(() => {
                fetch(uri, { method: 'HEAD' }).then(() => {
                    launch.isReady = true;
                    model.changed.emit();
                    clearInterval(launchIntervalId);
                });
            }, 1000);
        }
        if (isReady !== undefined) {
            logIntervalId = setInterval(() => {
                (0,_handler__WEBPACK_IMPORTED_MODULE_4__.requestAPI)('log?type=launch&folder=' + folder).then(d => {
                    var _a;
                    if (((_a = launch.log) === null || _a === void 0 ? void 0 : _a.timestamp) !== d.timestamp) {
                        launch.log = d;
                        model.changed.emit();
                    }
                });
            }, 2000);
        }
        return () => {
            clearIntervals();
        };
    }, [isReady, uri]);
    let link;
    if (isReady === undefined) {
        link = '';
    }
    else if (isReady === false) {
        link = 'Launching...';
    }
    else {
        link = (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", href: uri, target: "_blank" }, "Development Server"));
    }
    const button = isReady === undefined ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { onClick: onClickStart }, "Launch")) : (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("button", { onClick: onClickStop }, "Stop"));
    const information = isReady !== undefined && log ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("pre", { className: "crosscompute-LaunchLog" }, log.text)) : ('');
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-LaunchPanel" },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-LaunchControl" },
            link,
            button),
        information));
};
const AutomationReference = () => {
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { className: "crosscompute-AutomationReference" },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("a", { className: "crosscompute-Link", href: "https://docs.crosscompute.com", target: "_blank" }, "CrossCompute Documentation")));
};


/***/ }),

/***/ "./lib/constant.js":
/*!*************************!*\
  !*** ./lib/constant.js ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ErrorCode": () => (/* binding */ ErrorCode),
/* harmony export */   "logoIcon": () => (/* binding */ logoIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _style_icons_Logo_SmallFormat_20220127_svg__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../style/icons/Logo-SmallFormat-20220127.svg */ "./style/icons/Logo-SmallFormat-20220127.svg");


const logoIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'crosscompute:logo',
    svgstr: _style_icons_Logo_SmallFormat_20220127_svg__WEBPACK_IMPORTED_MODULE_1__["default"]
});
var ErrorCode;
(function (ErrorCode) {
    ErrorCode.configurationNotFound = -100;
})(ErrorCode || (ErrorCode = {}));


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
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab-crosscompute', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    const d = await response.json();
    if (!response.ok) {
        throw d;
    }
    return d;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/filebrowser */ "webpack/sharing/consume/default/@jupyterlab/filebrowser");
/* harmony import */ var _jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _body__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./body */ "./lib/body.js");



// import { ISettingRegistry } from '@jupyterlab/settingregistry';

/**
 * Initialization data for the jupyterlab-crosscompute extension.
 */
const plugin = {
    id: 'jupyterlab-crosscompute:plugin',
    autoStart: true,
    requires: [_jupyterlab_filebrowser__WEBPACK_IMPORTED_MODULE_2__.IFileBrowserFactory, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabShell, _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_1__.IDocumentManager],
    optional: [
        // ISettingRegistry
        _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer
    ],
    activate: (app, browserFactory, labShell, docManager, 
    // settingRegistry?: ISettingRegistry,
    restorer) => {
        const { shell, commands } = app;
        const browser = browserFactory.defaultBrowser;
        const browserModel = browser.model;
        const openFolder = (folder) => {
            labShell.activateById(browser.id);
            browserModel.cd(folder);
        };
        const openPath = (path) => docManager.openOrReveal(path);
        const automationBody = new _body__WEBPACK_IMPORTED_MODULE_3__.AutomationBody(commands, openFolder, openPath);
        const refresh = () => automationBody.updateModel({ folder: '/' + browserModel.path });
        browserModel.pathChanged.connect(refresh);
        labShell.layoutModified.connect(refresh);
        shell.add(automationBody, 'right', { rank: 1000 });
        /*
        if (settingRegistry) {
          settingRegistry
            .load(plugin.id)
            .then(settings => {
              console.log('jupyterlab-crosscompute settings loaded:', settings.composite);
            })
            .catch(reason => {
              console.error('Failed to load settings for jupyterlab-crosscompute.', reason);
            });
        }
        */
        if (restorer) {
            restorer.add(automationBody, automationBody.id);
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/model.js":
/*!**********************!*\
  !*** ./lib/model.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "AutomationModel": () => (/* binding */ AutomationModel)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);

class AutomationModel {
    constructor() {
        // Folder used for most recent update
        this.folder = null;
        // Error state from extension server
        this.error = {};
        // Launch state from extension server
        this.launch = {};
        // Signal to refresh widget
        this.changed = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal(this);
    }
}


/***/ }),

/***/ "./style/icons/Logo-SmallFormat-20220127.svg":
/*!***************************************************!*\
  !*** ./style/icons/Logo-SmallFormat-20220127.svg ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ("<svg width=\"48\" height=\"48\" enable-background=\"new 0 0 48 48\" version=\"1.1\" viewBox=\"0 0 48 48\" xmlns=\"http://www.w3.org/2000/svg\">\n <style type=\"text/css\">.st0{display:none;opacity:0;fill:#FFFFFF;}\n\t.st1{fill:#939598;}\n\t.st2{fill:#F63806;}\n\t.st3{fill:#148ED5;}\n\t.st4{fill:#D43105;}\n\t.st5{fill:#17A2F5;}\n\t.st6{fill:#284454;}</style>\n <rect id=\"a\" class=\"st0\" x=\"-236.5\" y=\"-238.04\" width=\"519.1\" height=\"519.1\"/>\n <g transform=\"matrix(.9465 0 0 .9465 1.284 .71797)\">\n  <g id=\"b\">\n   <path id=\"c\" class=\"st1\" d=\"m29.1 11.9c1.2 0.5 2.4 1.2 3.4 2l5.4-8.1c-2.1-1.6-4.4-2.8-7-3.6-0.7-0.2-1.4 0.2-1.5 1l-1 7.5c-0.1 0.5 0.2 1 0.7 1.2z\"/>\n   <path id=\"d\" class=\"st1\" d=\"m29.1 37.2c-0.5 0.2-0.8 0.7-0.7 1.2l1 7.5c0.1 0.7 0.8 1.2 1.5 1 2.5-0.8 4.9-2 7-3.6l-5.4-8.1c-1 0.8-2.2 1.5-3.4 2z\"/>\n   <path id=\"e\" class=\"st1\" d=\"m18.8 37.2c-1.2-0.5-2.4-1.2-3.4-2l-5.4 8.1c2.1 1.6 4.4 2.8 7 3.6 0.7 0.2 1.4-0.2 1.5-1l1-7.5c0.1-0.5-0.2-1-0.7-1.2z\"/>\n   <path id=\"f\" class=\"st1\" d=\"m18.5 3.1c-0.1-0.7-0.8-1.2-1.5-1-2.5 0.8-4.9 2-7 3.6l5.4 8.1c1-0.8 2.1-1.5 3.4-2 0.5-0.2 0.8-0.7 0.7-1.2z\"/>\n   <path id=\"g\" class=\"st1\" d=\"m26.3 2.9h-4.6c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6h4.6c0.3 0 0.6-0.3 0.6-0.6s-0.2-0.6-0.6-0.6z\"/>\n   <path id=\"h\" class=\"st1\" d=\"m26.6 6.6c0-0.3-0.3-0.6-0.6-0.6h-3.9c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6h3.9c0.3 0 0.6-0.2 0.6-0.6z\"/>\n   <path id=\"i\" class=\"st1\" d=\"m25.6 9.1h-3.2c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6h3.2c0.3 0 0.6-0.3 0.6-0.6 0.1-0.3-0.2-0.6-0.6-0.6z\"/>\n   <path id=\"j\" class=\"st1\" d=\"m26.3 45h-4.6c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6h4.6c0.3 0 0.6-0.3 0.6-0.6s-0.2-0.6-0.6-0.6z\"/>\n   <path id=\"k\" class=\"st1\" d=\"m22.1 43.2h3.9c0.3 0 0.6-0.3 0.6-0.6s-0.3-0.6-0.6-0.6h-3.9c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6z\"/>\n   <path id=\"l\" class=\"st1\" d=\"m25.6 38.9h-3.2c-0.3 0-0.6 0.3-0.6 0.6s0.3 0.6 0.6 0.6h3.2c0.3 0 0.6-0.3 0.6-0.6s-0.2-0.6-0.6-0.6z\"/>\n  </g>\n  <path id=\"m\" class=\"st2\" d=\"m37.9 5.7-5.4 8.1c3.1 2.5 5.2 6.4 5.2 10.7s-2 8.2-5.2 10.7l5.4 8.1c5.7-4.3 9.5-11.1 9.5-18.8s-3.8-14.5-9.5-18.8z\"/>\n  <path id=\"n\" class=\"st3\" d=\"m10.1 43.3 5.4-8.1c-3.1-2.5-5.2-6.4-5.2-10.7s2-8.2 5.2-10.7l-5.4-8.1c-5.8 4.3-9.5 11.1-9.5 18.8s3.7 14.5 9.5 18.8z\"/>\n  <g id=\"o\">\n   <path id=\"p\" class=\"st4\" d=\"m40.2 37.3c-0.3-0.3-0.8-0.2-1 0.1s-0.5 0.6-0.8 0.9-0.2 0.8 0.1 1c0.1 0.1 0.3 0.2 0.5 0.2s0.4-0.1 0.5-0.2c0.3-0.3 0.6-0.6 0.8-1 0.2-0.3 0.2-0.7-0.1-1z\"/>\n   <path id=\"q\" class=\"st4\" d=\"m44.4 18.4c-0.1-0.4-0.5-0.6-0.9-0.5s-0.6 0.5-0.5 0.9c0.5 1.8 0.7 3.7 0.7 5.5 0 4-1.1 7.8-3.2 11.2-0.2 0.3-0.1 0.8 0.2 1 0.1 0.1 0.3 0.1 0.4 0.1 0.2 0 0.5-0.1 0.6-0.3 2.3-3.6 3.4-7.7 3.4-12 0.1-2-0.2-4-0.7-5.9z\"/>\n  </g>\n  <g id=\"r\">\n   <path id=\"s\" class=\"st5\" d=\"m9.4 9.7c-0.2-0.1-0.3-0.2-0.5-0.2s-0.4 0.1-0.5 0.2c-0.3 0.3-0.6 0.6-0.8 1-0.3 0.3-0.2 0.8 0.1 1 0.3 0.3 0.8 0.2 1-0.1s0.5-0.6 0.8-0.9c0.2-0.3 0.2-0.7-0.1-1z\"/>\n   <path id=\"t\" class=\"st5\" d=\"m7 12.6c-0.1-0.1-0.3-0.1-0.4-0.1-0.2 0-0.5 0.1-0.6 0.3-2.3 3.6-3.4 7.7-3.4 12 0 2 0.3 4 0.8 5.9 0.1 0.4 0.5 0.6 0.9 0.5s0.6-0.5 0.5-0.9c-0.5-1.8-0.8-3.7-0.8-5.5 0-4 1.1-7.8 3.2-11.2 0.3-0.3 0.2-0.8-0.2-1z\"/>\n  </g>\n  <path class=\"st6\" d=\"m45.6 13.5c-1.6-3-3.8-5.8-6.5-7.9l-1.4-1c-2-1.4-4.2-2.4-6.5-3.2-0.6-0.2-1.2-0.1-1.7 0.2s-0.8 0.8-0.9 1.4l-1 7.5c-0.1 0.9 0.4 1.8 1.2 2.1 1.1 0.5 2.2 1.1 3.2 1.9 3.1 2.5 4.8 6.1 4.9 10 0 3.9-1.8 7.6-4.9 10-1 0.8-2 1.4-3.2 1.9-0.9 0.3-1.4 1.2-1.2 2.1l1 7.5c0.1 0.6 0.4 1.1 0.9 1.4 0.3 0.2 0.7 0.3 1.1 0.3 0.2 0 0.4 0 0.6-0.1 2.3-0.7 4.5-1.8 6.5-3.2l1.4-1c2.7-2.1 4.9-4.9 6.5-7.9 1.8-3.4 2.7-7.2 2.7-11.1-0.1-3.8-1-7.5-2.7-10.9zm-8.9 29.6c-1.9 1.3-3.9 2.3-6.1 2.9h-0.3c-0.1 0-0.1-0.1-0.1-0.2l-1-7.5c0-0.1 0.1-0.3 0.2-0.3 1-0.4 1.9-0.9 2.8-1.5zm0-37.1-4.4 6.6c-0.9-0.6-1.8-1.1-2.8-1.5-0.1-0.1-0.2-0.2-0.2-0.3l1-7.5c0-0.1 0.1-0.2 0.1-0.2h0.3c2.1 0.6 4.2 1.6 6 2.9zm1.8 18.5c0-4.2-1.8-8.1-4.9-10.9l4.5-6.6c0.2 0.2 0.4 0.4 0.7 0.6l-3.8 5.4c-0.1 0.2-0.2 0.4-0.1 0.6 0 0.2 0.2 0.4 0.3 0.6 0.4 0.3 0.9 0.2 1.2-0.2l3.6-5.3 0.5 0.5-2.9 3.9c-0.3 0.4-0.2 0.9 0.2 1.2s0.9 0.2 1.2-0.2l2.7-3.6c0.1 0.2 0.3 0.3 0.4 0.5l-1.8 2.2c-0.3 0.4-0.2 0.9 0.1 1.2 0.4 0.3 0.9 0.2 1.2-0.1l1.4-1.8c2.3 3.6 3.5 7.7 3.5 12 0 6.7-3.2 13.3-8.4 17.5l-4.5-6.7c3.1-2.7 4.9-6.6 4.9-10.8z\"/>\n  <path class=\"st6\" d=\"m19.2 36.4c-1.2-0.5-2.2-1.1-3.2-1.8-3.1-2.5-4.8-6.1-4.9-10 0-3.9 1.8-7.6 4.9-10 1-0.8 2-1.4 3.2-1.9 0.9-0.3 1.4-1.2 1.2-2.1l-1-7.5c-0.1-0.6-0.4-1.1-0.9-1.4s-1.1-0.4-1.7-0.2c-2.3 0.7-4.5 1.8-6.5 3.2l-1.4 1c-2.7 2-4.9 4.7-6.5 7.8-1.8 3.4-2.7 7.2-2.7 11.1s0.9 7.6 2.7 11.1c1.6 3 3.8 5.8 6.5 7.9l1.4 1c2 1.4 4.2 2.4 6.5 3.2 0.2 0.1 0.4 0.1 0.6 0.1 0.4 0 0.8-0.1 1.1-0.3 0.5-0.3 0.8-0.8 0.9-1.4l1-7.5c0.1-1.1-0.4-1.9-1.2-2.3zm-1.5-33.1 1 7.5c0 0.1-0.1 0.3-0.2 0.3-1 0.4-1.9 0.9-2.8 1.5l-4.5-6.6c1.9-1.3 3.9-2.3 6.1-2.9h0.3s0.1 0 0.1 0.2zm-4.7 32.8c0.1-0.2 0.2-0.4 0.1-0.6 0-0.2-0.2-0.4-0.3-0.6-0.2-0.1-0.4-0.2-0.6-0.1-0.2 0-0.4 0.2-0.6 0.3l-3.6 5.2-0.5-0.5 2.9-3.9c0.3-0.4 0.2-0.9-0.2-1.2-0.2-0.1-0.4-0.2-0.6-0.2s-0.4 0.2-0.6 0.3l-2.7 3.6c-0.1-0.1-0.2-0.2-0.3-0.4l1.7-2.2c0.1-0.2 0.2-0.4 0.2-0.6s-0.1-0.4-0.3-0.6c-0.2-0.1-0.4-0.2-0.6-0.2s-0.4 0.1-0.6 0.3l-1.4 1.8c-2.3-3.6-3.5-7.7-3.5-12 0-6.7 3.2-13.3 8.4-17.5l4.5 6.7c-3.1 2.8-4.9 6.7-4.9 10.9s1.8 8.1 4.9 10.9l-4.5 6.7c-0.2-0.2-0.4-0.4-0.7-0.6zm5.7 2.2-1 7.5c0 0.1-0.1 0.2-0.1 0.2-0.1 0-0.1 0.1-0.3 0-2.2-0.7-4.2-1.7-6.1-2.9l4.4-6.6c0.9 0.6 1.8 1.1 2.8 1.5 0.3 0 0.3 0.2 0.3 0.3z\"/>\n  <path id=\"u\" class=\"st6\" d=\"m33 24.6c0-5-4-9-9-9s-9 4-9 9 4 9 9 9 9-4.1 9-9zm-9.8 7.5c-3.8-0.4-6.7-3.6-6.7-7.5 0-0.7 0.1-1.3 0.2-1.9l4.3 4.6v1.6c0 0.4 0.6 0.9 1 0.9h0.9c0.1 0 0.2 0.1 0.2 0.2v2.1zm6.3-3.2c-0.1-0.3-0.3-0.5-0.6-0.5h-1.8v-2.4c0-0.7-0.5-1.2-1.2-1.2l-5.7-0.1v-2.1h1.5c0.8 0 1.5-0.7 1.5-1.5v-1.7h2.8s1.1-0.6 1.6-1.4c2.4 1.3 4 3.8 4 6.7 0 1.9-0.7 3.7-1.9 5z\"/>\n </g>\n</svg>\n");

/***/ })

}]);
//# sourceMappingURL=lib_index_js.db990ae0d4f1c92ec1b6.js.map