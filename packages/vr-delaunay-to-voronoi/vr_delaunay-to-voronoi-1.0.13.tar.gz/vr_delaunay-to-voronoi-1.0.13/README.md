# VR.Delaunay-To-Voronoi

Convert from Delaunay tesselation to Voronoi triangulation.
In contrast to qHull, this provides edges of Voronoi triangulations.

## Visualization

![](https://gitlab.com/dfki/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/-/raw/main/_images/scatter_delaunay_voronoi.png)

## Features

-   Largely typed
-   Reasonably quick
-   Fully tested

## Problem Statement

qHull provides edges, but not vertices of Voronoi triangulations.
To gather the edges and the vertices, this library derives them from the
  Delaunay tesselation.

## Approach

The Delaunay tesselation is calculated by qHull.
This provides a stable and known-good base to derive from.

## Mental Model

-   TODO

## Status

[![pipeline status](https://gitlab.com/dfki/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/badges/main/pipeline.svg)](https://gitlab.com/dfki/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/-/pipelines/latest)
&nbsp;
[![coverage report](https://gitlab.com/dfki/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/badges/main/coverage.svg)](https://gitlab.com/dfki/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/-/jobs)
&nbsp;
[![PyPI Status](https://img.shields.io/pypi/status/vr.delaunay-to-voronoi)](https://pypi.org/project/vr-delaunay-to-voronoi/)
&nbsp;
[![PyPI Version](https://img.shields.io/pypi/v/vr_delaunay_to_voronoi)](https://pypi.org/project/vr-delaunay-to-voronoi/#history)
&nbsp;
[![PyPI License Badge](https://img.shields.io/pypi/l/vr_delaunay_to_voronoi)](https://pypi.org/project/vr-delaunay-to-voronoi/)
&nbsp;
[![Wheel Badge](https://img.shields.io/pypi/wheel/vr_delaunay_to_voronoi)](https://pypi.org/project/vr-delaunay-to-voronoi/#files)
&nbsp;
[![Python Versions](https://img.shields.io/pypi/pyversions/vr_delaunay_to_voronoi)](https://pypi.org/project/vr-delaunay-to-voronoi/)

## License

This package is not licensed. Therefore, it can only be used in the DFKI.

## Usage

This package originates from and is being used in production
    at the [VR.Backend](https://git.ni.dfki.de/iml/vr/vr.backend) project.
However,
    the VR.Backend project is currently internal to the DFKI.

## Demo

-   TODO

## Development

For development and maintenance of this project,
  see the [development documentation](README_DEVELOPERS.md).

## Documentation

For more complete documentation,
    see our [dedicated documentation pages](https://dfki.gitlab.io/fb/ni/ol/iml/vr/vr.delaunay-to-voronoi/).

## Support

Please refer to the issue tracker for any inquiry.
