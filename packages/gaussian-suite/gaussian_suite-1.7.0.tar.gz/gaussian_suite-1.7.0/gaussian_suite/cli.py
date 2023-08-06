"""
This module contains the command line interface to gaussian_suite
"""


import argparse
from argparse import RawTextHelpFormatter
import xyz_py as xyzp
import numpy as np
import os
import sys
import textwrap

import hpc_suite as hpc
from hpc_suite.action import OrderAction
from hpc_suite.generate_job import parse_hostname

from . import gen_input
from . import extractor
from . import opt_extractor
from . import freq_extractor
from . import gen_job
from . import cd_extractor


def check_file(file_name, extension):
    """
    Checks extension of `file_name` matches `extension`
    If extension does not match, the program is terminated

    Parameters
    ----------
    file_name : str
        file name whose extension will be checked
    extension : str
        extension to check against

    Returns
    -------
    None

    """

    ext = os.path.splitext(file_name)[1]
    if ext != extension:
        sys.exit("Incorrect file format provided!")

    return


def generate_input_func(user_args, hpc_args):
    """
    Wrapper function for CLI gen_input call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """

    labels, coords = xyzp.load_xyz(user_args.xyz_file)
    labels_nn = xyzp.remove_label_indices(labels)
    labels = xyzp.add_label_indices(labels_nn)

    sub = [x.capitalize() for x in user_args.sub]

    # Substitute atoms if requested
    if sub:
        labels, labels_nn = gen_input.subsititute_element(
            sub, labels, labels_nn
        )

    # Freeze all hydrogens
    if user_args.opt_H_only:
        frozen = [0 if lab == 'H' else -1 for lab in labels_nn]
    # Freeze only specified atoms
    elif len(user_args.frozen):
        frozen = np.loadtxt("{}".format(user_args.frozen), dtype=int)
    else:
        frozen = []

    unique_elements = list(set(labels_nn))

    # Convert user list of ECP to dict
    user_ecp = {}
    if len(user_args.ecp) % 2:
        sys.exit("Missing ECP definition in --ecp argument")
    if len(user_args.ecp):
        user_args.ecp = [uae.replace(".", " ") for uae in user_args.ecp]
        user_ecp = {}
        for it in range(0, len(user_args.ecp)-1, 2):
            user_ecp[user_args.ecp[it].capitalize()] = user_args.ecp[it+1]

    file_name = "{}.com".format(os.path.splitext(user_args.xyz_file)[0])

    # Check Gaussian has a basis set (cc-pVDZ) for each atom
    # https://gaussian.com/basissets/
    # Alert user if not and add placeholder to com file
    supported = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na",
                 "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "Ca", "Sc", "Ti",
                 "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge",
                 "As", "Se", "Br", "Kr"]

    need_to_find = [
        label for label in unique_elements
        if label not in supported and label not in user_ecp.keys()
    ]

    user_args.hq = [hq.capitalize() for hq in user_args.hq]

    # Set basis quality for each element
    bs_spec = {}
    for atom in unique_elements:
        if atom in need_to_find:
            message = "\033[93m ***** Basis set must be added manually"
            message += " to .com file for {} ***** \033[0m".format(atom)
            print(message)
            bs_spec[atom] = "????"
        elif atom in user_args.hq:
            bs_spec[atom] = "cc-pVTZ"
        elif atom not in user_ecp.keys():
            bs_spec[atom] = "cc-pVDZ"

    # Set ecp quality if given
    ecp_spec = {}
    ecp_short = {
        "rsc": "stuttgart rsc 1997"
    }
    for atom in unique_elements:
        if atom in user_ecp.keys():
            if user_ecp[atom] in ecp_short.keys():
                ecp_spec[atom] = ecp_short[user_ecp[atom]]
            else:
                ecp_spec[atom] = user_ecp[atom]

    gen_input.gen_input(
        file_name, labels, coords, user_args.charge, user_args.mult,
        user_args.method, bs_spec, ecp_spec=ecp_spec,
        subiso=user_args.subiso, chelpg=user_args.chelpg,
        opt=not user_args.no_opt, frozen=frozen
    )


def gen_job_func(user_args, unknown_args):
    """
    Wrapper function for CLI gen_job call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """

    hpc_args = hpc.read_args(['generate_job'] + unknown_args)

    if hpc_args.profile == 'read_hostname':
        machine = parse_hostname()
    else:
        machine = hpc_args.profile

    supported_machines = [
        "csf3",
        "csf4"
    ]

    if machine not in supported_machines:
        sys.exit("Error: Unsupported machine")

    default_mod = {
        "csf3": "apps/binapps/gaussian/g16c01_em64t",
        "csf4": "gaussian/g16c01_em64t_detectcpu"
    }

    default_scratch = {
        "csf3": "/scratch/$USER/Gaussian/gau_temp_$JOB_ID",
        "csf4": "/scratch/$USER/Gaussian/gau_temp_$SLURM_JOBID"
    }

    default_chk = {
        "csf3": "$CurrDir/$JNAME.chk",
        "csf4": "$JNAME.chk"
    }

    default_version = {
        "csf3": "$g16root/g16/g16",
        "csf4": "$g16root/g16/g16"
    }

    # GB per core
    mem_multiplier = {
        "csf3": 4,
        "csf4": 4
    }

    # Create submission script
    gen_job.create_submission_script(
        "{}.DATA".format(user_args.com_file_name[:-4]),
        user_args.n_cores,
        user_args.n_cores * mem_multiplier[machine],
        machine,
        default_mod[machine],
        default_scratch[machine],
        default_chk[machine],
        default_version[machine],
        gen_fchk=not user_args.no_gen_fchk,
    )

    return


def coord_extractor_func(user_args):
    """
    Wrapper function for CLI coord_extractor call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """

    ext = os.path.splitext(user_args.file_name)[1]

    supported_exts = [".fchk", ".log", ".com"]

    if ext not in supported_exts:
        os.exit("Error: Unsupported file extension!")

    parsers = [
        opt_extractor.read_coords_fchk,
        opt_extractor.read_coords_log,
        opt_extractor.read_coords_com
    ]
    ext_dict = dict(zip(supported_exts, parsers))

    # Extract labels and coordinates from file
    labels, coords = ext_dict[ext](
        user_args.file_name,
        numbered=user_args.numbered
    )

    # Write .xyz file
    file_name = "{}_cextr.xyz".format(os.path.splitext(user_args.file_name)[0])
    xyzp.save_xyz(file_name, labels, coords)

    return


def extractor_func(args, unknown_args):
    """
    Wrapper function for command line interface call to extractor

    Parameters
    ----------
    args : argparser object
        command line arguments
    unknown_args : list
        unknown command line flags to be passed on to a secondary parser

    Returns
    -------
    None

    """

    try:
        selected = args.order
    except AttributeError:
        sys.exit("No section selected for extraction!")

    # default filter selection {source: destination}
    default_filter = {
        "freq": hpc.store.keep_all("occurrence")
    }

    store_args = hpc.read_args(['store'] + unknown_args)

    # set up default filter
    store_args.filter = store_args.filter or \
        [default_filter.get(item, None) for item, _ in selected]

    hpc.store_func(store_args, extractor.make_extractor, selected)

    return


def distort_func(user_args):
    """
    Wrapper function for CLI distort call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """

    # Check log file has been provided
    check_file(user_args.log_file_name, ".log")

    # Read displacement vectors from Gaussian
    props, _ = freq_extractor.get_freq_prop_log(user_args.log_file_name)

    # Read optimised structure from Gaussian
    labels, coords = opt_extractor.read_coords_log(user_args.log_file_name)

    # Check user hasn't requested a stupid number
    n_modes = np.shape(props["displacements"])[1]
    if not 0 < user_args.mode <= n_modes:
        print('Invalid mode number selected')
        print('This molecule has {:d} modes'.format(n_modes))
        exit()

    # Distort along chosen vibrational mode by 1 unit of
    # normalised displacement vector
    n_atoms = np.shape(props["displacements"])[0]//3
    disp_vec = props["displacements"][:, user_args.mode-1]
    disp_vec = np.reshape(disp_vec, [n_atoms, 3], order='C')
    dist_coords = [co + di for co, di in zip(coords, disp_vec)]

    # Write .xyz file
    file_name = "{}_distorted.xyz".format(
        os.path.splitext(user_args.log_file_name)[0]
        )
    xyzp.save_xyz(file_name, labels, dist_coords, verbose=True)

    return


def dip_deriv_func(user_args):
    """

    Wrapper function for CLI dipole derivates call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """
    # Check log file has been provided
    check_file(user_args.log_file_name, ".log")

    # Check .fchk file has been provided
    check_file(user_args.fchk_file_name, ".fchk")

    # Extract displacement vectors for vibrational modes
    props, _ = freq_extractor.get_freq_prop_log(
        user_args.log_file_name
    )

    red_mass = props["reduced_masses"]
    disp_vec = props["displacements"]
    n_dirs = np.shape(disp_vec)[0]

    # Remove sqrt(reduced_mass) weighting from each displacement vector
    disp_vec /= np.tile(np.sqrt(red_mass), [n_dirs, 1])

    # Extract per atom dipole derivatives from .fchk file
    dip_deriv_pa = freq_extractor.get_dip_deriv_fchk(
        user_args.fchk_file_name
    )
    n_modes = len(red_mass)

    dip_deriv = np.zeros([n_modes, 3])

    for it in range(n_modes):
        dip_deriv[it] = np.sum(
            dip_deriv_pa * np.tile(
                disp_vec[:, it], [3, 1]
                ).T,
            axis=0
        )

    # Convert from e u^-1/2 to km^1/2 mol^-1/2
    dip_deriv *= 31.2231

    out_head = user_args.log_file_name.split(".")[0]
    out_name = "{}_dipole_derivatives.dat".format(out_head)

    np.savetxt(
        out_name,
        dip_deriv,
        header="Units: km^1/2 mol^-1/2",
        fmt="% 7.5e"
    )

    print("Dipole derivatives are written to")
    print("{}".format(out_name))

    return


def cd_extractor_func(user_args):
    """

    Wrapper function for CLI charges and dipoles extractor call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """
    # Check log file has been provided
    check_file(user_args.log_file_name, ".log")

    if user_args.mode == 'charges_dipoles':

        # Extract charges and dipoles
        charges, dipoles = cd_extractor.get_chelpg_charges_dipoles(
            user_args.log_file_name
        )

        out_head = user_args.log_file_name.split(".")[0]

        out_name = "{}_charges_dipoles.dat".format(out_head)

        # output array of charges, dip_x, dip_y, dip_z
        out_array = np.vstack([charges, np.array(dipoles).T]).T

        np.savetxt(
            out_name,
            out_array,
            header="Charges (e), dipole_x (A e), dipole_y (A e), dipole_z (A e)",
            fmt="% 7.5e"
        )

        print("Charges and dipoles are written to")
        print("{}".format(out_name))

    else:

        # Extract charges
        charges = cd_extractor.get_chelpg_charges(
            user_args.log_file_name
        )

        out_head = user_args.log_file_name.split(".")[0]

        out_name = "{}_charges.dat".format(out_head)

        np.savetxt(
            out_name,
            charges,
            header="Charges (e)",
            fmt="% 7.5e"
        )

        print("Charges are written to")
        print("{}".format(out_name))

    return


def geom_conv_func(user_args):
    """

    Wrapper function for CLI max/rmsd force and displacements call

    Parameters
    ----------
    user_args : argparser object
        User arguments

    Returns
    -------
    None

    """

    _, props, thresholds = opt_extractor.get_max_rmsd_force_displacement(
        user_args.log_file_name
    )

    opt_extractor.plot_max_rmsd_force_displacement(
        props,
        thresholds,
        save=user_args.save_plot,
        show=not user_args.no_show
    )

    if user_args.save_values:
        header = "Max. Force    RMSD Force    "
        header += "Max. Displacement    RMSD Displacement"
        np.savetxt(
            "geom_convergence_params.dat",
            props,
            fmt="%f         %f          %f          %f",
            header=header
        )
        print(
            "Convergence parameters are written to geom_convergence_params.dat"
        )

    return


def read_args(arg_list=None):
    """

    Creates parser and subparsers for command line arguments

    Parameters
    ----------
    arg_list : list
        User arguments

    Returns
    -------
    None

    """

    description = '''
    A package for dealing with Gaussian input and output files.
    '''

    epilog = '''
    To display options for a specific program, use
    gaussian_suite PROGRAM_NAME -h
    '''

    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='prog')

    # Generate Input files

    gen_input = subparsers.add_parser(
        'gen_input',
        formatter_class=RawTextHelpFormatter,
        description="\
        Generates Gaussian input (.com) file from .xyz file\n\
        Default calculation is opt+freq, with all atoms treated with cc-PDVZ"
    )
    gen_input.set_defaults(func=generate_input_func) # noqa

    gen_input.add_argument(
        "xyz_file",
        type=str,
        metavar="xyz_file",
        help="xyz file containing atomic coordinates"
    )

    gen_input.add_argument(
        "charge",
        type=int,
        metavar="charge",
        help="Charge of molecule/ion/complex"
    )

    gen_input.add_argument(
        "mult",
        type=int,
        metavar="multiplicity",
        help="Spin Multiplicity (2S+1) of molecule/ion/complex"
    )

    gen_input.add_argument(
        "method",
        type=str,
        metavar="method",
        help="Either 1) DFT Functional - PBE, PBE0, B3LYP \n" +
             "Or     2) Method -  MP2"
    )
    gen_input.add_argument(
        "--no_opt",
        action="store_true",
        help="Skip optimisation"
    )

    gen_input.add_argument(
        "--hq",
        type=str,
        default=[],
        nargs="+",
        metavar=("atom_1", "atom_2"),
        help="Increase basis set quality for these labels to cc-PDTZ"
    )

    gen_input.add_argument(
        "--ecp",
        type=str,
        default=[],
        nargs="+",
        metavar="[atom, ecp_name]",
        help=textwrap.dedent(
            """Specify atoms for which an ECP is used.
    Input as atom, ecp, atom, ecp
    where ecp is the name given on the basis set exchange website
    Substitute spaces in basis set names with full stops
    The shorthand for Stuttgart RSC 1997 ECP is rsc
    Make sure to module load tools/env/proxy or this will not work!
            """
        )
    )

    gen_input.add_argument(
        "--sub",
        type=str,
        default=[],
        nargs=2,
        metavar=("X", "Y"),
        help="Use atom Y in place of atom X (all instances)"
    )

    gen_input.add_argument(
        "--chelpg",
        type=str,
        default='',
        choices=["charge", "charge_dipole"],
        help="Express electronic potential as charges and dipoles with CHELPG"
    )

    gen_input.add_argument(
        "--subiso",
        default=[],
        nargs="+",
        help="For labels XX, YY, ZZ use mass MMM"
    )

    gen_input.add_argument(
        "--frozen",
        type=str,
        default='',
        metavar="file_name",
        help="""Freeze atoms specified in file. File must contain n_atoms
        rows of either 0 (unfrozen) or -1 (frozen) as integers with
        the same ordering as the coordinates"""
    )

    gen_input.add_argument(
        "--opt_H_only",
        action="store_true",
        help="Freeze all atoms other than hydrogens"
    )

    # Submission script and submission

    gen_job = subparsers.add_parser(
        "gen_job",
        formatter_class=RawTextHelpFormatter,
        description="""
        Generate submission script for .com file
        """
    )

    gen_job.set_defaults(
        func=gen_job_func
    )

    gen_job.add_argument(
        "com_file_name",
        type=str,
        help="Gaussian .com file name"
    )

    gen_job.add_argument(
        "n_cores",
        type=int,
        help="Number of cores (threads) to request"
    )

    gen_job.add_argument(
        "--short",
        action="store_true",
        help="Request short queue (1 hour and 12 cores max)"
    )

    gen_job.add_argument(
        "--no_gen_fchk",
        action="store_true",
        help="Skip generation of formatted checkpoint file"
    )

    # Vibrational mode extractor

    extract = subparsers.add_parser(
        'extractor',
        description="""Program which facilitates extraction of data from the
        human-readable text output and *.fchk output files from an Gaussian
        calculation.""",
        epilog="""Example: gaussian_suite extractor -i dy.log -o dy_freq.hdf5
        --freq frequency""")

    extract.set_defaults(func=extractor_func)

    extract.add_argument(
        '-H', '--Help', const='store',
        action=hpc.SecondaryHelp,
        help='show help message for additional arguments and exit'
    )

    extract.add_argument(
        '--freq',
        nargs='+',
        action=OrderAction,
        choices=["frequency", "ir_intensity", "reduced_mass", "force_constant",
                 "irrep", "displacement"],
        help='Extract items from a frequency calculation'
    )

    extract.add_argument(
        '--fchk',
        nargs='+',
        action=OrderAction,
        choices=["hessian", "atomic_mass"],
        help='Extract items from the formatted checkpoint file'
    )

    # Coordinate extractor

    coord_extractor = subparsers.add_parser(
        "coord_extractor",
        formatter_class=RawTextHelpFormatter,
        description="""
        Extracts coordinates from Gaussian .log, .com, or .fchk file.
        If .log file is given, the optimised coordinates are retrieved.
        """
        )
    coord_extractor.set_defaults(
        func=coord_extractor_func
    )

    coord_extractor.add_argument(
        "file_name",
        type=str,
        help="Gaussian .log, .com, or .fchk file name"
    )

    coord_extractor.add_argument(
        "--numbered",
        action="store_true",
        help="If specified add index numbers for final xyz file e.g. Dy1 C3"
    )

    # Distort

    distort = subparsers.add_parser(
        "distort",
        formatter_class=RawTextHelpFormatter,
        description="""
        Distorts .log file structure along specified vibrational mode and saves
        structure to xyz file
        """
    )

    distort.set_defaults(
        func=distort_func
    )

    distort.add_argument(
        "log_file_name",
        type=str,
        help="Gaussian .log file name"
    )

    distort.add_argument(
        "mode",
        type=int,
        help="Number of vibrational mode to distort along"
    )

    # Dipole derivatives

    dip_deriv = subparsers.add_parser(
        "dip_deriv",
        formatter_class=RawTextHelpFormatter,
        description="""
        Extract dipole derivatives dmu_x/dQ, dmu_y/dQ, dmu_z/dQ
        from .log and .fchk files
        """
    )

    dip_deriv.set_defaults(
        func=dip_deriv_func
    )

    dip_deriv.add_argument(
        "log_file_name",
        type=str,
        help="Gaussian .log file name"
    )

    dip_deriv.add_argument(
        "fchk_file_name",
        type=str,
        help="Gaussian .fchk file (obtained using formchk on .chk file)"
    )

    # Charges and dipoles extraction

    cd_extract = subparsers.add_parser(
        "cd_extractor",
        formatter_class=RawTextHelpFormatter,
        description="""
        Extract charges and dipoles from fit of electronic potential (CHELPG)
        """
    )

    cd_extract.set_defaults(
        func=cd_extractor_func
    )

    cd_extract.add_argument(
        "log_file_name",
        type=str,
        help="Gaussian .log file name"
    )

    cd_extract.add_argument(
        "--mode",
        type=str,
        choices={"charges_dipoles", "charges"},
        default="charges_dipoles",
        help="Type of decomposition to extract from .log file"
    )

    # Charges and dipoles extraction

    geom_conv = subparsers.add_parser(
        "geom_convergence",
        formatter_class=RawTextHelpFormatter,
        description="""
        Plot max/rmsd values of forces and displacements in geometry
        optimsation
        """
    )

    geom_conv.set_defaults(
        func=geom_conv_func
    )

    geom_conv.add_argument(
        "log_file_name",
        type=str,
        help="Gaussian .log file name"
    )

    geom_conv.add_argument(
        "--save_plot",
        action="store_true",
        help="Save plot to file"
    )

    geom_conv.add_argument(
        "--no_show",
        action="store_true",
        help="Do not show plot on screen"
    )

    geom_conv.add_argument(
        "--save_values",
        action="store_true",
        help="Save maximum and rmsd values of force and displacement to file"
    )

    # If argument list is none, then call function func
    # which is assigned to help function
    parser.set_defaults(func=lambda user_args: parser.print_help())

    # read sub-parser
    _args, _ = parser.parse_known_args(arg_list)

    # select parsing option based on sub-parser
    if _args.prog in ['extractor', 'gen_job', 'gen_input']:
        args, hpc_args = parser.parse_known_args(arg_list)
        args.func(args, hpc_args)
    else:
        args = parser.parse_args(arg_list)
        args.func(args)
    return


def main():
    read_args()
