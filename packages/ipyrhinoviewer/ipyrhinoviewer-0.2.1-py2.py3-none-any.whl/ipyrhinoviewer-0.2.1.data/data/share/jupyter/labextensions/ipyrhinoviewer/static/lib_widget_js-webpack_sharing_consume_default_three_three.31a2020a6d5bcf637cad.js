(self["webpackChunkipyrhinoviewer"] = self["webpackChunkipyrhinoviewer"] || []).push([["lib_widget_js-webpack_sharing_consume_default_three_three"],{

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) Florian Jaeger
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;
//# sourceMappingURL=version.js.map

/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// Copyright (c) Florian Jaeger
// Distributed under the terms of the Modified BSD License.
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.RhinoView = exports.RhinoModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const THREE = __importStar(__webpack_require__(/*! three */ "webpack/sharing/consume/default/three/three?90a2"));
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
const OrbitControls_1 = __webpack_require__(/*! three/examples/jsm/controls/OrbitControls */ "./node_modules/three/examples/jsm/controls/OrbitControls.js");
const _3DMLoader_1 = __webpack_require__(/*! three/examples/jsm/loaders/3DMLoader */ "./node_modules/three/examples/jsm/loaders/3DMLoader.js");
// Import the CSS
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
class RhinoModel extends base_1.DOMWidgetModel {
    defaults() {
        return {
            ...super.defaults(),
            _model_name: RhinoModel.model_name,
            _model_module: RhinoModel.model_module,
            _model_module_version: RhinoModel.model_module_version,
            _view_name: RhinoModel.view_name,
            _view_module: RhinoModel.view_module,
            _view_module_version: RhinoModel.view_module_version,
            path: '',
            height: 700,
            width: 1000,
            background_color: 'rgb(255, 255, 255)',
            camera_pos: { x: 15, y: 15, z: 15 },
        };
    }
}
exports.RhinoModel = RhinoModel;
RhinoModel.serializers = {
    ...base_1.DOMWidgetModel.serializers,
};
RhinoModel.model_name = 'RhinoModel';
RhinoModel.model_module = version_1.MODULE_NAME;
RhinoModel.model_module_version = version_1.MODULE_VERSION;
RhinoModel.view_name = 'RhinoView'; // Set to null if no view
RhinoModel.view_module = version_1.MODULE_NAME; // Set to null if no view
RhinoModel.view_module_version = version_1.MODULE_VERSION;
function load3dmModel(scene, filePath, options) {
    const { receiveShadow, castShadow } = options;
    return new Promise((resolve, reject) => {
        const loader = new _3DMLoader_1.Rhino3dmLoader();
        loader.setLibraryPath('https://cdn.jsdelivr.net/npm/rhino3dm@0.15.0-beta/');
        loader.load(filePath, (data) => {
            const obj = data;
            obj.position.y = 0;
            obj.position.x = 0;
            obj.position.z = 0;
            obj.receiveShadow = receiveShadow;
            obj.castShadow = castShadow;
            scene.add(obj);
            obj.traverse((child) => {
                if (child.isObject3D) {
                    child.castShadow = castShadow;
                    child.receiveShadow = receiveShadow;
                }
            });
            resolve(obj);
        }, undefined, (error) => {
            console.log(error);
            reject(error);
        });
    });
}
class RhinoView extends base_1.DOMWidgetView {
    constructor() {
        super(...arguments);
        this.path = this.model.get('path');
        this.width = this.model.get('width');
        this.height = this.model.get('height');
        this.background_color = this.model.get('background_color');
        this.postion = this.model.get('camera_pos');
    }
    showError(msg) {
        const error = document.createElement('p');
        error.textContent = msg;
        this.el.appendChild(error);
        const loading = document.getElementById('loading');
        if (loading !== null) {
            this.el.removeChild(loading);
        }
    }
    render() {
        const loading = document.createElement('p');
        loading.id = 'loading';
        loading.textContent = 'Loading';
        this.el.appendChild(loading);
        if (this.width < 100 || this.width > 3000) {
            this.showError('Error: width must be in range of 100-3000');
            return;
        }
        if (this.height < 100 || this.height > 3000) {
            this.showError('Error: height must be in range of 100-3000');
            return;
        }
        if (this.path === '') {
            this.showError('Error: path is required');
            return;
        }
        if (this.path.split('.').pop() !== '3dm') {
            this.showError('Error: path should lead to a 3dm file');
            return;
        }
        const scene = new THREE.Scene();
        try {
            scene.background = new THREE.Color(this.background_color);
        }
        catch (error) {
            this.showError(error);
            return;
        }
        const camera = new THREE.PerspectiveCamera(50, this.width / this.height, 1, 1000);
        const renderer = new THREE.WebGLRenderer();
        renderer.setSize(this.width, this.height);
        const ambientLight = new THREE.AmbientLight(0xcccccc, 2);
        scene.add(ambientLight);
        const controls = new OrbitControls_1.OrbitControls(camera, renderer.domElement);
        const onContextMenu = (event) => {
            event.stopPropagation();
        };
        this.el.addEventListener('contextmenu', onContextMenu);
        load3dmModel(scene, '/tree/' + this.path, {
            receiveShadow: true,
            castShadow: true,
        })
            .then(() => {
            this.el.removeChild(loading);
            this.el.appendChild(renderer.domElement);
            this.value_changed();
            this.model.on('change:value', this.value_changed, this);
            animate();
        })
            .catch(() => {
            this.showError('Error: path "' + this.model.get('path') + '" was not found');
            return;
        });
        camera.position.x = this.postion.x;
        camera.position.y = this.postion.y;
        camera.position.z = this.postion.z;
        const tracker = document.createElement('p');
        this.el.onselectstart = () => {
            return false;
        };
        this.el.classList.add('border');
        this.el.appendChild(tracker);
        camera.lookAt(0, 0, 0);
        let frame = 0;
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            if (frame === 20) {
                tracker.textContent =
                    'camera position: x: ' +
                        camera.position.x.toString() +
                        ' y: ' +
                        camera.position.y.toString() +
                        ' z: ' +
                        camera.position.z.toString();
                frame = 0;
            }
            frame++;
            renderer.render(scene, camera);
        }
        animate();
    }
    value_changed() {
        this.path = this.model.get('path');
    }
}
exports.RhinoView = RhinoView;
//# sourceMappingURL=widget.js.map

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./css/widget.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/widget.css ***!
  \**************************************************************/
/***/ ((module, exports, __webpack_require__) => {

// Imports
var ___CSS_LOADER_API_IMPORT___ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
exports = ___CSS_LOADER_API_IMPORT___(false);
// Module
exports.push([module.id, ".border {\n  border-radius: 25px;\n  border: 2px solid rgba(32, 32, 16, 0);\n  padding: 20px;\n  width: 200px;\n  height: 150px;\n}", ""]);
// Exports
module.exports = exports;


/***/ }),

/***/ "./css/widget.css":
/*!************************!*\
  !*** ./css/widget.css ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./widget.css */ "./node_modules/css-loader/dist/cjs.js!./css/widget.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"ipyrhinoviewer","version":"0.2.0","description":"A Custom Jupyter Rhino Viewer","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/TU-Wien-dataLAB/ipyrhinoviewer","bugs":{"url":"https://github.com/TU-Wien-dataLAB/ipyrhinoviewer/issues"},"license":"BSD-3-Clause","author":{"name":"Florian Jaeger","email":"florian.jaeger@tuwien.ac.at"},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/TU-Wien-dataLAB/ipyrhinoviewer"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ipyrhinoviewer/labextension","clean:nbextension":"rimraf ipyrhinoviewer/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","@types/three":"^0.142.0","three":"^0.142.0"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/jest":"^26.0.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.61.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ipyrhinoviewer/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js-webpack_sharing_consume_default_three_three.31a2020a6d5bcf637cad.js.map