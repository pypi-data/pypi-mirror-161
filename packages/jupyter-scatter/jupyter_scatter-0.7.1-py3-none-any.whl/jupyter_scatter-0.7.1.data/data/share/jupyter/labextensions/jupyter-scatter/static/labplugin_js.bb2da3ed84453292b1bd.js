(self["webpackChunkjupyter_scatter"] = self["webpackChunkjupyter_scatter"] || []).push([["labplugin_js"],{

/***/ "./index.js":
/*!******************!*\
  !*** ./index.js ***!
  \******************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// Export widget models and views, and the npm package version number.
module.exports = __webpack_require__(/*! ./src/index.js */ "./src/index.js");
module.exports.version = __webpack_require__(/*! ./package.json */ "./package.json").version;


/***/ }),

/***/ "./labplugin.js":
/*!**********************!*\
  !*** ./labplugin.js ***!
  \**********************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

const plugin = __webpack_require__(/*! ./index */ "./index.js");
const base = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const widgetName = __webpack_require__(/*! ./package.json */ "./package.json").name;

module.exports = {
  id: 'jupyter.extensions.' + widgetName,
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
    widgets.registerWidget({
      name: widgetName,
      version: plugin.version,
      exports: plugin
    });
  },
  autoStart: true
};


/***/ })

}]);
//# sourceMappingURL=labplugin_js.bb2da3ed84453292b1bd.js.map