"""
Routines that provide translation of velociraptor quantities into something a
little more human readable, or to internal quantities.
"""

import unyt

from velociraptor.units import VelociraptorUnits


def typo_correct(particle_property_name: str):
    """
    Corrects for any typos in field names that may exist.
    """

    key = {"veldips": "veldisp"}

    if particle_property_name in key.keys():
        return key[particle_property_name]
    else:
        return particle_property_name


def get_aperture_unit(unit_name: str, unit_system: VelociraptorUnits):
    """
    Converts the velociraptor strings to internal velociraptor units 
    from the naming convention in the velociraptor files.
    """

    # Correct any typos
    corrected_name = typo_correct(unit_name).lower()

    key = {
        "sfr": unit_system.star_formation_rate,
        "zmet": unit_system.metallicity,
        "mass": unit_system.mass,
        "npart": unyt.dimensionless,
        "rhalfmass": unit_system.length,
        "veldisp": unit_system.velocity,
        "r": unit_system.length,
        "lx": unit_system.length * unit_system.velocity,
        "ly": unit_system.length * unit_system.velocity,
        "lz": unit_system.length * unit_system.velocity,
    }

    return key.get(corrected_name, None)


def get_particle_property_name_conversion(name: str, ptype: str):
    """
    Takes an internal velociraptor particle property and returns
    a fancier name for use in plot legends. Typically used for the
    complex aperture properties.
    """

    corrected_name = typo_correct(name)

    combined_name = f"{corrected_name}_{ptype}".lower()

    key = {
        "sfr_": "SFR $\dot{\\rho}_*$",
        "sfr_gas": "Gas SFR $\dot{\\rho}_*$",
        "zmet_": "Metallicity $Z$",
        "zmet_gas": "Gas Metallicity $Z_{\\rm g}$",
        "zmet_star": "Star Metallicity $Z_*$",
        "zmet_bh": "Black Hole Metallicity $Z_{\\rm BH}$",
        "mass_": "Mass $M$",
        "mass_gas": "Gas Mass $M_{\\rm g}$",
        "mass_star": "Stellar Mass $M_*$",
        "mass_bh": "Black Hole Mass $M_{\\rm BH}$",
        "mass_interloper": "Mass of Interlopers",
        "npart_": "Number of Particles $N$",
        "npart_gas": "Number of Gas Particles $N_{\\rm g}$",
        "npart_star": "Number of Stellar Particles $N_*$",
        "npart_bh": "Black Hole Mass $N_{\\rm BH}$",
        "npart_interloper": "Number of Interlopers",
        "rhalfmass_": "Half-mass Radius $R_{50}$",
        "rhalfmass_gas": "Gas Half-mass Radius $R_{50, {\\rm g}}$",
        "rhalfmass_star": "Stellar Half-mass Radius $R_{50, *}$",
        "rhalfmass_bh": "Black Hole Half-mass Radius $R_{50, {\\rm BH}}$",
        "r_": "Radius $R_{\\rm SO}$",
        "veldisp_": "Velocity Dispersion $\sigma$",
        "veldisp_gas": "Gas Velocity Dispersion $\sigma_{\\rm g}}$",
        "veldisp_star": "Stellar Velocity Dispersion $\sigma_{*}$",
        "veldisp_bh": "Black Hole Velocity Dispersion $\sigma_{\\rm BH}$",
        "subgridmasses_aperture_total_solar_mass_bh": "Subgrid Black Hole Mass $M_{\\rm BH}$",
    }

    return key.get(combined_name, corrected_name)
