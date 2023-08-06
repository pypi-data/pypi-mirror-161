#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Florian Jaeger.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode, Integer, Any, Dict
from ._frontend import module_name, module_version

class RhinoViewer(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('RhinoModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('RhinoView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    path = Unicode('').tag(sync=True)
    width = Integer(1000).tag(sync=True)
    height = Integer(700).tag(sync=True)
    background_color = Any('rgb(255,255,255)').tag(sync=True)
    camera_pos = Dict(default_value={"x": 15, "y": 15, "z": 15}).tag(sync=True)
