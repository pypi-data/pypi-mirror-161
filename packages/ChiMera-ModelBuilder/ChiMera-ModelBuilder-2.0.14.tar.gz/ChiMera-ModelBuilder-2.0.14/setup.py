#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    "carveme==1.5.1",
    "MarkupSafe==2.0.1",
    "diamond",
    "cobra==0.22.1",
    "escher==1.7.3",
    "psamm==1.1.2",
    "ray",
    "seaborn",
    "matplotlib",
    "bs4",
    "argparse",
    "requests",
    "numpy",
    "plotly",
    "plotly-express",
]

included_files = {
    'ChiMera': [
        'ChiMera/dependencies/all_metabo_paths/',
        'ChiMera/dependencies/all_metabo_paths/carbohydrate_metabolism.json',
        'ChiMera/dependencies/all_metabo_paths/central_carbon_metabolism_final.json',
        'ChiMera/dependencies/all_metabo_paths/central_metabolism.json',
        'ChiMera/dependencies/all_metabo_paths/fatty_acid_beta_oxidation.json',
        'ChiMera/dependencies/all_metabo_paths/fatty_acid_biosynthesis_saturated.json',
        'ChiMera/dependencies/all_metabo_paths/glycolysis_TCA_PPP.json',
        'ChiMera/dependencies/all_metabo_paths/inositol_retinol_metabolism.json',
        'ChiMera/dependencies/all_metabo_paths/nucleotide_metabolism.json',
        'ChiMera/dependencies/all_metabo_paths/partial_amino_acid metabolism.json',
        'ChiMera/dependencies/all_metabo_paths/tryptophan_metabolism.json',
    ]
}


setup(
    name='ChiMera-ModelBuilder',
    version='2.0.14',
    description="ChiMera: An easy-to-use pipeline for Genome-based Metabolic Network reconstruction, evaluation, and visualization.",
    long_description=readme,
    author="Gustavo Tamasco",
    author_email='tamascogustavo@gmail.com',
    url='https://github.com/tamascogustavo/chimera',
    entry_points={
        'console_scripts': [
            'chimera_core=ChiMera.chimera_core:main',
            #'chimera_silencer=ChiMera.tools.silencer:main',
            #'chimera_harvest=ChiMera.tools.path_harvest:main',
        ],
    },
    #   package_dir={'':'src'},
    packages=find_packages(),
    include_package_data=True,
    package_data=included_files,
    install_requires=requirements,
    license="glp3",
    zip_safe=False,
    keywords='ChiMera',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console', 
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    setup_requires=['setuptools_scm']
    #    test_suite='tests',
    #    tests_require=test_requirements,
)
