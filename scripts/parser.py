import re

import numpy as np
import pandas as pd
from pandas import MultiIndex
from pyprocar import ProcarParser, ProcarSelect

from .app_utils import block_stdout


class SimpleParser:
    def __init__(self, bandfile: str, outcar: str | None = None):
        self.bandfile = bandfile
        self.outcar = outcar
        self._data = None

    def read_file(self) -> None:
        band_data = pd.read_csv(
            self.bandfile, comment="#", delim_whitespace=True, header=None
        )

        num_bands = band_data.shape[1] - 1
        columns = [("kpath", "")]
        columns += [("bands", i) for i in range(1, num_bands + 1)]
        columns = MultiIndex.from_tuples(columns)
        band_data.columns = columns
        self._data = band_data

        if self.outcar:
            self._offset_by_fermi()

    def _offset_by_fermi(self) -> None:
        with open(self.outcar, "r") as f_outcar:
            contents = f_outcar.read()
        pattern = r"E-fermi\s*:\s*[-+]?[0-9]*\.?[0-9]+"
        matches = re.findall(pattern, contents)
        matched = matches[0].split(":")[-1].strip()
        efermi = float(matched)
        self._data["bands"] = self._data["bands"] - efermi

        return

    @property
    def bands(self):
        return self._data["bands"]

    @property
    def kpath(self):
        return self._data["kpath"]


class ProParser:
    @block_stdout
    def __init__(self, procar: str, outcar: str | None = None):
        self.procar = procar
        self.outcar = outcar
        pc_parser = ProcarParser()
        pc_parser.readFile(self.procar)
        self._data = ProcarSelect(pc_parser, deepCopy=True)

        if outcar:
            self._offset_by_fermi()

    def _offset_by_fermi(self) -> None:
        with open(self.outcar, "r") as f_outcar:
            contents = f_outcar.read()
        pattern = r"E-fermi\s*:\s*[-+]?[0-9]*\.?[0-9]+"
        matches = re.findall(pattern, contents)
        # get the value of fermi energy
        matched = matches[0].split(":")[-1].strip()
        efermi = float(matched)
        self._data.bands = self._data.bands - efermi

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
        num_spin = int(self._data.spd.shape[2])
        num_bands = int(self._data.bands.shape[-1] / 2)
        if num_spin == 2:
            return self._data.bands[:, num_bands:]
        else:
            raise Exception("Not spin-polarized")

    @property
    def weights(self):
        return self._data.spd

    def select_orb(
        self, ispin: list[int], atoms: list[int], orbs: list[int], separate=True
    ) -> None:
        self._data.selectIspin(ispin, separate=separate)
        self._data.selectAtoms(atoms)
        self._data.selectOrbital(orbs)

        return
