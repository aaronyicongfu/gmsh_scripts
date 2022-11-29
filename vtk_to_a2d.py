import argparse


def parse_arguments():
    p = argparse.ArgumentParser()
    p.add_argument("vtk", type=str)
    args = p.parse_args()
    return args


def read_3d_connectivity(vtk_fh):
    """
    Return connectivities of tet, hex, wedge and pyramid cells
    """
    conn_tet = []
    conn_hex = []
    conn_wedge = []
    conn_pyrmd = []
    connectivity = {10: conn_tet, 12: conn_hex, 13: conn_wedge, 14: conn_pyrmd}
    for line in vtk_fh:
        if "CELLS" in line:
            break  # line = CELLS ncell size
    ncell = int(line.strip().split()[1])

    # Load ragged conn
    ragged_conn = []
    for i in range(ncell):
        line = vtk_fh.readline()
        numbers = [int(s) for s in line.strip().split()]
        npt, conn = numbers[0], numbers[1:]
        ragged_conn.append(conn)

    # Load element label data
    for line in vtk_fh:
        if "CELL_TYPES" in line:
            break

    for i in range(ncell):
        label = int(vtk_fh.readline().strip())
        if label in connectivity.keys():
            connectivity[label].extend(ragged_conn[i])

    return connectivity


if __name__ == "__main__":
    args = parse_arguments()

    with open(args.vtk, "r") as f:
        conns = read_3d_connectivity(f)

    print(conns)
