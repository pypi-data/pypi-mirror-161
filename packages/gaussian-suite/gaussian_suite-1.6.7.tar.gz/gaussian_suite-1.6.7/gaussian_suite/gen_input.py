"""
This module contains functions for constructing input files for Gaussian
calculations
"""


import requests
import os
import sys
from requests.exceptions import ConnectionError
import xyz_py as xyzp
import copy
from numpy.typing import ArrayLike

# These are VdW radii taken from the 2016/2017
# CRC Handbook of physics of chemistry
# Page 9-57
crc_radii = {
    "Ac": 2.47,
    "Al": 1.84,
    "Am": 2.44,
    "Sb": 2.06,
    "Ar": 1.88,
    "As": 1.85,
    "At": 2.02,
    "Ba": 2.68,
    "Bk": 2.44,
    "Be": 1.53,
    "Bi": 2.07,
    "B": 1.92,
    "Br": 1.85,
    "Cd": 2.18,
    "Ca": 2.31,
    "Cf": 2.45,
    "C": 1.70,
    "Ce": 2.42,
    "Cs": 3.43,
    "Cl": 1.75,
    "Cr": 2.06,
    "Co": 2.00,
    "Cu": 1.96,
    "Cm": 2.45,
    "Dy": 2.31,
    "Es": 2.45,
    "Er": 2.29,
    "Eu": 2.35,
    "Fm": 2.45,
    "F": 1.47,
    "Fr": 3.48,
    "Gd": 2.34,
    "Ga": 1.87,
    "Ge": 2.11,
    "Au": 2.14,
    "Hf": 2.23,
    "He": 1.40,
    "Ho": 2.30,
    "H": 1.10,
    "In": 1.93,
    "I": 1.98,
    "Ir": 2.13,
    "Fe": 2.04,
    "Kr": 2.02,
    "La": 2.43,
    "Lr": 2.46,
    "Pb": 2.02,
    "Li": 1.82,
    "Lu": 2.24,
    "Mg": 1.73,
    "Mn": 2.05,
    "Md": 2.46,
    "Hg": 2.23,
    "Mo": 2.17,
    "Nd": 2.39,
    "Ne": 1.54,
    "Np": 2.39,
    "Ni": 1.97,
    "Nb": 2.18,
    "N": 1.55,
    "No": 2.46,
    "Os": 2.16,
    "O": 1.52,
    "Pd": 2.10,
    "P": 1.80,
    "Pt": 2.13,
    "Pu": 2.43,
    "Po": 1.97,
    "K": 2.75,
    "Pr": 2.40,
    "Pm": 2.38,
    "Pa": 2.43,
    "Ra": 2.83,
    "Rn": 2.20,
    "Re": 2.16,
    "Rh": 2.10,
    "Rb": 3.03,
    "Ru": 2.13,
    "Sm": 2.36,
    "Sc": 2.15,
    "Se": 1.90,
    "Si": 2.10,
    "Ag": 2.11,
    "Na": 2.27,
    "Sr": 2.49,
    "S": 1.80,
    "Ta": 2.22,
    "Tc": 2.16,
    "Te": 2.06,
    "Tb": 2.33,
    "Tl": 1.96,
    "Th": 2.45,
    "Tm": 2.27,
    "Sn": 2.17,
    "Ti": 2.11,
    "W": 2.18,
    "U": 2.41,
    "V": 2.07,
    "Xe": 2.16,
    "Yb": 2.26,
    "Y": 2.32,
    "Zn": 2.01,
    "Zr": 2.23
}


def can_float(s):
    """
    Checks if string can be converted to float

    Parameters
    -----------
        s : str
            string to check

    Returns
    -------
        bool
            True or False
    """

    try:
        float(s)
        return True
    except ValueError:
        return False


def create_basis(bs_spec, ecp_spec={}):
    """
    Creates string containing basis set section of com file

    Parameters
    -----------
        bs_spec : dict
            atomic labels (keys) and basis set specifiers (vals)
            Basis set specifiers must be
            EITHER:
                names of basis sets supported in Gaussian with correct
                capitalisation
                    e.g. cc-pVDZ
            OR
                names of basis sets listed on the basis set exchange, in which
                case the prefix BSE_ must be applied to the name.
                    e.g. BSE_cc-aug-pvtz
        ecp_spec : dict, optional
            atomic labels (keys) and effective corepotential specifiers (vals)
            ECP specifiers must be
                names of basis sets listed on the basis set exchange
                    e.g. RSC1997
    Returns
    -------
        str
            basis set section for com file
        str
            pseudopotential section for com file
    """

    # Make empty basis and separator strings
    basis_section = ""

    # Build basis set string for supported sets
    sep = ""
    for it, (label, basis) in enumerate(bs_spec.items()):

        if "BSE_" in label:
            continue

        # Separator between basis set blocks
        if it > 0:
            sep = "\n**** \n"

        basis_section += "{}{} 0 \n{}".format(sep, label, basis)

    # Build basis set string for BSE sets
    sep = "\n**** \n"
    for it, (label, basis) in enumerate(bs_spec.items()):

        if "BSE_" not in label:
            continue

        # Get basis set information from BSE
        basis_name = basis.lstrip("BSE_")
        basis_block = bse_contact(basis_name, label)

        basis_section += "{}{} 0 \n{}".format(sep, label, basis_block)

    basis_section += "\n"

    # ECP basis sets and pseudopotentials
    pseudo_section = ""
    for it, (label, ecp) in enumerate(ecp_spec.items()):
        # Swap spaces for space identifier
        ecp_name = ecp.replace(" ", "%20")
        # Swap plus for plus identifier
        ecp_name = ecp_name.replace("+", "%2B")
        # Swap brackets for bracket identifiers
        ecp_name = ecp_name.replace("(", "%28")
        ecp_name = ecp_name.replace(")", "%29")
        ecp = bse_contact(ecp_name, label)
        # Split into basis set and pseudopotential parts and add
        # neccessary spacing and packing
        basis_section += "****\n"
        basis_section += ecp.text.split("****")[0]
        if it + 1 == len(ecp_spec):
            basis_section += "****\n"
        try:
            pseudo_section += ecp.text.split("****\n")[1].lstrip("\n")
        except IndexError:
            sys.exit("Error in ECP specification, aborting")

    return basis_section, pseudo_section


def bse_contact(basis_name, label):
    """
    Wrapper for contacting Basis Set Exchange (BSE) to request basis set
    information for a given atom

    Parameters
    -----------
        basis_name : str
            Name of basis set
        label : str
            Label of atom for which basis set is obtained

    Returns
    -------
        str
            Either:
                basis set block if basis set requested
            Or:
                basis set and ecp blocks if ECP requested
    """

    # Try contacting BSE
    try:
        basis_block = _bse_contact(basis_name, label)
    # If connection failed try loading csf proxy
    except ConnectionError:
        try:
            os.system("module load tools/env/proxy")
            basis_block = _bse_contact(basis_name, label)
        # if this fails again alert user
        except ConnectionError:
            message = "Cannot contact Basis Set Exchange"
            message += "\nUse module load tools/env/proxy and try again"
            sys.exit(message)
    # If contact successful but BSE returns basis set not found, alert user
    if not basis_block.ok:
        message = "Error in BSE - {} not found for {}".format(
            basis_name, label
        )
        message += "\nCheck basis set exchange website"
        sys.exit(message)

    return basis_block


def _bse_contact(basis_name, label):
    """
    Wrapper for contacting Basis Set Exchange (BSE) to request basis set
    information for a given atom

    Parameters
    -----------
        basis_name : str
            Name of basis set
        label : str
            Label of atom for which basis set is obtained

    Returns
    -------
        str
            Either:
                basis set block if basis set requested
            Or:
                basis set and ecp blocks if ECP requested
    """

    # Basis set exchange url
    bse_url = "http://basissetexchange.org"

    # Set URL extension to request Stuttgart RSC 1997 ECP in Gaussian
    # format for given atom
    ext = r"/api/basis/{}/format/gaussian94/?header=False&version=0&elements={}".format(basis_name, label) # noqa

    # Make request to BSE
    basis_block = requests.get(
        "{}{}".format(bse_url, ext),
        timeout=5
    )

    return basis_block


def set_chelpg_radii(unique_elements):
    """
    Retrieve list of extra VdW radii needed for chelpg charge decomposition

    Parameters
    -----------
        unique_elements : list
            Atomic labels of unique atoms

    Returns
    -------
        dict
            labels (keys) and VdW radii (values) for non-standard
            radii used in CHELPG charge decomposition
    """

    standard_radii = ["H", "He", "Li", "Be", "B", "C", "N", "O", "F"]

    extra_radii = {
        label: crc_radii[label]
        for label in unique_elements
        if label not in standard_radii
    }

    return extra_radii


def get_method(name):
    """
    Returns Gaussian keyword for requested method/functional

    Parameters
    -----------
        name : str
            Method name from command line

    Returns
    -------
        str
            Method name used by Gaussian
        str
            title line
    """

    name = name.lower()

    if name == "pbe":
        method = "pbepbe"
        dft = "DFT"

    elif name == "pbe0":
        method = "pbe1pbe"
        dft = "DFT"

    elif name == "b3lyp":
        method = "B3LYP"
        dft = "DFT"

    elif name == "tpss":
        method = "TPSSTPSS"
        dft = "DFT"

    elif name == "tpssh":
        method = "TPSSh"
        dft = "DFT"

    elif name == "m062x":
        method = "m062x"
        dft = "DFT"

    elif name == "mp2":
        method = "MP2"
        dft = ""

    else:
        method = None
        print("Method/Functional not found")
        exit()

    return method, dft


def create_title_and_route(method, extra_radii, opt=True, freq=True, ecp=False,
                           chelpg='', extra_route=[], extra_title=""):
    """
    Creates title and routecard for Gaussian com file

    Parameters
    -----------
        method : str
            Either dft functional or mp2
        extra_radii : dict
            Dictionary of labels (keys) and VdW radii (values) for non-standard
            radii used in CHELPG charge decompositon
        opt : bool, default True
            If True, enable optimisation
        freq : bool, default True
            If True, enable frequency calculation
        ecp : bool, default False
            If True, ECP commands will be added to routecard
        chelpg : bool, default False
            If True, carry out a chelpg charge/dipole decomposition of the
            electronic wavefunction
        extra_route : list, optional
            Additional commands to be added to routecard
        extra_title : str, optional
            Additional comments to be added to title line

    Returns
    -------
        str
            Title line for Gaussian com file
        str
            Routecard line for Gaussian com file
    """

    method_name, dft = get_method(method)

    title = "{} {} {}".format(dft, method.upper(), extra_title)

    routecard = "#p "

    if opt:
        title += "OPT "
        routecard += "opt "

    if freq:
        title += "FREQ "
        routecard += "freq=HPModes iop(7/33=3) "

    routecard += " {} ".format(method_name)

    if ecp:
        routecard += "pseudo=read gen "

    if dft:
        routecard += "empiricaldispersion=gd3 int=grid=ultrafine "

    if chelpg == 'charge':
        routecard += "pop=(CHELPG"
    elif chelpg == 'charge_dipole':
        routecard += "pop=(CHELPG, AtomDipole"

    if chelpg and extra_radii:
        routecard += ", ReadRadii) "
    elif chelpg:
        routecard += ") "

    routecard += "scf=(xqc,maxcycle=500) "

    if len(extra_route):
        for ex in extra_route:
            routecard += "{} ".format(ex)

    return title, routecard


def subsititute_element(sub_list, labels, labels_nn):
    """
    Substitute specified atom(s) for others
    Atoms can be given as labels (Dy, C) or labels with numbers (Dy1, C4)
    Allowing for specific subsititutions

    Parameters
    -----------
        sub_list : list
            Pair of atoms to substitute [XX, YY] where XX is replaced by YY
        labels : list
            Atomic labels of each atom with numbers (if present)
        labels_nn : list
            Atomic labels of each atom without numbers

    Returns
    -------
        list
            Atomic labels of each atom with numbers (if present) after swap
        list
            Atomic labels of each atom without numbers after swap
    """

    old = sub_list[0]
    new = sub_list[1]

    # Perform swap for labels and labels_nn
    for it, val in enumerate(labels):
        if old in val:
            labels_nn[it] = xyzp.remove_label_indices([new])[0]
            num = ''
            for c in labels[it]:
                if c.isdigit():
                    num += c
            labels[it] = new+num

    return labels, labels_nn


def substitute_masses(sub_list, labels, labels_nn):
    """
    Substitute mass of specified atoms with specified mass
    Atoms can be given as labels (Dy, C) or labels with numbers (Dy1, C4)
    Allowing for specific mass subsititutions

    Parameters
    -----------
        sub_list : list
            List of atoms and mass to substitute
            [xx,yy,zz,mass, xx, yy, zz, mass]
        labels : list
            Atomic labels of each atom with numbers (if present)
        labels_nn : list
            Atomic labels of each atom without numbers

    Returns
    -------
        labels_nn : str
            New set of atom labels including (Iso=XXX)
    """

    # Create dictionary of atoms (keys) and new mass (vals)
    # for atoms to be substituted
    # The keys may be atom labels with numbers e.g. C5, Dy1
    subs = {}
    for it, val in enumerate(sub_list):
        if not can_float(val):
            curr_atom = val
        if can_float(val):
            subs[curr_atom] = val

    # Search labels with numbers for match if user provided
    # substitution(s) contain labels with numbers e.g. Dy1
    if any([key.isdigit for key in subs.keys()]):
        alist = copy.copy(labels)
    # Or without numbers otherwise e.g. Dy
    else:
        alist = copy.copy(labels_nn)

    # Replace labels with label+mass
    # for specified atoms
    # e.g. Dy --> Dy(Iso=100)
    # e.g. Dy1 --> Dy1(Iso=100)
    for it, label in enumerate(alist):
        if label in subs.keys():
            labels_nn[it] = "{:}(Iso={:})".format(
                labels_nn[it].capitalize(), subs[label]
                )
            labels[it] = "{:}(Iso={:})".format(
                labels[it].capitalize(), subs[label]
                )

    return labels_nn, labels


def create_com_file(charge, mult, f_name_head, labels, coords,
                    basis, pseudo, routecard, title, extra_radii,
                    verbose=True, frozen=[]):
    """
    Create Gaussian com file by compiling title, routecard, geometry,
    basis set, and any other info

    Parameters
    -----------
        charge : int
            Charge of system
        mult : int
            Spin multiplicity of system
        f_name_head : str
            Output file name without extension
        labels : list
            Atomic labels of each atom with numbers
        coords : list
            list of lists of xyz coordinates of each atom
        basis : str
            basis set section
        pseudo : str
            pseudopotentials section
        routecard : str
            routecard line
        title : str
            title line
        extra_radii : dict
            Dictionary of labels (keys) and VdW radii (values) for non-standard
            radii used in CHELPG charge decompositon
        verbose : bool, default True
            If True, warnings will be printed to screen
        frozen : list, optional
            Specifies which atoms move during geometry optimisation process
            List of -1 (frozen) and 0 (unfrozen) for each atom in same order
            as coords
    Returns
    -------
        None
    """

    # Set all atoms as unfrozen if no freezing specified
    if not len(frozen):
        frozen = [0]*len(labels)

    # Create comfile name
    comfile = "{}.com".format(f_name_head)

    # Write comfile
    with open(comfile, "w") as f:

        # Header
        f.write("$RunGauss \n")
        f.write(routecard + "\n")
        f.write("\n")
        f.write(title + "\n")
        f.write("\n")

        # Coordinates
        f.write("{:d} {:d}".format(charge, mult))
        f.write("\n")
        if "opt" in routecard:
            for lab, frz, trio in zip(labels, frozen, coords):
                f.write(
                    "{:5} {:2d}    {:11.7f} {:11.7f} {:11.7f} \n"
                    .format(lab.capitalize(), frz, *trio)
                )
        else:
            for lab, trio in zip(labels, coords):
                f.write(
                    "{:5}     {:11.7f} {:11.7f} {:11.7f} \n"
                    .format(lab.capitalize(), *trio)
                )
        f.write("\n")

        # Basis set information
        # If ECP used, extra CHELPG radii last
        if extra_radii and not len(pseudo):
            for key, val in extra_radii.items():
                f.write("{} {:5.2f}\n".format(key, val))
            f.write("\n")
        f.write(basis)
        f.write("\n")
        f.write(pseudo)
        f.write("\n")
        # If ECP used, extra CHELPG radii last
        if extra_radii and len(pseudo):
            for key, val in extra_radii.items():
                f.write("{} {:5.2f}\n".format(key, val))
        f.write("\n")

    f.close()

    if verbose:
        print("Input file written to {}".format(comfile))
        message = "Generate submission script with \033[0;32m"
        message += "gaussian_suite gen_job {} NCORES \033[0m".format(comfile)
        print(message)

    return


def gen_input(f_name: str, labels: list[str], coords: ArrayLike,
              charge: int, mult: int, method: str, bs_spec: dict[str: str],
              ecp_spec: dict[str:str], subiso: list[int, float] = [],
              chelpg: str = '', opt: bool = True, freq: bool = True,
              extra_route: list[str] = [], extra_title: str = "",
              verbose: bool = True, frozen: list[str] = []):
    """
    Generates Gaussian input .com file ready for use with
    gaussian_suite submit

    Parameters
    -----------

        f_name: str
             Name of final output file
        labels : list
            Atomic labels with or without indexing numbers
        coords : np.ndarray
            x,y,z coordinates of each atom (n_atoms, 3)
        charge : int
            Charge of system
        multiplicity : int
            Spin Multiplicity of system 2S+1
        method : str {"pbe", "pbe0", b3lyp, "tpss", "tpssh", "m062x", "mp2"}
            Method to use
        bs_spec : dict
            Capitalised atomic labels (keys) and basis set specifiers (vals)
            Basis set specifiers must be
            EITHER:
                names of basis sets supported in Gaussian with correct
                capitalisation
                    e.g. cc-pVDZ
            OR
                names of basis sets listed on the basis set exchange, in which
                case the prefix BSE_ must be applied to the name.
                    e.g. BSE_cc-aug-pvtz-pp
        ecp_spec : dict, optional
            atomic labels (keys) and effective corepotential specifiers (vals)
            ECP specifiers must be
                names of basis sets listed on the basis set exchange
                    e.g. RSC1997
        subiso : list, optional
            List lists of atoms to substitute ordered as
                [atom1, atom2, atom2, mass]
            where atomN can contain numbers
            e.g. Dy1 or Dy
        chelpg : str {'charge', 'charge_dipole'}
            If specified, enables decomposition of electronic potential]
            using CHELPG scheme
        opt : bool, default True
            If True enables optimisation
        freq : bool, default True
            If True enables frequency calculation
        extra_route : list, optional
            Additional commands to be added to routecard
        extra_title : str, optional
            Additional comments to be added to title line
        verbose : list, optional
            If True, warnings will be printed to screen
        frozen : list, optional
            Specifies which atoms move during geometry optimisation process
            List of -1 (frozen) and 0 (unfrozen) for each atom in same order
            as coords
    Returns
    -------
        None
    """

    # Remove numbers
    labels_nn = xyzp.remove_label_indices(labels)

    # Get list of which elements are present
    unique_elements = list(set(labels_nn))

    # Trim down basis set specification to only include atoms present in
    # labels
    bs_spec = {
        element: spec for element, spec in bs_spec.items()
        if element in unique_elements
    }

    # Trim down ecp specification to only include atoms present in
    # labels
    ecp_spec = {
        element: spec for element, spec in ecp_spec.items()
        if element in unique_elements
    }

    # Create basis set and ecp specification
    basis, pseudo = create_basis(bs_spec, ecp_spec=ecp_spec)
    if len(pseudo):
        ecp = True
    else:
        ecp = False

    # Generate dictionary of extra radii if chelpg requested
    if chelpg:
        extra_radii = set_chelpg_radii(unique_elements)
    else:
        extra_radii = {}

    # Create routecard and title
    title, routecard = create_title_and_route(
        method,
        extra_radii,
        opt=opt,
        freq=freq,
        ecp=ecp,
        chelpg=chelpg,
        extra_route=extra_route,
        extra_title=extra_title
    )

    # convert subiso elements to floats or capitalized strings as appropriate
    subiso = [
        float(x) if
        can_float(x) else x.capitalize() for x in subiso
    ]

    # Substitute masses if requested
    if subiso:
        labels_nn, labels = substitute_masses(subiso, labels, labels_nn)

    # Create com file
    f_name_head = f_name.split(".")[0]
    create_com_file(charge, mult, f_name_head, labels, coords, basis, pseudo,
                    routecard, title, extra_radii, verbose=verbose,
                    frozen=frozen)
