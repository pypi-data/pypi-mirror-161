#!/usr/bin/env python3

from setuptools import setup #, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
	long_description = fh.read()

# setup(
# 	name = "joby_m_anthony_iii",
# 	version = "2.0.0",
# 	author = "Joby M. Anthony III",
# 	author_email = "jmanthony1@liberty.edu",
# 	description = "Numerical methods/techniques.",
# 	long_description=long_description,
# 	long_description_content_type="text/markdown",
# 	url = "https://github.com/jmanthony3/joby_m_anthony_iii.git",
# 	packages=find_packages('src'),
#     package_dir={'':'src'},
# 	classifiers = [
# 		"Programming Language :: Python :: 3",
# 		"License :: OSI Approved :: MIT License",
# 		"Operating System :: OS Independent",
# 	],
# 	platforms = "any"
# )

setup()