import typing as ty
from abc import ABC

from .experiment import Experiment
from .lindhard_factors import lindhard_quenching_factor_semi_conductors, _get_nr_resolution
import numpy as np
import dddm
from functools import partial

export, __all__ = dddm.exporter()


class _BaseSuperCdms(Experiment, ABC):
    """Base class of superCDMS to introduce shared properties"""
    location = "SNOLAB"

    # Parameters needed for eq. 3, 4 of https://arxiv.org/pdf/1610.00006.pdf
    # Since they are not directly used, they are not set as class attributes
    _energy_parameters = dict(

        si_hv={'Z': 14,
               'epsilon': 0.003,
               'e_delta_v': 0.1,
               'e_thr_phonon': 100e-3,
               'sigma_phonon': 5e-3,
               'sigma_ion': np.nan,  # Only phonons
               # https://arxiv.org/pdf/2001.06503.pdf Table III & IV
               'k': 0.161,
               'c0': 0.0091,
               'c1': 3.33e-05,
               'U': 0.15
               },
        si_izip={'Z': 14,
                 'epsilon': 0.003,
                 'e_delta_v': 0.008,
                 'e_thr_phonon': 175e-3,
                 'sigma_phonon': 25e-3,
                 'sigma_ion': 110e-3,
                 # https://arxiv.org/pdf/2001.06503.pdf Table III & IV
                 'k': 0.161,
                 'c0': 9.1e-3,
                 'c1': 3.33e-05,
                 'U': 0.15
                 },
        ge_hv={'Z': 32,
               'epsilon': 0.00382,
               'e_delta_v': 0.1,
               'e_thr_phonon': 100e-3,
               'sigma_phonon': 10e-3,
               'sigma_ion': np.nan,  # Only phonons
               # https://arxiv.org/pdf/2001.06503.pdf Table III & IV
               'k': 0.162,
               'c0': 9.1e-3,
               'c1': 0.62e-05,
               'U': 0.15
               },
        ge_izip={'Z': 32,
                 'epsilon': 0.00382,
                 'e_delta_v': 0.006,
                 'e_thr_phonon': 350e-3,
                 'sigma_phonon': 50e-3,
                 'sigma_ion': 100e-3,
                 # https://arxiv.org/pdf/2001.06503.pdf Table III & IV
                 'k': 0.162,
                 'c0': 9.1e-3,
                 'c1': 0.62e-05,
                 'U': 0.15
                 },
    )

    def get_energy_thr_ee_from_phonon_thr(self) -> ty.Union[float, int]:
        """get the energy threshold (ee) based on the energy_parameters"""
        assert 'migdal' in self.interaction_type
        this_conf = self._energy_parameters[self.detector_key]
        return energy_ee_from_energy_phonon(
            e_ph=this_conf['e_thr_phonon'],
            e_delta_v=this_conf['e_delta_v'],
            epsilon=this_conf['epsilon']
        )

    def get_energy_res_ee_from_phonon_res(self) -> ty.Union[float, int]:
        """get the energy resolution (ee) based on the energy_parameters"""
        assert 'migdal' in self.interaction_type
        this_conf = self._energy_parameters[self.detector_key]
        return energy_ee_from_energy_phonon(
            e_ph=this_conf['sigma_phonon'],
            e_delta_v=this_conf['e_delta_v'],
            epsilon=this_conf['epsilon']
        )

    def energy_nr_to_detectable_energy_function(self) -> ty.Callable:
        """
        Get phonon energy (hv) or ionization energy (izip) from nuclear recoil energy
        """
        assert 'migdal' not in self.interaction_type
        det_key = self.detector_key
        this_conf = self._energy_parameters[det_key]
        if 'izip' in det_key:
            return partial(energy_ionization_from_e_nr,
                           Z=this_conf['Z'],
                           k=this_conf['k'],
                           c0=this_conf['c0'],
                           c1=this_conf['c1'],
                           U=this_conf['U'],
                           )
        if 'hv' in det_key:
            return partial(energy_phonon_from_energy_nr,
                           Z=this_conf['Z'],
                           k=this_conf['k'],
                           e_delta_v=this_conf['e_delta_v'],
                           epsilon=this_conf['epsilon'],
                           c0=this_conf['c0'],
                           c1=this_conf['c1'],
                           U=this_conf['U'],
                           )
        raise ValueError(f'got {det_key}?!')

    @property
    def detector_key(self) -> str:
        material = self.target_material.lower()
        if 'hv' in self.detector_name.lower():
            return f'{material}_hv'
        assert 'izip' in self.detector_name.lower()
        return f'{material}_izip'


@export
class SuperCdmsHvGeNr(_BaseSuperCdms):
    detector_name = 'SuperCDMS_HV_Ge_NR'
    target_material = 'Ge'
    interaction_type = 'SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 44 * 1.e-3  # Tonne year
    energy_threshold_kev = 40. / 1e3  # table VIII, Enr
    cut_efficiency = 0.85  # p. 11, right column
    detection_efficiency = 0.85  # p. 11, left column NOTE: ER type!

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        phonon_energy_from_nr = self.energy_nr_to_detectable_energy_function()
        phonon_resolution = self._energy_parameters[self.detector_key]['sigma_phonon']
        return _get_nr_resolution(energies_in_kev, phonon_energy_from_nr, phonon_resolution)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 27  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsHvSiNr(_BaseSuperCdms):
    detector_name = 'SuperCDMS_HV_Si_NR'
    target_material = 'Si'
    interaction_type = 'SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 9.6 * 1.e-3  # Tonne year
    energy_threshold_kev = 78. / 1e3  # table VIII, Enr
    cut_efficiency = 0.85  # p. 11, right column
    detection_efficiency = 0.85  # p. 11, left column NOTE: ER type!

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        phonon_energy_from_nr = self.energy_nr_to_detectable_energy_function()
        phonon_resolution = self._energy_parameters[self.detector_key]['sigma_phonon']
        return _get_nr_resolution(energies_in_kev, phonon_energy_from_nr, phonon_resolution)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 300  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsIzipGeNr(_BaseSuperCdms):
    detector_name = 'SuperCDMS_iZIP_Ge_NR'
    target_material = 'Ge'
    interaction_type = 'SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 56 * 1.e-3  # Tonne year
    energy_threshold_kev = 272. / 1e3  # table VIII, Enr
    cut_efficiency = 0.75  # p. 11, right column
    detection_efficiency = 0.85  # p. 11, left column

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        ionization_energy_from_nr = self.energy_nr_to_detectable_energy_function()
        ionization_resolution = self._energy_parameters[self.detector_key]['sigma_ion']
        return _get_nr_resolution(energies_in_kev, ionization_energy_from_nr, ionization_resolution)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 3300e-6  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsIzipSiNr(_BaseSuperCdms):
    detector_name = 'SuperCDMS_iZIP_Si_NR'
    target_material = 'Si'
    interaction_type = 'SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 4.8 * 1.e-3  # Tonne year
    energy_threshold_kev = 166. / 1e3  # table VIII, Enr
    cut_efficiency = 0.75  # p. 11, right column
    detection_efficiency = 0.85  # p. 11, left column

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        ionization_energy_from_nr = self.energy_nr_to_detectable_energy_function()
        ionization_resolution = self._energy_parameters[self.detector_key]['sigma_ion']
        return _get_nr_resolution(energies_in_kev, ionization_energy_from_nr, ionization_resolution)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 2900e-6  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsHvGeMigdal(_BaseSuperCdms):
    detector_name = 'SuperCDMS_HV_Ge_Migdal'
    target_material = 'Ge'
    interaction_type = 'migdal_SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 44 * 1.e-3  # Tonne year
    cut_efficiency = 0.85  # p. 11, right column
    detection_efficiency = 0.5  # p. 11, left column NOTE: migdal is ER type!

    @property
    def energy_threshold_kev(self):
        return self.get_energy_thr_ee_from_phonon_thr()

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        e_res_ee = self.get_energy_res_ee_from_phonon_res()
        return self._flat_resolution(len(energies_in_kev), e_res_ee)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 27  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsHvSiMigdal(_BaseSuperCdms):
    detector_name = 'SuperCDMS_HV_Si_Migdal'
    target_material = 'Si'
    interaction_type = 'migdal_SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 9.6 * 1.e-3  # Tonne year
    cut_efficiency = 0.85  # p. 11, right column
    detection_efficiency = 0.675  # p. 11, left column NOTE: migdal is ER type!

    @property
    def energy_threshold_kev(self):
        return self.get_energy_thr_ee_from_phonon_thr()

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        e_res_ee = self.get_energy_res_ee_from_phonon_res()
        return self._flat_resolution(len(energies_in_kev), e_res_ee)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 300  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsIzipGeMigdal(_BaseSuperCdms):
    detector_name = 'SuperCDMS_iZIP_Ge_Migdal'
    target_material = 'Ge'
    interaction_type = 'migdal_SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 56 * 1.e-3  # Tonne year
    cut_efficiency = 0.75  # p. 11, right column
    detection_efficiency = 0.5  # p. 11, left column NOTE: migdal is ER type!

    @property
    def energy_threshold_kev(self):
        return self.get_energy_thr_ee_from_phonon_thr()

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        e_res_ee = self.get_energy_res_ee_from_phonon_res()
        return self._flat_resolution(len(energies_in_kev), e_res_ee)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 22  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


@export
class SuperCdmsIzipSiMigdal(_BaseSuperCdms):
    detector_name = 'SuperCDMS_iZIP_Si_Migdal'
    target_material = 'Si'
    interaction_type = 'migdal_SI'
    __version__ = '0.0.0'
    exposure_tonne_year = 4.8 * 1.e-3  # Tonne year
    cut_efficiency = 0.75  # p. 11, right column
    detection_efficiency = 0.675  # p. 11, left column NOTE: migdal is ER type!

    @property
    def energy_threshold_kev(self):
        return self.get_energy_thr_ee_from_phonon_thr()

    def resolution(self, energies_in_kev):
        """Flat resolution"""
        e_res_ee = self.get_energy_res_ee_from_phonon_res()
        return self._flat_resolution(len(energies_in_kev), e_res_ee)

    def background_function(self, energies_in_kev):
        """Flat bg rate"""
        bg_rate_nr = 370  # counts/kg/keV/year
        conv_units = 1.0e3  # Tonne
        return self._flat_background(len(energies_in_kev), bg_rate_nr * conv_units)


def energy_ee_from_energy_phonon(e_ph, e_delta_v, epsilon):
    """Eq. 4 in https://arxiv.org/abs/1610.00006 rewritten to ee
    (`y`=1) and `eta`=1"""
    return e_ph / (1 + e_delta_v / epsilon)


def energy_phonon_from_energy_nr(e_r_nr, Z, k, e_delta_v, epsilon, c0, c1, U):
    y = lindhard_quenching_factor_semi_conductors(e_r_nr, atomic_number_z=Z, k=k, c0=c0, c1=c1, U=U)
    if not isinstance(y, np.ndarray):
        raise ValueError
    return e_r_nr * (1 + y * (e_delta_v / epsilon))


def energy_ionization_from_e_nr(e_r_nr, Z, k, c0, c1, U):
    y = lindhard_quenching_factor_semi_conductors(e_r_nr, atomic_number_z=Z, k=k, c0=c0, c1=c1, U=U)
    if not isinstance(y, np.ndarray):
        raise ValueError
    return e_r_nr * y
