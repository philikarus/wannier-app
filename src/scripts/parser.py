import re
from distutils.version import LooseVersion
from typing import Any, Optional

import numpy as np
import pandas as pd
import pyprocar
from pandas import MultiIndex
from pymatgen.electronic_structure.plotter import BSPlotter
from pymatgen.io.vasp import BSVasprun
from pyprocar import ProcarParser

from .utils import block_stdout

if LooseVersion(pyprocar.__version__) < LooseVersion("6.0.0"):
    from pyprocar import ProcarSelect
else:
    from pyprocar.core import ProcarSelect


class ParseXmlError(Exception):
    def __init__(self):
        super().__init__("Can't parse xml file")


class ParseKpointsError(Exception):
    def __init__(self):
        super().__init__("Can't parse kpoints file")


class ParseProcarError(Exception):
    def __init__(self):
        super().__init__("Can't parse procar file")


class ParseWannError(Exception):
    def __init__(self):
        super().__init__("Can't parse wannier90_band.dat file")


class VaspParser:
    def __init__(self, vasp_xml: str, kpoint_file: Optional[str] = None):
        try:
            vasprun = BSVasprun(vasp_xml)
            self.atom_list: list[str] = vasprun.atomic_symbols
        except Exception:
            raise ParseXmlError

        if kpoint_file:
            try:
                bs_symm = vasprun.get_band_structure(kpoint_file, line_mode=True)
                bs_plotter = BSPlotter(bs_symm)
                self.efermi = bs_symm.efermi
                self._data = bs_plotter.bs_plot_data(zero_to_efermi=False)
                self.is_spin_polarized = bs_symm.is_spin_polarized
            except Exception:
                raise ParseKpointsError

    @property
    def bands(self):
        # key "1" in self_data["energy"]["1"] always exists whenever it is spin polarized
        return np.vstack([seg.T for seg in self._data["energy"]["1"]]) - self.efermi

    @property
    def bands_up(self):
        return self.bands

    @property
    def bands_down(self):
        if self.is_spin_polarized:
            return (
                np.vstack([seg.T for seg in self._data["energy"]["-1"]]) - self.efermi
            )
        else:
            raise Exception("Not spin polarized")

    @property
    def kpath(self):
        return np.hstack(self._data["distances"])

    @property
    def ticks(self):
        ticks = list(set(self._data["ticks"]["distance"]))
        ticklabels = self._data["ticks"]["label"]
        ticklabels = [ticklabels[0]] + list(set(ticklabels[1:-1])) + [ticklabels[-1]]
        ticklabels = [
            r"$\Gamma$" if label == "GAMMA" else r"{}".format(label)
            for label in ticklabels
        ]
        return {"ticks": ticks, "ticklabels": ticklabels}


class WannParser:
    def __init__(self, bandfile: str, vasp_xml: str | None = None):
        self.bandfile = bandfile
        self.vasp_xml = vasp_xml
        self._data = None

    def read_file(self) -> None:
        try:
            band_data = WannParser._read_wann_data(self.bandfile)

            num_bands = band_data.shape[1] - 1
            columns = [("kpath", "")]
            columns += [("bands", i) for i in range(1, num_bands + 1)]
            band_data.columns = MultiIndex.from_tuples(columns)
            self._data = band_data

            if self.vasp_xml:
                self._offset_by_fermi()
        except Exception:
            raise ParseWannError

    @staticmethod
    def _read_wann_data(bandfile: str):
        bands = []
        band = []
        kpath = []
        with open(bandfile) as f:
            for line in f:
                stripped = line.strip()
                if len(stripped) != 0:
                    band.append(stripped.split()[-1])
                else:
                    bands.append(band)
                    band = []

        with open(bandfile) as f:
            for line in f:
                stripped = line.strip()
                if len(stripped) != 0:
                    kpath.append(stripped.split()[0])
                else:
                    break

        bands = np.array(bands, dtype=np.float64)
        kpath = np.array(kpath, dtype=np.float64)[:, np.newaxis]
        data = pd.DataFrame(np.hstack((kpath, bands.T)))

        return data

    def _offset_by_fermi(self) -> None:
        with open(self.vasp_xml, "r") as f:
            contents = f.read()
        pattern = r'<i name="efermi">\s*([\d.-]+)\s*</i>'
        matches = re.findall(pattern, contents)
        efermi = float(matches[0])
        self._data["bands"] = self._data["bands"] - efermi

        return

    @property
    def bands(self):
        return np.array(self._data["bands"])

    @property
    def kpath(self):
        return np.array(self._data["kpath"])


class ProjParser:
    @block_stdout
    def __init__(self, procar: str, vasp_xml: str):
        self.procar = procar
        self.vasp_xml = vasp_xml
        pc_parser = ProcarParser()
        try:
            pc_parser.readFile(self.procar)
            self.orbitals: list[str] = pc_parser.orbitalName[
                : pc_parser.orbitalCount - 1
            ]
            self._data = ProcarSelect(pc_parser, deepCopy=True)
            self._offset_by_fermi()
        except Exception:
            raise ParseProcarError

    def _offset_by_fermi(self) -> None:
        with open(self.vasp_xml, "r") as f:
            contents = f.read()
        pattern = r'<i name="efermi">\s*([\d.-]+)\s*</i>'
        matches = re.findall(pattern, contents)
        efermi = float(matches[0])
        self.efermi = efermi
        self._data.bands = self._data.bands - efermi

    @property
    def is_spin_polarized(self):
        return self._data.spd.shape[2] == 2

    @property
    def bands(self):
        return self._data.bands

    @property
    def kpath(self):
        diff = self._data.kpoints[1:, :] - self._data.kpoints[0:-1, :]
        segs = np.linalg.norm(diff, axis=1)
        kpath = np.cumsum(segs)
        return kpath

    @property
    def bands_up(self):
        num_bands = int(self._data.bands.shape[-1] / 2)
        return self._data.bands[:, :num_bands]

    @property
    def bands_down(self):
        num_bands = int(self._data.bands.shape[-1] / 2)
        if self.is_spin_polarized:
            return self._data.bands[:, num_bands:]
        else:
            raise Exception("Not spin-polarized")

    @property
    def weights(self):
        return self._data.spd

    @block_stdout
    def select_atom_and_orb(
        self, ispin: list[int], atoms: list[int], orbs: list[int], separate=False
    ) -> None:
        """
        ispin: For nsoc calculation, ispin=[0] denotes the spin density, ispin=[1] denotes the spin magnetization
            For soc calculation, ispin=[0] denotes the spin density and ispin=[1], [2], [3] denotes Sx, Sy, Sz

        atoms: list of atom indices, [0, 1, 2, ...]

        orbs: list of orbital indices, [0, 1, 2, ...] for [
            "s",
            "py",
            "pz",
            "px",
            "dxy",
            "dyz",
            "dz2",
            "dxz",
            "x2-y2",
            "fy3x2",
            "fxyz",
            "fyz2",
            "fz3",
            "fxz2",
            "fzx2",
            "fx3",
            "tot",
        ]
        """
        self._data.selectIspin(ispin, separate=separate)
        self._data.selectAtoms(atoms)
        self._data.selectOrbital(orbs)

        return
