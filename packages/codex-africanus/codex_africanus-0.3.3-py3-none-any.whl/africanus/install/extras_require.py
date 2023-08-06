# flake8: noqaextras_require = {
   'cuda': ['cupy >= 9.0.0', 'jinja2 >= 2.10'],
   'dask': ['dask[array] >= 2.2.0'],
   'jax': ['jax >= 0.2.11', 'jaxlib >= 0.1.65'],
   'scipy': ['scipy >= 1.4.0'],
   'astropy': ['astropy >= 4.0'],
   'python-casacore': ['python-casacore >= 3.4.0, != 3.5.0'],
   'ducc0': ['ducc0 >= 0.9.0'],
   'testing': ['pytest', 'flaky', 'pytest-flake8 >= 1.0.6', 'flake8 >= 4.0.0, < 5.0.0'],
}
