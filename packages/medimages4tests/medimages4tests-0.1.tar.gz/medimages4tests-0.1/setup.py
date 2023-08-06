import versioneer
from setuptools import setup, find_namespace_packages


setup(
    name='medimages4tests',
    version=versioneer.get_version(),
    author='Thomas G. Close',
    author_email='tom.g.close@gmail.com',
    packages=find_namespace_packages(),
    url='https://github.com/australian-imaging-service/medimages4tests',
    license='CC0',
    description=('Generates dummy medical image data with realistic headers '
                 'to be used in image handling tests'),
    long_description=open('README.rst').read(),
    install_requires=[
        'pydicom>=1.0.2'],
    extras_require={
        'test': [
            'pytest>=5.4.3',
            'pytest-env>=0.6.2',
            'pytest-cov>=2.12.1']},
    include_package_data=True,
    cmdclass=versioneer.get_cmdclass(),
    classifiers=(
        ["Development Status :: 4 - Beta",
         "Intended Audience :: Healthcare Industry",
         "Intended Audience :: Science/Research",
         "License :: OSI Approved :: Apache Software License",
         "Natural Language :: English",
         "Topic :: Scientific/Engineering :: Bio-Informatics",
         "Topic :: Scientific/Engineering :: Medical Science Apps."]
        + ["Programming Language :: Python :: " + str(v)
           for v in ('3.5', '3.6', '3.7', '3.8', '3.9')]),
    keywords='repository analysis medical-imaging neuroimaging workflows pipelines')
