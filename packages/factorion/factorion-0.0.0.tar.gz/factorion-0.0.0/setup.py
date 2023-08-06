# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 04:10:00 2022

@author: dr_ylks
"""

import sys
sys.path.append('.')
from setuptools import setup, find_packages

with open('README.md') as f:
	long_description = f.read()
	
version = "0.0.0"
setup(name="factorion",
	version=version,
	zip_safe=False,
	license="GPLv3",
	author="Dr. Yves-Laurent Kom Samo",
	author_email="github@factorion.ai",
	url="https://www.factorion.ai",
	description = "A Collection of Prediction APIs",
	long_description=long_description,
	long_description_content_type='text/markdown',  # This is important!
	project_urls={
		"Documentation": "https://www.factorion.ai/reference",
		"Source Code": "https://github.com/kxytechnologies/factorion/"},
	download_url = "https://github.com/kxytechnologies/factorion/archive/v%s.tar.gz" % version,
	keywords = ["Prediction API"],
	packages=find_packages(exclude=["tests"]),
	install_requires=["numpy>=1.13.1", "scipy>=1.4.1", "pandas>=0.23.0", "requests>=2.22.0"],
	classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Programming Language :: Python :: 3 :: Only",
		"Development Status :: 5 - Production/Stable",
		"Topic :: Scientific/Engineering :: Artificial Intelligence",
		"Topic :: Scientific/Engineering :: Mathematics"
	],
    scripts=['bin/factorion']
)
