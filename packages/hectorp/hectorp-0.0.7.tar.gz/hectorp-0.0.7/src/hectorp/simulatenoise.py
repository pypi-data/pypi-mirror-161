# -*- coding: utf-8 -*-
#
# This program creates synthetic noise.
#
#  This script is part of HectorP 0.0.7
#
#  HectorP is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  HectorP is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with HectorP. If not, see <http://www.gnu.org/licenses/>
#
# 6/2/2022 Machiel Bos, Santa Clara
#===============================================================================

import os
import math
import time
import sys
import numpy as np
import argparse
from hectorp.control import Control
from hectorp.observations import Observations
from scipy import signal
from pathlib import Path

#===============================================================================
# Subroutines
#===============================================================================

def create_h(m,noisemodel,dt,ts_format):
    """ Create impulse function

    Args:
        m (int) : length of time series
        noisemodel (string) : abreviation of noise model (PL, WL, GGM)
        dt (float) : sampling period in days
        ts_format (string) : 'mom' or 'msf'

    Returns:
        [sigma,h] : noise amplitude + array of float with impulse response
    """

    #--- Constant, small number
    EPS = 1.0e-8

    #--- Array to fill impulse response
    h = np.zeros(m)

    #--- Ask noise parameter values
    if noisemodel=='White':
        print('white noise amplitude: ', end='')
        sigma = float(input())
        h[0] = sigma
    elif noisemodel in ['Powerlaw','Flicker','RandomWalk']:
        if noisemodel=='Powerlaw':
            print('spectral index kappa: ', end='')
            kappa = float(input())
            if kappa<-2.0-EPS or kappa>2.0+EPS:
                print('kappa shoud lie between -2 and 2 : {0:f}'.format(kappa))
                sys.exit()
            d = -kappa/2.0
            print('power-law noise amplitude: ', end='')
        elif noisemodel=='FN':
            d = 0.5
            print('flicker noise amplitude: ', end='')
        else:
            d = 1.0
            print('random walk noise amplitude: ', end='')
        sigma = float(input())
        if ts_format=='mom':
            sigma *= math.pow(dt/365.25,0.5*d)  # Already adjust for scaling
        elif ts_format=='msf':
            sigma *= math.pow(dt/3600.0,0.5*d)  # Already adjust for scaling
        else:
            print('unknown scaling: {0:s}'.format(ts_format))
            sys.exit()

        h[0] = 1.0;
        for i in range(1,m):
            h[i] = (d+i-1.0)/i * h[i-1]
    elif noisemodel=='GGM':
        try:
            phi = control.params['GGM_1mphi']
        except:
            print('factor 1-phi (to avoid 0.999999...): ', end='')
            phi = float(input())
            if phi<0.0 or phi>1.0+EPS:
                print('1-phi should lie between 0 and 1: {0:f}'.format(phi))
                sys.exit()
        print('spectral index kappa: ', end='')
        kappa = float(input())
        if kappa<-2.0-EPS or kappa>2.0+EPS:
            print('kappa shoud lie between -2 and 2 : {0:f}'.format(kappa))
            sys.exit()
        d = -kappa/2.0
        print('power-law noise amplitude: ', end='')
        sigma = float(input())
        if observations.ts_format=='mom':
            sigma *= math.pow(dt/365.25,0.5*d)  # Already adjust for scaling
        elif observations.ts_format=='msf':
            sigma *= math.pow(dt/3600.0,0.5*d)  # Already adjust for scaling
        else:
            print('unknown scaling: {0:s}'.format(observations.ts_format))
            sys.exit()
        h[0] = 1.0;
        for i in range(1,m):
            h[i] = (d+i-1.0)/i * h[i-1] * (1.0-phi)
    else:
        print('Unknown noisemodel: {0:s}'.format(noisemodel))
        sys.exit()


    return [sigma,h]


#===============================================================================
# Main program
#===============================================================================

def main():

    print("\n***************************************")
    print("    simulatenoise, version 0.0.7")
    print("***************************************")

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Simulate noise time series')

    #--- List arguments that can be given 
    parser.add_argument('-i', required=False, default='simulatenoise.ctl', \
                                      dest='fname', help='Name of control file')

    args = parser.parse_args()

    #--- parse command-line arguments
    fname = args.fname

    #--- Read control parameters into dictionary (singleton class)
    control = Control(fname)
    observations = Observations()

    #--- Some variables that define the runs
    directory     = Path(control.params['SimulationDir'])
    label         = control.params["SimulationLabel"]
    n_simulations = control.params["NumberOfSimulations"]
    m             = control.params["NumberOfPoints"]
    dt            = control.params["SamplingPeriod"]
    ms            = control.params["TimeNoiseStart"]
    noisemodels   = control.params['NoiseModels']
    try:
        repeatablenoise = control.params['RepeatableNoise']
    except:
        repeatablenoise = False
    try:
        missingdata = control.params['MissingData']
        perc_missingdata = control.params['PercMissingData']
    except:
        missingdata = False
        perc_missingdata = 0.0
    try:
        includeoffsets = control.params['Offsets']
    except:
        includeoffsets = False


    #--- Start the clock!
    start_time = time.time()

    #--- Already create all the impulse functions
    if isinstance(noisemodels,list)==False:
        noisemodels = [noisemodels]
    n_models = len(noisemodels)
    zeros    = np.zeros(m+ms)
    h        = [zeros]*n_models
    sigma    = [0.0]*n_models
    j = 0
    for noisemodel in noisemodels:
        [sigma[j],h[j]] = create_h(m+ms,noisemodel,dt,observations.ts_format)
        j += 1

    #--- Already create time array
    if observations.datafile=='None' and observations.ts_format=='mom':
        t = np.zeros(m);
        t[0] = 51544.0 # 1 January 2000
        for i in range(1,m):
            t[i] = t[i-1] + dt
    elif observations.datafile=='None' and observations.ts_format=='msf':
        t = np.zeros(m);
        for i in range(1,m):
            t[i] = t[i-1] + dt
    else:
        print('problem, not implemented yet....')
        sys.exit()

    #--- Create random number generator
    if repeatablenoise==True:
        rng = np.random.default_rng(0)
    else:
        rng = np.random.default_rng()

    #--- Does the directory exists?
    if not os.path.exists(directory):
       os.makedirs(directory)

    #--- Run all simulations
    for k in range(0,n_simulations):

        #--- Open file to store time-series
        datafile = label + '_' + str(k) + "." + observations.ts_format
        fname = str(directory.resolve()) + '/' + datafile

        #--- Create the synthetic noise
        y = np.zeros(m)
        for j in range(0,len(sigma)):
            w = sigma[j] * rng.standard_normal(m+ms)
            y += signal.fftconvolve(h[j], w)[0:m]

        #--- convert this into Panda dataframe
        observations.create_dataframe_and_F(t,y,[],dt)

        #--- write results to file
        observations.write(fname)


    #--- Show time lapsed
    print("--- {0:8.3f} seconds ---\n".format(float(time.time() - start_time)))
