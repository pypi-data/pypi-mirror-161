"""
This module contains various functions for extracting information from output
files produced by Gaussian optimisation (OPT) calculations.
"""


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import xyz_py as xyzp
import xyz_py.atomic
import sys
from . import freq_extractor


def read_coords_fchk(f_name, numbered=False):
    """
    Read Gaussian .fchk file and extracts atomic labels and coordinates
    then print to xyz file with same basename as fchk file

    Parameters
    ----------
        f_name : str
            Name of fchk file
        numbered : bool, default False
            If true, resulting list of labels contain atomic indices as well
            as symbols e.g. Dy1 Yb1 C3

    Returns:
    --------
        list
            List of atomic labels
        np.ndarray
            (n_atom,3) array of atomic coordinates
    """
    a_nums = []
    coords = []

    n_atoms = freq_extractor.get_n_atoms_fchk(f_name)

    # Open .fchk file
    with open(f_name, "r") as f:
        for line in f:

            if "Atomic numbers" in line:
                # Gaussian prints up to 6 atomic numbers per line
                for n_rows in range(int(np.ceil(n_atoms/6))):
                    # Move to next line
                    line = next(f)
                    [a_nums.append(int(i)) for i in line.split()]
                a_nums = np.asarray(a_nums)

            if "Current cartesian coordinates" in line:
                # This is units of bohr, so needs to be converted to
                # Angstroms using the correct factor
                # Gaussian prints up to 5 coordinates per line
                for n_rows in range(int(np.ceil(3*n_atoms/5))):
                    # Move to next line
                    line = next(f)
                    [coords.append(float(i)*0.529177249) for i in line.split()]
                # Now rearrange coordinates from a 3N list into a 3 by N array
                coords = np.reshape(coords, (n_atoms, 3))

    f.close()

    # Convert atomic numbers to atomic labels
    labs = xyzp.num_to_lab(a_nums, numbered=numbered)

    return labs, coords


def read_coords_log(f_name, numbered=False):
    """
    Read Gaussian .log file to extracts atomic labels and coordinates
    then print to xyz file with same basename as log file

    Parameters
    ----------
        f_name : str
            Name of log file
        numbered : bool, default False
            If true, resulting list of labels contain atomic indices as well
            as symbols e.g. Dy1 Yb1 C3

    Returns:
    --------
        list
            List of atomic labels
        np.ndarray
            (n_atom,3) array of atomic coordinates
    """

    n_atoms = freq_extractor.get_n_atoms_log(f_name)

    # Get coordinates
    with open(f_name, "r") as f:
        for line in f:

            # Read in coordinates from checkpoint geometry
            # todo
            # if "Structure from the checkpoint file:" in line:
            #     print("Reading checkpoint structures from log file")
            #     print("is currently unsupported, skipping...")
            #     pass

            # Read in coordinates from standard orientation geometry
            if any(head in line for head in [
                "Standard orientation:", "Input orientation:"
            ]):
                coords = []
                a_nums = []

                # Skip header
                for i in range(4):
                    line = next(f)

                for i in range(n_atoms):
                    line = next(f)
                    coords.append([float(coord) for coord in line.split()[3:]])
                    a_nums.append(int(line.split()[1]))

    f.close()

    # Convert atomic numbers to atomic labels
    labs = xyzp.num_to_lab(a_nums, numbered=numbered)

    return labs, coords


def read_coords_com(f_name, numbered=False):
    """
    Read Gaussian .com file to extracts atomic labels and coordinates
    then print to xyz file with same basename as com file

    Parameters
    ----------
        f_name : str
            Name of com file
        numbered : bool, default False
            If true, resulting list of labels contain atomic indices as well
            as symbols e.g. Dy1 Yb1 C3

    Returns:
    --------
        list
            List of atomic labels
        np.ndarray
            (n_atom,3) array of atomic coordinates
    """

    cm_found = False
    labs = []
    coords = []

    with open(f_name, "r") as f:
        for line in f:
            # Try and find charge and multiplicity line
            if len(line.split()) == 2:
                try:
                    [int(s) for s in line.split()]
                    cm_found = True
                    line = next(f)
                except ValueError:
                    pass
            # Try and find coordinates after charge and multiplicity lines
            if cm_found:
                while len(line.split()):
                    labs.append(line.split()[0])
                    coords.append([
                        float(coord)
                        for coord in line.split()[-3:]
                    ])
                    line = next(f)

                break

    if labs == [] or coords == []:
        sys.exit('Error: Unable to locate coordinates')

    if numbered:
        labs = xyzp.add_label_indices(labs)

    return labs, coords


def get_max_rmsd_force_displacement(f_name):
    """
    Extracts maximum and rmsd of forces and displacements from log file
    for each step of geometry optimisation up to the point of convergence

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        bool
            True if convergence of all four parameters, else False
        np.ndarray
            n_steps by 4 array, containing convergence statistics with columns
            max force, rmsd force, max displacement, rmsd displacement
        np.ndarray
            4 by 1 array, containing convergence thresholds with elements
            max force, rmsd force, max displacement, rmsd displacement
    """

    # Initialise lists for displacements and forces
    d_max = []
    d_rmsd = []
    f_max = []
    f_rmsd = []

    yn_dict = {
        "YES": True,
        "NO": False
    }

    yes_no = []
    converged = False

    with open(f_name, 'r') as f:
        for line in f:

            # Convergence properties and threshold info
            if 'Value     Threshold  Converged?' in line:

                yes_no = []

                # Force Maximum
                line = next(f)
                f_max.append(float(line.split()[2]))
                f_max_thresh = float(line.split()[3])
                yes_no.append(yn_dict[line.split()[4]])

                # Force rmsd
                line = next(f)
                f_rmsd.append(float(line.split()[2]))
                f_rmsd_thresh = float(line.split()[3])
                yes_no.append(yn_dict[line.split()[4]])

                # Displacement Maximum
                line = next(f)
                d_max.append(float(line.split()[2]))
                d_max_thresh = float(line.split()[3])
                yes_no.append(yn_dict[line.split()[4]])

                # Displacement rmsd
                line = next(f)
                d_rmsd.append(float(line.split()[2]))
                d_rmsd_thresh = float(line.split()[3])
                yes_no.append(yn_dict[line.split()[4]])

            # Check for complete convergence of forces and displacements
            if all(yes_no) and len(yes_no):
                converged = True
                break

        if not len(yes_no):
            sys.exit("No optimisation steps found")

        thresholds = np.array(
            [f_max_thresh, f_rmsd_thresh, d_max_thresh, d_rmsd_thresh]
        )
        props = np.array([f_max, f_rmsd, d_max, d_rmsd]).T

        return converged, props, thresholds


def plot_max_rmsd_force_displacement(props, thresholds, show=True, save=False,
                                     save_name="geom_convergence.png"):
    """
    Plots maximum and rmsd of forces and displacements from log file
    vs step of geometry optimisation

    Parameters
    ----------
        props: np.ndarray
            n_steps by 4 array, containing convergence statistics with columns
            max force, rmsd force, max displacement, rmsd displacement
        thresholds: np.ndarray
            4 by 1 array, containing convergence thresholds with elements
            max force, rmsd force, max displacement, rmsd displacement
        show: bool, default True
            If True, show plot on screen
        save: bool, default False
            If True, save plot to file with name `save_name`
        save_name: str, default="geom_convergence.png"
            Name of file to save plot to


    Returns
    -------
        matplotlib.pyplot.figure
            figure object of plot
        matplotlib.pyplot.axis
            axis object of plot for max force
        matplotlib.pyplot.axis
            axis object of plot for rmsd force
        matplotlib.pyplot.axis
            axis object of plot for max displacement
        matplotlib.pyplot.axis
            axis object of plot for rmsd displacement
    """

    n_steps = np.size(props, axis=0)

    # Create figure and axes
    fig, (ax1, ax3) = plt.subplots(
        1,
        2,
        sharex='all',
        sharey=False,
        figsize=(12, 6),
        num="Convergence properties"
    )
    ax2 = ax1.twinx()
    ax4 = ax3.twinx()

    step_range = np.arange(1, n_steps+1)

    for it, ax in enumerate([ax1, ax2, ax3, ax4]):

        # Plot data
        ax.plot(
            step_range,
            props[:, it],
            linewidth=0,
            color="red" if (it+1) % 2 else "blue",
            marker="o"
        )

        # Plot threshold line
        ax.plot(
            [0, n_steps],
            [thresholds[it]]*2,
            linewidth=2,
            color="red" if (it+1) % 2 else "blue",
            alpha=0.7
        )

    for ax in ax1, ax3:
        ax.set_xlabel("Step number")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    ax1.set_ylabel(" Maximum Force / a.u.", color="red")
    ax2.set_ylabel(" RMSD of Force / a.u.", color="blue")
    ax3.set_ylabel(" Maximum Displacement / a.u.", color="red")
    ax4.set_ylabel(" RMSD of Displacement / a.u.", color="blue")

    fig.tight_layout()

    # Show or save plot
    if save:
        fig.savefig(save_name, dpi=500)
    if show:
        plt.show()

    return fig, ax1, ax2, ax3, ax4
