"""
This script use Gmsh to generate a 3-dimensional domain meshed with
hexahedron, tetrahedral, wedge and pyramid elements in the vtk format
"""

import gmsh
import numpy as np
import argparse

p = argparse.ArgumentParser()
p.add_argument("--small-scale", action="store_true")
p.add_argument("--gui", action="store_true")
args = p.parse_args()

gmsh.initialize()

# Set up points, lines, loops and surfaces
p1 = gmsh.model.geo.addPoint(0, 0, 0)
p2 = gmsh.model.geo.addPoint(0, 0, 1)
p3 = gmsh.model.geo.addPoint(0, 1, 1)
p4 = gmsh.model.geo.addPoint(0, 1, 0)

l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)
l3 = gmsh.model.geo.addLine(p3, p4)
l4 = gmsh.model.geo.addLine(p4, p1)

loop1 = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])

rect = gmsh.model.geo.addPlaneSurface([loop1])

# Set transfinite mesh
grow_rate = 1.1
npts = 2 if args.small_scale else 5
gmsh.model.geo.mesh.setTransfiniteCurve(l1, nPoints=npts, coef=grow_rate)
gmsh.model.geo.mesh.setTransfiniteCurve(l2, nPoints=npts)
gmsh.model.geo.mesh.setTransfiniteCurve(l3, nPoints=npts, coef=grow_rate)
gmsh.model.geo.mesh.setTransfiniteCurve(l4, nPoints=npts)
gmsh.model.geo.mesh.setTransfiniteSurface(
    1, arrangement="Left", cornerTags=[p1, p2, p3, p4]
)

nelems = 2 if args.small_scale else 5
twist = gmsh.model.geo.twist(
    dimTags=[(2, rect)],
    x=1,
    y=0.5,
    z=0.5,
    dx=2,
    dy=0,
    dz=0,
    ax=1,
    ay=0,
    az=0,
    angle=0.5 * np.pi,
    numElements=[nelems],
    heights=[],
    recombine=True,
)

gmsh.model.geo.synchronize()

twist_start_tag = rect
twist_end_tag = twist[0][1]
twist_vol_tag = twist[1][1]

pg_face1 = gmsh.model.addPhysicalGroup(
    dim=2, tags=[twist_start_tag], tag=100, name="face1"
)
pg_face2 = gmsh.model.addPhysicalGroup(
    dim=2, tags=[twist_end_tag], tag=101, name="face2"
)
pg_vol = gmsh.model.addPhysicalGroup(dim=3, tags=[twist_vol_tag], tag=1, name="volume")


gmsh.model.mesh.setRecombine(dim=2, tag=rect)
gmsh.option.setNumber("Mesh.Algorithm", 5)

pts = gmsh.model.getEntities(dim=0)
h = 0.5 if args.small_scale else 0.05
gmsh.model.mesh.setSize(pts, size=h)

gmsh.model.mesh.generate(dim=3)


if args.gui:
    gmsh.fltk.run()

gmsh.write("3d_hex_twisted.vtk")

gmsh.finalize()
