"""
Objects required to register derived quantities. Enables
the extension of the `catalogue` object.
"""

import numpy as np
import unyt


class DerivedQuantities(object):
    """
    Derived quantities class. Contains methods to open a python
    source file that creates derived quantities as follows:

    The source file will have access to:

    + numpy (imported as np)
    + unyt (imported as unyt)

    You should write your derived quantities as follows:
    
    .. code-block:: python

        self.derived_quantitiy_name = catalogue.type.field_name * 0.5
        self.derived_quantitiy_name_two = (
            catalogue.type.field_name / catalogue.type.field_name_two
        )


    For example, to register the specific star formation rate in apertures:

    .. code-block:: python

        for aperture_size in [5, 10, 30, 50, 100]:
            stellar_mass = getattr(
                catalogue.apertures,
                f"mass_star_{aperture_size}_kpc"
            )

            star_formation_rate = getattr(
                catalogue.apertures,
                f"sfr_gas_{aperture_size}_kpc"
            )

            ssfr = star_formation_rate / stellar_mass
            # Don't forget to set the name or your plot will be un-labeled!
            ssfr.name = f"Specific SFR ({aperture_size} kpc)"

            setattr(
                self, f"specific_sfr_gas_{aperture_size}_kpc", ssfr
            )
    

    The path to this file should be passed to the __init__ method
    of this class. Note that you should only register quantities that
    you do in fact intend to use, as these are not lazily loaded
    in the same way as the properties that are built into catalogues.
    For example, in the above registration both the star formation rate
    and stellar mass are loaded from the VELOCIraptor catalogue file,
    a behaviour which may not be ideal if the catalogue is very large.

    """

    def __init__(self, registration_file_path: str, catalogue):
        """
        Registers additional (derived) quantities from the 
        VelociraptorCatalogue to itself, using a python
        source file that does this registration inside
        the private _register_quantities() method.

        Parameters
        ----------

        registration_file_path: str
            Path to the python source file. For more information
            on the contents of this file, check out the information
            of this object.

        catalogue: VelociraptorCatalogue
            The catalogue to derive the quantities from.

        
        Returns
        -------
    
        DerivedQuantities
            An instance of the DerivedQuantities class with
            the properties defined in registration_file_path
            available as attributes.
        
        """

        self.registration_file_path = registration_file_path
        self.catalogue = catalogue

        self._register_quantities()

        return

    def _register_quantities(self):
        """
        Registers any required derived quantities using the python
        source file defined in the initialiser.

        """

        catalogue = self.catalogue

        with open(self.registration_file_path, "r") as handle:
            exec(handle.read())

        return
