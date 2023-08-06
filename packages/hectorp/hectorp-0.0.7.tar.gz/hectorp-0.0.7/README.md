
### HectorP

### Table of Contents

1. [Introduction](#introduction)
2. [Code Description](#code)
    1. [Installation](#installation)
    2. [Directory Structure](#directories)
3. [Bugs/Future Work](#bugs)
4. [Utilities](#utilities)
5. [Reference](#references)


### 1. Introduction <a name="introduction"></a>

<p>HectorP is a software package that can be used to estimate a trend in time series with temporal correlated noise. Trend estimation is a common task in geophysical research where one is interested in phenomena such as the increase in temperature, sea level or GNSS derived station position over time. The trend can be linear or a higher degree polynomial and in addition one can estimate periodic signals, offsets and post-seismic deformation. Together they represent the model that is fitted to the observations.</p>

<p>It is well known that in most geophysical time series the noise is correlated in time ([Agnew, 1992](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/91GL02832); [Beran, 1992](https://www.amazon.com/Statistics-Long-Memory-Processes-Monographs-Probability/dp/0412049015)) and this has a significant influence on the accuracy by which the model parameters can be estimated. Therefore, the use of a computer program such as HectorP is advisable. HectorP assumes that the user knows what type of temporal correlated noise exists in the observations and estimates both the model parameters and the parameters of the chosen noise model using the Restricted Maximum Likelihood Estimation (RMLE) method. Since for most observations the choice of noise model can be found from literature or by looking at the power spectral density, this is sufficient in most cases.</p>

<p>Instead of using HectorP, one can also use the [CATS](https://www.ngs.noaa.gov/gps-toolbox/cats.htm) software of Williams (2008). Another alternative is the program [est_noise](https://github.com/langbein-usgs/est_noise) of Langbein (2010). Recent versions include some tricks from Bos et al. (2013) to deal with missing data but with a different way to construct the covariance matrix (Langbein, 2017). HectorP is a complete rewrite of [Hector](https://teromovigo.com/hector/) which is written in C++. The reason for changing the programming language was the need to make maintenance of the code easier. The HectorP (P for Python) has around 8 times less lines of code than Hector (C++). In addition, Hector could not run on Windows and installation on a Mac computer was difficult. HectorP is a truly cross-platform application. I have tried to keep the way HectorP works similar to that of the C++ version to smooth the transition</p>

The reason HectorP is fast is because it makes use of the symmetry in the covariance matrix (i.e., a Toeplitz matrix) to apply fast methods to compute its inverse. Non-stationary noise is approximated by a noise model that becomes stationary at the very, very low frequencies and in this way also a Toeplitz covariance matrix is generated. This is a nutshell the core reason why HectorP is fast. Another part is due to clever usage of the Fast Fourier Transform (FFT).

<p> In the book by [Montillet and Bos (2020)](https://link.springer.com/book/10.1007/978-3-030-21718-1#about) more examples on the analysis of geodetic time series with temporal correlated noise can be found.</p>

<p> The next secion explains how to install HectorP on your computer, the best way to organise your files and the recommended work flow to analyse the time series. For more detailed information, see the Wiki pages on this site.</p>

### 2. Code Description <a name="code"></a>

List of programs provided by the Hector software package.

| Name              | Description                                              |
|:---               |:---                                                      |
| [estimatetrend](./doc/estimatetrend.md) | Main program to estimate a linear trend.                 |
| estimatespectrum  | Program to estimate the power spectral density from the data or residuals using the Welch periodogram method.  |
| modelspectrum     | Given a noise model and values of the noise parameters,  this program computed the associated power spectral density for given frequency range.                       |
| [removeoutliers](./doc/removeoutliers.md) | Program to remove outliers from the data.                |
| findoffset        | Program to find the epoch of a possible offset in the time series.                                             |
| simulatenoise     | Program to files with synthetic coloured noise.          |
| [date2mjd](./doc/date2mjd.md) | Small program to convert calendar date into Modified  Julian Date.                                      |
| [mjd2date](./doc/mjd2date.md) | The inverse of date2mjd.      |


#### 2.i Installation <a name="installation"></a>

Following Python customs, it is best to create a virtual environment by typing on the command line:
```
python3 -m venv env
source env/bin/activate
```

This creates the virtual environment (called and stored in `env`) which is then activated. Next, on the command line type:
```
(env) pip install hectorp
```

That should be it. You can now go to the directory where you have your project and run the hectorp executables. Once you are done, you can exit your virtual environment with:
```
deactivate
```


#### 2.ii Directory Structure <a name="directories"></a>

The following directory structure is recommended to automate the analysis of your time series with HectorP:
```
ori_files
obs_files
pre_files
fin_files
```

The `ori_files` directory is needed if your time series does follow the [HectorP formats](./doc/fileformats.md). HectorP comes with scripts to convert formats 
(e.g., enu, pos, sol) into the mom-format which are then stored in the
`obs_files` directory.

The `obs_files` directory contains the time series files in mom/msf-format. 
Normally one wants to remove outliers and the cleaned time series are stored in 
`pre_files`. These are then analysed with 'estimatetrend' to create a copy of 
the observations with the fitted model in the `fin_files` directory. If you 
look at [example/ex1](./examples/ex1) then this will become clearer.

The advantage of adapting this directory structure is that you can just type `estimate_all_trends` which will look for all files in the `obs_files` directory, remove the outliers, estimate the trends and finally estimates the power spectral density of the residuals.



### 3. Bugs/Future Work <a name="bugs"></a>

Of course, one selling point of Hector is its speed. Having a source code that is easy to maintain is all very well for me, but the user does not care about that. Fortunately, the numpy and scipy libraries are optimised which results in good comparison with the C++ version, see table below.

| N        | C++ (s) | Python (s) |
|:---      |     ---:|        ---:|
| 1000     |       5 |        2.4 |
| 3000     |       6 |        6.7 |
| 5000     |       7 |       13.6 |
| 8000     |      12 |       56.5 |
| 5000 10% |      16 |       63.8 |
| 8000 10% |      33 |       81.0 |
| 5000 20% |      26 |       70.0 |
| 8000 20% |      60 |      140.0 |




### 4. Utilities <a name="utilities"></a>

### 5. References <a name="references"></a>
