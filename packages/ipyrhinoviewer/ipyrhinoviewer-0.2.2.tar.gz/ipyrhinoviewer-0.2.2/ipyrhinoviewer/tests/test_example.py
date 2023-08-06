#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Florian Jaeger.
# Distributed under the terms of the Modified BSD License.

import pytest

from ..widget import RhinoViewer


def test_example_creation_blank():
    w = RhinoViewer()
    assert w.value == 'rhino.3dm'
