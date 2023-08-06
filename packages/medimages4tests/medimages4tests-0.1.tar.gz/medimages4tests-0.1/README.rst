Medimages4tests
===============

.. image:: https://github.com/australian-imaging-service/medimages4tests/actions/workflows/test.yml/badge.svg
   :target: https://github.com/australian-imaging-service/medimages4tests/actions/workflows/test.yml
.. image:: https://codecov.io/gh/australian-imaging-service/medimages4tests/branch/main/graph/badge.svg?token=UIS0OGPST7
   :target: https://codecov.io/gh/australian-imaging-service/medimages4tests
.. .. image:: https://img.shields.io/pypi/pyversions/medimages4tests.svg
..    :target: https://pypi.python.org/pypi/medimages4tests/
..    :alt: Supported Python versions
.. .. image:: https://img.shields.io/pypi/v/medimages4tests.svg
..    :target: https://pypi.python.org/pypi/medimages4tests/
..    :alt: Latest Version

Generates dummy medical images, with junk image data but realistic headers,
to test imaging handling pipelines

Installation
------------

Medimage4tests is available on PyPI so to install, simply use pip

.. code-block:: bash

    $ pip3 install medimages4tests
    
or include in your package's ``test_requires``.


Usage
-----

.. code-block:: python

    # Import medimages4tests generator functions
    from medimages4tests.dicom.mri.fmap.ge.discovery_mr888.dv26_0_r05_2008a import sample_image

    # Return generated images in pytest fixtures (or alternative test framework)
    @pytest.fixture()
    def ge_dicom_fmap():
        return sample_image()
