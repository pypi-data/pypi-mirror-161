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
      show_axes: true,
      grid: null,
      ambient_light: null,
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

const load3dmModel = (
  scene: THREE.Scene,
  filePath: string,
  options: { receiveShadow: any; castShadow: any }
) => {
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
};

export class RhinoView extends DOMWidgetView {
  private path: string = this.model.get('path');
  private width: number = this.model.get('width');
  private height: number = this.model.get('height');
  private background_color: number | string =
    this.model.get('background_color');
  private postion: { x: number; y: number; z: number } =
    this.model.get('camera_pos');
  private show_axes: boolean = this.model.get('show_axes');
  private grid: { size: number; divisions: number } | null =
    this.model.get('grid');
  private scene: THREE.Scene;
  private ambientLight: { color: string; intensity: number } =
    this.model.get('ambient_light');

  render() {
    //add a loading element while loading
    const loading = document.createElement('p');
    loading.id = 'loading';
    loading.textContent = 'Loading';
    this.el.appendChild(loading);

    //check parameters
    try {
      this.checkParams();
    } catch (e) {
      this.showError(e.message);
      return;
    }

    //create scene
    this.scene = new THREE.Scene();

    //set background color
    try {
      this.scene.background = new THREE.Color(this.background_color);
    } catch (error) {
      this.showError(error);
      return;
    }
    //create camera
    const camera = new THREE.PerspectiveCamera(
      50,
      this.width / this.height,
      1,
      1000
    );

    //set renderer window based on parameters
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(this.width, this.height);

    this.addHelpersElements();

    this.handleLighting();

    const controls = new OrbitControls(camera, renderer.domElement);
    //Stops opening the context menu on right click
    const onContextMenu = (event: Event) => {
      event.stopPropagation();
    };
    this.el.addEventListener('contextmenu', onContextMenu);

    //Load the file
    load3dmModel(this.scene, '/tree/' + this.path, {
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

    //position camera
    camera.position.x = this.postion.x;
    camera.position.y = this.postion.y;
    camera.position.z = this.postion.z;
    //add a camera coordinates tracker
    const tracker = document.createElement('p');
    this.el.onselectstart = () => {
      return false;
    };
    renderer.domElement.classList.add('border');
    this.el.appendChild(tracker);

    camera.lookAt(0, 0, 0);
    let frame = 0;
    const animate = () => {
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
      renderer.render(this.scene, camera);
    };

    animate();
  }

  private handleLighting(): void {
    if (this.ambientLight !== null) {
      const ambientLight = new THREE.AmbientLight(
        this.ambientLight.color,
        this.ambientLight.intensity
      );
      this.scene.add(ambientLight);
    }
    /*

    const spotLight = new THREE.SpotLight(0xffffff, 2);
    spotLight.position.set(0, 0, 100);
    spotLight.castShadow = true;
    spotLight.shadow.mapSize.width = 1024;
    spotLight.shadow.mapSize.height = 1024;

    spotLight.shadow.camera.near = 500;
    spotLight.shadow.camera.far = 4000;
    spotLight.shadow.camera.fov = 30;
    this.scene.add(spotLight);*/
  }

  private addHelpersElements() {
    if (this.show_axes) {
      const axesHelper = new THREE.AxesHelper(200);
      this.scene.add(axesHelper);
    }

    if (this.grid !== null) {
      const gridHelper = new THREE.GridHelper(
        this.grid.size,
        this.grid.divisions
      );
      this.scene.add(gridHelper);
    }
  }

  showError(msg: string): void {
    const error = document.createElement('p');
    error.textContent = msg;
    this.el.appendChild(error);
    const loading = document.getElementById('loading');
    if (loading !== null) {
      this.el.removeChild(loading);
    }
  }

  value_changed(): void {
    this.path = this.model.get('path');
  }

  private checkParams() {
    if (this.width < 100 || this.width > 3000) {
      throw new Error('Error: width must be in range of 100-3000');
    }
    if (this.height < 100 || this.height > 3000) {
      throw new Error('Error: height must be in range of 100-3000');
    }
    if (this.path === '') {
      throw new Error('Error: path is required');
    }
    if (this.path.split('.').pop() !== '3dm') {
      throw new Error('Error: path should lead to a 3dm file');
    }
  }
}
