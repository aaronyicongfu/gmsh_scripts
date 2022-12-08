import gmsh
import numpy as np
import argparse

p = argparse.ArgumentParser()
p.add_argument("nx", type=int, default=10)
p.add_argument("ny", type=int, default=10)
p.add_argument("nz", type=int, default=10)
p.add_argument("--lx", type=float, default=1.0)
p.add_argument("--ly", type=float, default=1.0)
p.add_argument("--lz", type=float, default=1.0)
p.add_argument("--bc_portion", type=float, default=0.5)
p.add_argument("--gui", action="store_true")
args = p.parse_args()

gmsh.initialize()

# Set up points, lines, loops and surfaces
lx = args.lx
ly = args.ly
lz = args.lz
frac = args.bc_portion

p1 = gmsh.model.geo.addPoint(0.0, 0.0, 0.0)
p2 = gmsh.model.geo.addPoint(0.0, ly, 0.0)
p3 = gmsh.model.geo.addPoint(0.0, ly, lz)
p4 = gmsh.model.geo.addPoint(0.0, 0.0, lz)

l1 = gmsh.model.geo.addLine(p1, p2)
l2 = gmsh.model.geo.addLine(p2, p3)
l3 = gmsh.model.geo.addLine(p3, p4)
l4 = gmsh.model.geo.addLine(p4, p1)

loop1 = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])

rect = gmsh.model.geo.addPlaneSurface([loop1])

# Set transfinite mesh
npts_y = args.ny + 1
npts_z = args.nz + 1
gmsh.model.geo.mesh.setTransfiniteCurve(l1, nPoints=npts_y)
gmsh.model.geo.mesh.setTransfiniteCurve(l2, nPoints=npts_z)
gmsh.model.geo.mesh.setTransfiniteCurve(l3, nPoints=npts_y)
gmsh.model.geo.mesh.setTransfiniteCurve(l4, nPoints=npts_z)
gmsh.model.geo.mesh.setTransfiniteSurface(
    1, arrangement="Left", cornerTags=[p1, p2, p3, p4]
)

twist = gmsh.model.geo.twist(
    dimTags=[(2, rect)],
    x=0.0,
    y=0.5 * ly,
    z=0.5 * lz,
    dx=lx,
    dy=0,
    dz=0,
    ax=1,
    ay=0,
    az=0,
    angle=0.0,
    numElements=[args.nx],
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

gmsh.model.mesh.generate(dim=3)

if args.gui:
    gmsh.fltk.run()

nelems = args.nx * args.ny * args.nz
dim = 2 if args.nz == 1 else 3
gmsh.write(f"{dim}d_hex_{nelems}.vtk")

gmsh.finalize()
