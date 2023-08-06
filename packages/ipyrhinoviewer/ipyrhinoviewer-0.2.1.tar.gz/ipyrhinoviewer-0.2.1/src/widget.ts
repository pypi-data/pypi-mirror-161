// Copyright (c) Florian Jaeger
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';
import * as THREE from 'three';
import { MODULE_NAME, MODULE_VERSION } from './version';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { Rhino3dmLoader } from 'three/examples/jsm/loaders/3DMLoader';

// Import the CSS
import '../css/widget.css';

export class RhinoModel extends DOMWidgetModel {
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

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'RhinoModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'RhinoView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

function load3dmModel(
  scene: THREE.Scene,
  filePath: string,
  options: { receiveShadow: any; castShadow: any }
) {
  const { receiveShadow, castShadow } = options;
  return new Promise((resolve, reject) => {
    const loader = new Rhino3dmLoader();
    loader.setLibraryPath('https://cdn.jsdelivr.net/npm/rhino3dm@0.15.0-beta/');
    loader.load(
      filePath,
      (data: any) => {
        const obj = data;
        obj.position.y = 0;
        obj.position.x = 0;
        obj.position.z = 0;
        obj.receiveShadow = receiveShadow;
        obj.castShadow = castShadow;
        scene.add(obj);

        obj.traverse((child: any) => {
          if (child.isObject3D) {
            child.castShadow = castShadow;
            child.receiveShadow = receiveShadow;
          }
        });

        resolve(obj);
      },
      undefined,
      (error: any) => {
        console.log(error);
        reject(error);
      }
    );
  });
}

export class RhinoView extends DOMWidgetView {
  private path: string = this.model.get('path');
  private width: number = this.model.get('width');
  private height: number = this.model.get('height');
  private background_color: number | string =
    this.model.get('background_color');
  private postion: { x: number; y: number; z: number } =
    this.model.get('camera_pos');

  showError(msg: string) {
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
    } catch (error) {
      this.showError(error);
      return;
    }
    const camera = new THREE.PerspectiveCamera(
      50,
      this.width / this.height,
      1,
      1000
    );

    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(this.width, this.height);

    const ambientLight = new THREE.AmbientLight(0xcccccc, 2);
    scene.add(ambientLight);
    const controls = new OrbitControls(camera, renderer.domElement);
    const onContextMenu = (event: Event) => {
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
        this.showError(
          'Error: path "' + this.model.get('path') + '" was not found'
        );
        return;
      });

    camera.position.x = this.postion.x;
    camera.position.y = this.postion.y;
    camera.position.z = this.postion.z;
    const tracker = document.createElement('p');
    this.el.onselectstart = () => {
      return false;
    };
    renderer.domElement.classList.add('border');
    this.el.appendChild(tracker);
    camera.lookAt(0, 0, 0);
    let frame = 0;
    function animate() {
      requestAnimationFrame(animate);
      controls.update();
      if (frame === 50) {
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

  value_changed(): void {
    this.path = this.model.get('path');
  }
}
