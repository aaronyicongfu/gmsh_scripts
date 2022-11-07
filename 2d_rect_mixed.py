"""
This script use Gmsh to generate a 2-dimensional rectangular domain meshed with
triangular and quadrilateral element types in the vtk format
"""
import gmsh
import argparse


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--small-scale", action="store_true")
    args = p.parse_args()
    return args


def define_mesh_topology(args):
    """
    Defines geometry entities: point, line, curve loop and surface
    """
    if args.small_scale:
        h1 = 0.2
        h2 = 0.5
    else:
        h1 = 0.01
        h2 = 0.05

    p1 = gmsh.model.geo.addPoint(0, 0, 0, meshSize=h1)
    p2 = gmsh.model.geo.addPoint(0.5, 0, 0, meshSize=h1)
    p3 = gmsh.model.geo.addPoint(0.5, 0.5, 0, meshSize=h1)
    p4 = gmsh.model.geo.addPoint(0, 0.5, 0, meshSize=h1)

    p5 = gmsh.model.geo.addPoint(1.5, 0, 0, meshSize=h2)
    p6 = gmsh.model.geo.addPoint(1.5, 0.5, 0, meshSize=h2)

    l1 = gmsh.model.geo.addLine(p1, p2)
    l2 = gmsh.model.geo.addLine(p2, p3)
    l3 = gmsh.model.geo.addLine(p3, p4)
    l4 = gmsh.model.geo.addLine(p4, p1)

    l5 = gmsh.model.geo.addLine(p2, p5)
    l6 = gmsh.model.geo.addLine(p5, p6)
    l7 = gmsh.model.geo.addLine(p6, p3)

    loop1 = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4])
    loop2 = gmsh.model.geo.addCurveLoop([l5, l6, l7, -l2])

    plane1 = gmsh.model.geo.addPlaneSurface([loop1])
    plane2 = gmsh.model.geo.addPlaneSurface([loop2])
    return plane1, plane2


if __name__ == "__main__":
    args = parse_args()

    # Initialize gmsh
    gmsh.initialize()

    # Create geometry
    plane1, plane2 = define_mesh_topology(args)
    gmsh.model.geo.synchronize()

    # Generate mesh
    gmsh.option.setNumber("Mesh.Algorithm", 5)
    gmsh.model.mesh.setRecombine(dim=2, tag=plane2)  # use quad element for plane 2
    gmsh.model.mesh.generate(dim=2)
    gmsh.write("mesh.vtk")

    # Finish
    gmsh.finalize()
