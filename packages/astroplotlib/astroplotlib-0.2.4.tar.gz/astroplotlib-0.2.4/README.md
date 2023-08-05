# astroplotlib

Python scripts to handle astronomical images. It allows the user building images
with any scale, overlay contours, and adding physical bars and orientation
arrows (N and E axes) automatically (e.g., [Hernandez-Jimenez 13](https://ui.adsabs.harvard.edu/abs/2013MNRAS.435.3342H/abstract), [15](https://ui.adsabs.harvard.edu/abs/2015MNRAS.451.2278H/abstract)). It is
possible to overlay pseudo-slits and obtain statistics from apertures
(e.g., [Dametto, N. Z. et al. 2014](https://ui.adsabs.harvard.edu/abs/2014MNRAS.443.1754D/abstract)). The user can also estimate the background
sky of the images (e.g., [Buzzo 2021](https://ui.adsabs.harvard.edu/abs/2021MNRAS.504.2146B/abstract)). There is a module to work with the output
table from the `Ellipse` task of `IRAF`.  The user can overlay the fitted isophotes
and their respective contours on the image (e.g.,  [Mora et al. 2019](https://ui.adsabs.harvard.edu/abs/2019MNRAS.488..830M/abstract),
[Buzzo et al. 2021](https://ui.adsabs.harvard.edu/abs/2021MNRAS.504.2146B/abstract), [Brito-Silva et al. 2021](https://ui.adsabs.harvard.edu/abs/2021arXiv211004423B/abstract)). The package also has a GUI  to mask
areas in the images by using different polygons.  It is possible to obtain
statistical information (e.g, total flux, mean, std, etc.) from the masked areas
too. There is also a GUI  to overlay star catalogues on the image and an option
to download them directly from the Vizier server.

version: 0.2.3

(c) 2014-2022 J. A. Hernandez-Jimenez

E-mail: joseaher@gmail.com

Website: https://gitlab.com/joseaher/astroplotlib

## Installation

astroplotlib requires:

    * numpy
    * scipy
    * matplotlib
    * astropy
    * astroquery
    * tkinter

This version can be easily installed within Anaconda Enviroment via PyPI:

    % pip install astroplotlib

If you prefer to install astroplotlib manually, you can clone the developing
version at https://gitlab.com/joseaher/astroplotlib. In the directory this
README is in, simply:

    % pip install .

or,

    % python setup.py install

## Uninstallation

To uninstall astroplotlib, simply

    % pip uninstall astroplotlib

## Citing

If you use this package for a scientific publication, please cite it ([Hernandez-Jimenez 2022](https://ascl.net/2204.002)). The BibTeX entry for this package is:

```
  @MISC{2022ascl.soft04002H,
        author = {{Hernandez-Jimenez}, Jose A.},
        title = "{Astroplotlib: Python scripts to handle astronomical images}",
        keywords = {Software},
        howpublished = {Astrophysics Source Code Library, record ascl:2204.002},
        year = 2022,
        month = apr,
        eid = {ascl:2204.002},
        pages = {ascl:2204.002},
        archivePrefix = {ascl},
        eprint = {2204.002},
        adsurl = {https://ui.adsabs.harvard.edu/abs/2022ascl.soft04002H},
        adsnote = {Provided by the SAO/NASA Astrophysics Data System}
       }
```
## Acknowledgements

This software was funded partially by Brazilian agency FAPESP, process number 2021/08920-8.
