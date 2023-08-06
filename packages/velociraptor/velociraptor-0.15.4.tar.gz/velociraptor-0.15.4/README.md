Velociraptor Python Library
===========================

[![Documentation Status](https://readthedocs.org/projects/velociraptor-python/badge/?version=latest)](https://velociraptor-python.readthedocs.io/en/latest/?badge=latest)

[Velociraptor](http://github.com/pelahi/velociraptor-stf) catalogues provide
a signifciant amount of information, but applying units to it can be painful.
Here, the `unyt` python library is used to automatically apply units to
velociraptor data and perform generic halo-catalogue reduction. This library
is primarily intended to be used on [SWIFT](http://swiftsim.com) data that
has been post-processed with velociraptor, but can be used for any
velociraptor catalogue.

The internals of this library are based heavily on the internals of the
[`swiftsimio`](http://github.com/swiftsim/swiftsimio) library, and essentially
allow the velociraptor catalogue to be accessed in a lazy, object-oriented
way. This enables users to be able to reduce data quickly and in a
computationally efficient manner, without having to resort to using the
`h5py` library to manually load data (and hence manually apply units)!

Requirements
------------

The velociraptor library requires:

+ `unyt` and its dependencies
+ `h5py` and its dependencies
+ `python3.6` or above

Note that for development, we suggest that you have `pytest` and `black`
installed. To create the plots in the example directory, you will need
the plotting framework `matplotlib`.

Installation
------------

You can install this library from PyPI using:
```
pip3 install velociraptor
```

Documentation
-------------

Full documentation is available on [ReadTheDocs](https://velociraptor-python.readthedocs.io/).

Why a custom library?
---------------------

This custom library, instead of something like `pandas`, allows us to
only load in the data that we require, and provide significant
context-dependent features that would not be available for something
generic. One example of this is the automatic labelling of properties,
as shown in the below example.

```python
from velociraptor import load
from velociraptor.tools import get_full_label

catalogue = load("/path/to/catalogue.properties")

stellar_masses = catalogue.apertures.mass_star_30_kpc
stellar_masses.convert_to_units("msun")

print(get_full_label(stellar_masses))
```
This outputs "Stellar Mass $M_*$ (30 kpc) $\left[M_\odot\right]$", which is
easy to add as, for example, a label on a plot.
