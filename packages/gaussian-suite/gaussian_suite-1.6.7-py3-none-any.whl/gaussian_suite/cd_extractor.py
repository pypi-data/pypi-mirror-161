"""
This module contains various functions for extracting information from output
files produced by Gaussian calculations containing the PROP keyword.
"""


def get_charges_dipoles_log(f_name):
    """
    Extracts charges and dipoles from .log file

    Parameters
    ----------
        f_name : str
            Name of log file

    Returns
    -------
        charges : list
            Charges per atom
        dipoles : list
            list of lists of dipoles in units of electron-angstrom
                [[mu_x_1, mu_y_1, mu_z_1],[mu_x_2, mu_y_2, mu_z_2], ...]

    """

    charges = []
    dipoles = []
    with open(f_name, 'r') as f:
        for line in f:

            if 'FitSet' in line:
                n_atoms = int(line.split()[2])

            if 'Charges from ESP fit' in line:
                for _ in range(2):
                    next(f)
                for _ in range(n_atoms):
                    line = next(f)
                    charges.append(float(line.split()[2]))
                    # Convert from Bohr-electron to Angstrom-electron
                    dips = [
                        float(dip)*0.5291772083 for dip in line.split()[3:6]
                    ]
                    dipoles.append(dips)

    return charges, dipoles
