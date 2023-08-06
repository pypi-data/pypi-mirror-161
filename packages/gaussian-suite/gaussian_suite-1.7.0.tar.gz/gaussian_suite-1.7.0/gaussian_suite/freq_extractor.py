"""
This module contains various functions for extracting information from output
files produced by Gaussian frequency (FREQ) calculations.
"""

import deprecation
import numpy as np
from .__version__ import __version__


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_freq_log(f_name):
    """
    Extracts frequencies from Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        list
            Vibrational mode energies in cm-1
    """

    frequencies = []
    n_atoms = get_n_atoms_log(f_name)

    # Read in frequencies
    with open(f_name, "r") as f:
        for line in f:
            if "Frequencies ---" in line:
                for mode in range(2, len(line.split())):
                    frequencies.append(float(line.split()[mode]))
            if len(frequencies) == 3*n_atoms - 6:
                break

    return frequencies


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_freq_prop_log(f_name):
    """
    Extracts vibrational mode properties from Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        dict
            Vibrational mode property names as keys and list of values as
            values
                Keys:
                    "frequencies"
                    "intensities"
                    "reduced_masses"
                    "force_constants"
                    "irreps"
                    "displacements"

        dict
            Units of each property in props
                Keys:
                    "frequencies"
                    "intensities"
                    "reduced_masses"
                    "force_constants"
                    "irreps"
                    "displacements"
                Values: Units (str)
    """

    props = {
        "frequencies": get_freq_log(f_name),
        "intensities": get_freq_intensity_log(f_name),
        "reduced_masses": get_freq_red_mass_log(f_name),
        "force_constants": [],
        "irreps": get_freq_irrep_log(f_name),
        "displacements": get_freq_displacements_log(f_name),
    }

    units = {
        "frequencies": "cm^-1",
        "intensities": "km^1/2 mol^-1/2",
        "reduced_masses": "amu",
        "force_constants": "mdyne angstrom^-1",
        "irreps":  "",
        "displacements": "angstrom reduced_mass^-1/2"
    }

    # Recalculate force constants at higher precision
    light = 299792458.  # [m/s]
    fc = np.asarray(props["frequencies"])**2
    fc *= 0.01*4.*np.pi**2. * (light*100.) ** 2. * 1.66054E-27
    fc *= props["reduced_masses"]
    props["force_constants"] = fc.tolist()

    return props, units


def get_freq_intensity_log(f_name):
    """
    Extracts intensity of each vibrational mode from
    Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        list
            Intensity of each mdoe in atomic mass units (u)
    """

    n_atoms = get_n_atoms_log(f_name)

    intensities = []
    with open(f_name, "r") as f:
        for line in f:
            if "IR Intensities ---" in line:
                for mode in range(3, len(line.split())):
                    intensities.append(float(line.split()[mode]))
            if len(intensities) == 3*n_atoms - 6:
                break

    return intensities


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_freq_red_mass_log(f_name):
    """
    Extracts reduced mass of each vibrational mode from
    Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        list
            Reduced mass of each mdoe in atomic mass units (u)
    """

    n_atoms = get_n_atoms_log(f_name)

    red_masses = []
    with open(f_name, "r") as f:
        for line in f:
            if "Reduced masses ---" in line:
                for mode in range(3, len(line.split())):
                    red_masses.append(float(line.split()[mode]))
            if len(red_masses) == 3*n_atoms - 6:
                break

    return red_masses


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_n_atoms_log(f_name):
    """
    Extracts number of atoms from Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        int
            Number of atoms
    """
    n_atoms = 0

    with open(f_name, "r") as f:
        for line in f:
            if "NAtoms=" in line:
                spl_line = line.split()
                n_atoms = int(spl_line[spl_line.index("NAtoms=")+1])
                break

    if n_atoms == 0:
        print("Cannot find number of atoms in file {}".format(f_name))
        print("Aborting")
        exit()

    return n_atoms


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_n_atoms_fchk(f_name):
    """
    Extracts number of atoms from Gaussian fchk file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        int
            Number of atoms
    """
    n_atoms = 0

    with open(f_name, "r") as f:
        for line in f:
            if "Number of atoms" in line:
                spl_line = line.split()
                n_atoms = int(spl_line[4])
                break

    if n_atoms == 0:
        print("Cannot find number of atoms in file {}".format(f_name))
        print("Aborting")
        exit()

    return n_atoms


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_freq_irrep_log(f_name):
    """
    Extracts Irreducible representation of each vibrational mode from
    Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        list
            Irreducible representation of each vibrational mode
    """

    irreps = []
    n_atoms = get_n_atoms_log(f_name)
    n_modes = 3*n_atoms-6
    with open(f_name, "r") as f:
        for line in f:
            if "and normal coordinates:" in line:
                line = next(f)
                line = next(f)
                [irreps.append(irrep) for irrep in line.split()]
                for chunk in range(n_modes//5 - 1):
                    for it in range(n_atoms*3 + 7):
                        line = next(f)
                    [irreps.append(irrep) for irrep in line.split()]
                break

    return irreps


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_freq_displacements_log(f_name):
    """
    Extracts vibrational mode displacements from
    Gaussian log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        np.ndarray
            Displacement vector of each vibrational mode
            [3*n_atoms x 3*n_atoms-6]
            Note these are weighted by 1/sqrt(mu) when printed by Gaussian
            and are therefore normalised and dimensionless
    """

    # Number of atoms and modes
    n_atoms = get_n_atoms_log(f_name)
    n_modes = 3*n_atoms-6
    coords = np.zeros([3*n_atoms, n_modes])

    # Displacements
    cmode = 0
    with open(f_name, "r") as f:
        for line in f:
            if "Coord Atom Element:" in line:
                cmode += 5
                line = next(f)
                for it in range(0, n_atoms*3, 3):
                    # x coords
                    vals = [num for num in line.split()[3:]]
                    coords[0+it, cmode-5:np.min([cmode, n_modes])] = vals
                    line = next(f)
                    # y coords
                    vals = [num for num in line.split()[3:]]
                    coords[1+it, cmode-5:np.min([cmode, n_modes])] = vals
                    line = next(f)
                    # z coords
                    vals = [num for num in line.split()[3:]]
                    coords[2+it, cmode-5:np.min([cmode, n_modes])] = vals
                    line = next(f)
            if cmode >= n_modes:
                break
    return coords


@deprecation.deprecated(
    deprecated_in="1.4.0", removed_in="2.0.0", current_version=__version__,
    details="use make_extractor interface instead"
)
def get_dip_deriv_fchk(f_name):
    """
    Extracts dipole derivatives from .fchk file
    These are derivatives for x, y, and z directions with
    respect to single atom displacements

    Parameters
    ----------
        f_name : str
            Name of .fchk file

    Returns
    -------
        np.ndarray
            Dipole derivative vector for each single atom displacement
            [3*n_atoms, 3]
    """

    dip_deriv = []

    n_atoms = get_n_atoms_log(f_name)

    with open(f_name, "r") as f:
        for line in f:
            if "Dipole Derivatives" in line:
                # Gaussian prints up to 5 floats per line
                for n_rows in range(int(np.ceil(9*n_atoms/5))):
                    # Move to next line
                    line = next(f)
                    [dip_deriv.append(float(i)) for i in line.split()]
                # Now rearrange coordinates from a 3N list into a 3 by N array
                dip_deriv = np.reshape(dip_deriv, (n_atoms*3, 3))

    return dip_deriv
