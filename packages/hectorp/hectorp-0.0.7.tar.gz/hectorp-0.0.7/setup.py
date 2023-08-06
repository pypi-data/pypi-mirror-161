import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hectorp",
    version="0.0.7",
    author="Machiel Bos",
    author_email="machielbos@protonmail.com",
    description="A collection of programs to analyse geodetic time series",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/machielsimonbos/hectorp",
    project_urls={
        "Bug Tracker": "https://gitlab.com/machielsimonbos/hectorp/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'scipy',
        'mpmath'
    ],
    entry_points ={ 
        'console_scripts': [ 
            'estimatespectrum = hectorp.estimatespectrum:main',
            'modelspectrum = hectorp.modelspectrum:main',
            'estimatetrend = hectorp.estimatetrend:main',
            'estimate_all_trends = hectorp.estimate_all_trends:main',
            'removeoutliers = hectorp.removeoutliers:main',
            'findoffsets = hectorp.findoffsets:main',
            'simulatenoise = hectorp.simulatenoise:main',
            'mjd2date = hectorp.mjd2date:main',
            'date2mjd = hectorp.date2mjd:main',
            'convert_rlrdata2mom = hectorp.convert_rlrdata2mom:main',
        ],
    }
)
