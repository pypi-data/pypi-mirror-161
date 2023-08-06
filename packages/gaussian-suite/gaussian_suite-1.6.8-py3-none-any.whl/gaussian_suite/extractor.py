"""This module contains functions for extracting data from gaussian output and
formatted checkpoint files
"""

import os
import re
import mmap
from itertools import count
import numpy as np
from hpc_suite.store import PlainTextExtractor


def is_fchk(f_name):
    """Predicate, which checks whether file has fchk extension.

    Parameters
    ----------
    f_name : str
        Name of file.

    Returns
    -------
    bool
        True if file has fchk extension.
    """
    if f_name:

        ext = os.path.splitext(f_name)[-1]

        if ext in ['.chk']:
            raise ValueError('Convert Gaussian .chk file to formatted '
                             'checkpoint file with formchk utility first.')

        return ext in ['.fchk']
    else:
        return False


def make_extractor(f_gaussian, select):
    """Resolve selected extractor.

    Parameters
    ----------
    f_gaussian : str
        Gaussian text or .fchk output.
    select : tuple of str
        Pair of item and option string.

    Returns
    -------
    hpc.Store object
        An extractor inheriting from the hpc.Store base class.

    """

    txt_extractors = {
        ("freq", item): (ExtractFreq, {'item': item})
        for item in ["frequency", "ir_intensity", "reduced_mass",
                     "force_constant", "irrep", "displacement"]
    }

    fchk_extractors = {
        ("fchk", "hessian"): "Cartesian Force Constants",
        ("fchk", "atomic_mass"): "Real atomic weights",
        ("fchk", "coordinates"): "Current cartesian coordinates"
    }

    if is_fchk(f_gaussian):
        return FchkExtractor(f_gaussian, fchk_extractors[select])
    else:
        extractor, kwargs = txt_extractors[select]
        return extractor(f_gaussian, **kwargs)


class ExtractFreq(PlainTextExtractor):
    def __init__(self, fchk_file, item, label="occurrence", **kwargs):

        self.item = item

        description = {
            "irrep": "Irreducible representation of the vibration",
            "frequency": "vibrational frequencies",
            "reduced_mass": "reduced masses in the Gaussian convention",
            "force_constant": "force constant",
            "ir_intensity": "intensity of the IR transition",
            "displacement": "cartesian displacement vectors"
        }

        units = {
            "irrep": "",
            "frequency": "cm^-1",
            "reduced_mass": "amu",
            "force_constant": "mDyne/ang",
            "ir_intensity": "km/mol",
            "displacement": ""
        }

        fmt = {
            "irrep": '%s',
            "displacement": '% .5f'
        }

        self.pattern = {
            "index": (r'', r'\d+'),
            "irrep": (r'', r'\w+'),
            "frequency": (r'Frequencies', r'\-?\d+\.\d+'),
            "reduced_mass": (r'Reduced masses', r'\d+\.\d+'),
            "force_constant": (r'Force constants', r'\-?\d+\.\d+'),
            "percent_model": (r'Percent ModelSys', r'\d+\.\d+'),
            "percent_real": (r'Percent RealSys', r'\d+\.\d+'),
            "ir_intensity": (r'IR Intensities', r'\d+\.\d+'),
            "displacement": (r'', r'[- ]\d+\.\d+'),
        }

        header_lines = [
            r'Harmonic frequencies (cm**-1), IR intensities (KM/Mole), Raman scattering',  # noqa
            r'activities (A**4/AMU), depolarization ratios for plane and unpolarized',  # noqa
            r'incident light, reduced masses (AMU), force constants (mDyne/A),',  # noqa
            r'and normal coordinates:'
        ]

        header_pattern = \
            r'\s+'.join([re.escape(line) for line in header_lines])

        self.sec_pattern = \
            header_pattern + r'(\s+' + self.make_chunk_pattern() + r')+'

        super().__init__(fchk_file, item.lower().replace(" ", "_"),
                         description[item], units=units[item],
                         fmt=fmt.get(item, '% .4f'), label=label, **kwargs)

    def make_chunk_pattern(self, label=None):

        chunk_pattern = (
            ''.join(('(?P<data>' if label == item else '') +
                    ('({}\ +\-\-\-\ +{}(\ +{})+\s+)?'.format(*pat, pat[1])
                    if pat[0] else
                    '({}(\ +{})+\s+)?'.format(pat[1], pat[1])) +
                    (')' if label == item else '')
                    for item, pat in self.pattern.items()
                    if item != "displacement") +
            r'Coord Atom Element:\s+' +
            ('(?P<data>' if label == "displacement" else '') +
            r'\d+\ +\d+\ +\d+(\ +[- ]\d+\.\d+)+' +
            r'(\s+\d+\ +\d+\ +\d+(\ +[- ]\d+\.\d+)+)+' +
            (')' if label == "displacement" else '')
        )

        return chunk_pattern

    def __iter__(self):

        counter = count(1)

        with open(self.txt_file, 'r+b') as f:
            # use mmap to buffer file contents
            # as a result, search pattern has to be encoded to byte string
            content = mmap.mmap(f.fileno(), 0)
            sec_it = re.finditer(self.sec_pattern.encode(), content)

        for m in sec_it:
            # get dictionary of matches
            sec = m.group()

            data_it = re.finditer(
                self.make_chunk_pattern(self.item).encode(), sec)

            if self.item == "displacement":
                raw_data = [[re.findall(self.pattern[self.item][1].encode(),
                                        row)
                             for row in n.groupdict()['data'].split(b'\n')]
                            for n in data_it]
            else:
                raw_data = [re.findall(self.pattern[self.item][1].encode(),
                                       n.groupdict()['data'])
                            for n in data_it]

            # format data
            data = self.format_data(raw_data)
            # generate label
            label = self.format_label(counter=counter)

            yield (label, data)

    def format_data(self, data):

        def flatten_data(data_list, dtype=float):
            return np.array(
                [val for chunk in data_list for val in chunk], dtype=dtype)

        def flatten_displacement_data(data_list):
            data = np.array(
                [vals for chunk in data_list for vals in zip(*chunk)],
                dtype=float)

            return np.reshape(data, (data.shape[0], data.shape[1] // 3, 3))

        func = {
            "irrep": lambda x: flatten_data(x, dtype=str),
            "displacement": lambda x: flatten_displacement_data(x)
        }

        return func.get(self.item, flatten_data)(data)


class FchkExtractor(PlainTextExtractor):
    """Extracts Gaussian *.fchk dataset.

    Parameters
    ----------
    fchk_file : str
        Name of Gaussian *.fchk output.
    """
    def __init__(self, fchk_file, item, label=(), **kwargs):

        description = {
            "Cartesian Force Constants": "Cartesian Hessian matrix",
            "Real atomic weights": "atomic masses",
            "Current cartesian corrdinates": "Cartesian coordinates"
        }

        units = {
            "Real atomic weights": 'amu'
        }

        fmt = {
            "Cartesian Force Constants": '% 16.8e',
            "Real atomic weights": '% 16.8e',
            "Current cartesian corrdinates": '% 16.8e'
        }

        self.item = item

        self.header_pattern = \
            item + r'\s+(?P<type>[RI])\s+(N\=\s+((?P<len>\d+))|(?P<data>))'

        self.data_pattern = {
            'R': r'([- ]\d*\.\d+E[+-]\d+)',
            'I': r'(\d+)'
        }

        super().__init__(fchk_file, item.lower().replace(" ", "_"),
                         description.get(item, None),
                         units=units.get(item, 'au'),
                         fmt=fmt.get(item, '%s'), label=label, **kwargs)

    def __iter__(self):

        with open(self.txt_file, 'r') as f:
            for line in f:
                m = re.match(self.header_pattern, line)
                if m:
                    m_dict = m.groupdict()

                    # if scalar data
                    if m_dict['len'] is None:
                        data = m_dict['data']

                    else:
                        num = 0
                        data = []
                        while num < int(m_dict['len']):
                            new_data = re.findall(
                                self.data_pattern[m_dict['type']], next(f))
                            num += len(new_data)
                            data.extend(new_data)

                    yield (self.format_label(), self.format_data(data))

    def format_data(self, data):

        def fill_lower_triangle(arr, dtype=float):
            num = int(-1/2 + np.sqrt(1/4 + 2 * len(arr)))
            mask = np.tri(num, dtype=bool)
            out = np.zeros((num, num), dtype=dtype)
            out[mask] = arr
            return out + np.tril(out, k=-1).T

        func = {
            'Cartesian Force Constants': fill_lower_triangle,
            'Real atomic weights': lambda x: np.array(x, dtype=float),
            'Current cartesian coordinates':
                lambda x: np.reshape(x, (-1, 3)).astype(float)
        }

        return func[self.item](data)
