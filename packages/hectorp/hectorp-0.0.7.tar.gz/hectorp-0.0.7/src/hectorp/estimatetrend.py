# -*- coding: utf-8 -*-
#
# This program estimates a trend from the observations.
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
# 29/12/2021 Machiel Bos, Santa Clara
#===============================================================================

import os
import math
import time
import json
import argparse
from matplotlib import pyplot as plt
import numpy as np
from hectorp.control import Control
from hectorp.observations import Observations
from hectorp.designmatrix import DesignMatrix
from hectorp.covariance import Covariance
from hectorp.mle import MLE
from pathlib import Path

#===============================================================================
# Main program
#===============================================================================

def main():

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Estimate trend')

    #--- List arguments that can be given 
    parser.add_argument('-graph', action='store_true', required=False,
                                        help='A graph is shown on screen')
    parser.add_argument('-eps', action='store_true',required=False,
                                        help='Save graph to an eps-file')
    parser.add_argument('-png', action='store_true',required=False,
                                        help='Save graph to an png-file')
    parser.add_argument('-i', required=False, default='estimatetrend.ctl', \
                                      dest='fname', help='Name of control file')


    args = parser.parse_args()

    #--- parse command-line arguments
    graph    = args.graph
    save_eps = args.eps
    save_png = args.png
    fname    = args.fname

    #--- Read control parameters into dictionary (singleton class)
    control = Control(fname)
    try:
        verbose = control.params['Verbose']
    except:
        verbose = True

    if verbose==True:
        print("\n***************************************")
        print("    estimatetrend, version 0.0.7")
        print("***************************************")

   
    #--- Get basename of filename
    datafile = control.params['DataFile']
    unit = control.params['PhysicalUnit']
    try:
        plotname = control.params['PlotName']
    except:
        cols = datafile.split('.')
        plotname = cols[0]

    #--- Call these singleton variables to later have subroutine 'show_results'
    observations = Observations()
    designmatrix = DesignMatrix()
    covariance   = Covariance()

    #--- MLE
    mle = MLE()

    #--- Start the clock!
    start_time = time.time()

    #--- run MLE (least-squares + nelder-mead cycle to find minimum)
    [theta,C_theta,noise_params,sigma_eta] = mle.estimate_parameters()

    #--- The diagonal of C_theta contains variance of estimated parameters
    error = np.sqrt(np.diagonal(C_theta))

    #--- Define 'output' dictionary to create json file with results
    output = {}
    observations.show_results(output)
    mle.show_results(output)
    covariance.show_results(output,noise_params,sigma_eta)
    designmatrix.show_results(output,theta,error)

    #--- Compute xhat, save it as column 'mod' to DataFrame and save it to file
    designmatrix.add_mod(theta)
    fname_out = control.params['OutputFile']
    observations.write(fname_out)

    #--- Get data
    if observations.ts_format=='mom':
        mjd = observations.data.index.to_numpy()
        t   = (mjd-51544)/365.25 + 2000
    else:
        t   = observations.data.index.to_numpy()
    x = observations.data['obs'].to_numpy()
    if 'mod' in observations.data.columns:
        xhat = observations.data['mod'].to_numpy() 

    #--- Show graph?
    if graph==True or save_eps==True or save_png==True:
        fig = plt.figure(figsize=(6, 4), dpi=150)
        plt.plot(t, x, 'b-', label='observed')
        if 'mod' in observations.data.columns:
            plt.plot(t, xhat, 'r-', label='model')

        plt.legend()
        if observations.ts_format=='mom':
            plt.xlabel('Year')
        else:
            plt.xlabel('Seconds of Day')
        plt.ylabel('[{0:s}]'.format(unit))

        if graph==True:
            plt.show()

        if save_eps==True or save_png==True:

            #--- Does the psd_figures directory exists?
            if not os.path.exists('data_figures'):
                os.mkdir('data_figures')

            directory = Path('data_figures')
            if save_eps==True:
                fname = directory / '{0:s}.eps'.format(plotname)
                fig.savefig(fname, format='eps', bbox_inches='tight')
            if save_png==True:
                fname = directory / '{0:s}.png'.format(plotname)
                fig.savefig(fname, format='png', bbox_inches='tight')

    #--- Save dictionary 'output' as json file
    with open('estimatetrend.json','w') as fp:
        json.dump(output, fp, indent=4)

    #--- Show time lapsed
    if verbose==True:
        print("--- {0:8.3f} s ---\n".format(float(time.time() - start_time)))
