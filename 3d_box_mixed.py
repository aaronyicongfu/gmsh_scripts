"""
This script use Gmsh to generate a 3-dimensional domain meshed with
hexahedron, tetrahedral wedge and pyramid elements in the vtk format
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
npts = 3 if args.small_scale else 20
tl1 = gmsh.model.geo.mesh.setTransfiniteCurve(l1, nPoints=npts, coef=grow_rate)
tl2 = gmsh.model.geo.mesh.setTransfiniteCurve(l2, nPoints=npts)
tl3 = gmsh.model.geo.mesh.setTransfiniteCurve(l3, nPoints=npts, coef=grow_rate)
tl4 = gmsh.model.geo.mesh.setTransfiniteCurve(l4, nPoints=npts)
gmsh.model.geo.mesh.setTransfiniteSurface(
    1, arrangement="Left", cornerTags=[p1, p2, p3, p4]
)

# Set up 1st stage
nelems = 2 if args.small_scale else 10
extrude = gmsh.model.geo.extrude(
    [(2, rect)], 1, 0, 0, numElements=[nelems], heights=[], recombine=True
)

# Set up 2nd stage
end = extrude[0]
twist = gmsh.model.geo.twist([end], 1, 0.5, 0.5, 1, 0, 0, 1, 0, 0, 0.5 * np.pi)

# Set up 3rd stage
end2 = twist[0]
nelems = 2 if args.small_scale else 10
extrude2 = gmsh.model.geo.extrude(
    [end2], 1, 0, 0, numElements=[nelems], heights=[], recombine=True
)

gmsh.model.geo.synchronize()
gmsh.model.mesh.setRecombine(dim=2, tag=rect)
gmsh.option.setNumber("Mesh.Algorithm", 5)

pts = gmsh.model.getEntities(dim=0)
h = 0.5 if args.small_scale else 0.05
gmsh.model.mesh.setSize(pts, size=h)

gmsh.model.mesh.generate(dim=3)

if args.gui:
    gmsh.fltk.run()

gmsh.write("3d_box_mixed.vtk")

gmsh.finalize()
