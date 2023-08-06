"""
This is the main the command line interface to xyz_py
"""

import argparse
import numpy as np
import os

from . import xyz_py


def struct_info_func(args):
    """
    Wrapper for cli call to get_ bonds, dihedrals and angles

    Parameters
    ----------
        args : argparser object
            command line arguments

    Returns
    -------
        None

    """

    labels, coords = xyz_py.load_xyz(args.xyz_file)

    labels = xyz_py.add_numbers(labels)

    f_head = os.path.splitext(args.xyz_f_name)[0]

    if args.cutoffs:
        cutoffs = parse_cutoffs(args.cutoffs)
    else:
        cutoffs = {}

    # Generate neighbourlist
    neigh_list = xyz_py.get_neighborlist(
        labels,
        coords,
        adjust_cutoff=cutoffs
    )

    # Get structural data
    bonds = xyz_py.get_bonds(
        labels,
        coords,
        style="labels",
        neigh_list=neigh_list
    )
    angles = xyz_py.get_angles(
        labels,
        coords,
        style="labels",
        neigh_list=neigh_list
    )
    dihedrals = xyz_py.get_dihedrals(
        labels,
        coords,
        style="labels",
        neigh_list=neigh_list
    )

    # Save to file
    np.savetxt("{}_bonds.dat".format(f_head), bonds, fmt="%s")
    np.savetxt("{}_angles.dat".format(f_head), angles, fmt="%s")
    np.savetxt("{}_dihedrals.dat".format(f_head), dihedrals, fmt="%s")

    return


def rotate_func(args):
    """
    Wrapper for cli call to rotate

    Parameters
    ----------
        args : argparser object
            command line arguments

    Returns
    -------
        None

    """
    labels, coords = xyz_py.load_xyz(args.xyz_file)

    if args.radians:
        xyz_py.rotate_coords(
            coords, args.alpha, args.beta, args.gamma
        )
    else:
        xyz_py.rotate_coords(
            coords,
            args.alpha*180./np.pi,
            args.beta*180./np.pi,
            args.gamma*180./np.pi
        )

    if args.out_f_name:
        out_f_name = args.out_f_name
    else:
        out_f_name = "{}_rotated.xyz".format(
            os.path.splitext(args.xyz_file)[0]
        )

    xyz_py.save_xyz(out_f_name, labels, coords)

    return


def list_form_func(args):
    """
    Wrapper for cli call to find_entities

    Parameters
    ----------
        args : argparser object
            command line arguments

    Returns
    -------
        None

    """

    labels, coords = xyz_py.load_xyz(args.xyz_file)

    labels = xyz_py.add_numbers(labels)

    if args.cutoffs:
        cutoffs = parse_cutoffs(args.cutoffs)
    else:
        cutoffs = {}

    entities_dict = xyz_py.find_entities(
        labels, coords, adjust_cutoff=cutoffs
    )

    for key, val in entities_dict.items():
        print("{} : {:d}".format(key, len(val)))

    return


def parse_cutoffs(cutoffs):

    if len(cutoffs) % 2:
        raise argparse.ArgumentTypeError("Error, cutoffs should come in pairs")

    for it in range(1, len(cutoffs), 2):
        try:
            float(cutoffs[it])
        except ValueError:
            raise argparse.ArgumentTypeError(
                "Error, second part of cutoff pair should be float"
            )

    parsed = {}

    for it in range(0, len(cutoffs), 2):

        parsed[cutoffs[it].capitalize()] = float(cutoffs[it+1])

    return parsed


def read_args(arg_list=None):
    """
    Parser for command line arguments. Uses subparsers for individual programs

    Parameters
    ----------
        args : argparser object
            command line arguments

    Returns
    -------
        None

    """

    description = """
    A package for manipulating xyz files and chemical structures
    """

    epilog = """
    To display options for a specific program, use xyz_py PROGRAMNAME -h
    """

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="prog")

    struct_info = subparsers.add_parser(
        "struct_info",
        description="Extracts structural information (bonds, angles and \
                     dihedrals) from xyz file"
    )
    struct_info.set_defaults(func=struct_info_func)

    struct_info.add_argument(
        "xyz_file",
        type=str,
        help="File containing xyz coordinates in .xyz format"
    )

    struct_info.add_argument(
        "--cutoffs",
        type=str,
        nargs="+",
        default=[],
        metavar=["symbol", "cutoff"],
        help="Change cutoff for symbol to cutoff e.g. Gd 2.5"
    )
    struct_info.add_argument(
        "--save_style",
        type=str,
        default="indices",
        choices=["labels", "indices"],
        help="Save bonds, angles, and dihedrals as atom labels or \
                atom indices"
    )

    rotate = subparsers.add_parser(
        "rotate",
        description="Rotate xyz file by alpha, beta, gamma in degrees using \
                     Easyspin convention"
    )
    rotate.set_defaults(func=rotate_func)

    rotate.add_argument(
        "xyz_file",
        type=str,
        help="File containing xyz coordinates in .xyz format"
    )

    rotate.add_argument(
        "alpha",
        type=float,
        help="Alpha angle in degrees"
    )

    rotate.add_argument(
        "beta",
        type=float,
        help="Beta angle in degrees"
    )

    rotate.add_argument(
        "gamma",
        type=float,
        help="Gamma angle in degrees"
    )

    rotate.add_argument(
        "-r", "--radians",
        action="store_true",
        help="Use radians instead of degrees"
    )

    rotate.add_argument(
        "--out_f_name",
        type=str,
        metavar="file_name",
        help="Output file name - default is append xyz file with _rotated"
    )

    list_form = subparsers.add_parser(
        "list_formulae",
        description="Finds bonded entities in xyz file using adjacency, and \
                     prints their formula and number of ocurrences"
    )
    list_form.set_defaults(func=list_form_func)

    list_form.add_argument(
        "xyz_file",
        type=str,
        help="File containing xyz coordinates in .xyz format"
    )

    list_form.add_argument(
        "--cutoffs",
        type=str,
        nargs="+",
        metavar="symbol number",
        help="Modify cutoff used to define bonds"
    )

    # If arg_list==None, i.e. normal cli usage, parse_args() reads from
    # "sys.argv". The arg_list can be used to call the argparser from the
    # back end.

    # read sub-parser
    parser.set_defaults(func=lambda args: parser.print_help())
    args = parser.parse_args(arg_list)
    args.func(args)


def main():
    read_args()
