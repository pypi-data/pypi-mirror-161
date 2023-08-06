# -*- coding: utf-8 -*-
#
# This program removes outliers from the observations.
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
import json
import numpy as np
import argparse
from matplotlib import pyplot as plt
from hectorp.datasnooping import DataSnooping
from hectorp.control import Control
from hectorp.observations import Observations
from pathlib import Path

#===============================================================================
# Main program
#===============================================================================

def main():

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Remove outliers')

    #--- List arguments that can be given
    parser.add_argument('-graph', action='store_true', required=False,
                                        help='A graph is shown on screen')
    parser.add_argument('-eps', action='store_true',required=False,
                                        help='Save graph to an eps-file')
    parser.add_argument('-png', action='store_true',required=False,
                                        help='Save graph to an png-file')
    parser.add_argument('-i', required=False, default='removeoutliers.ctl', \
                                      dest='fname', help='Name of control file')

    args = parser.parse_args()

    #--- parse command-line arguments
    graph    = args.graph
    save_eps = args.eps
    save_png = args.png
    fname    = args.fname

    #--- Read control parameters into dictionary (singleton class)
    control = Control(fname)
    datafile = control.params['DataFile']
    unit = control.params['PhysicalUnit']
    try:
        plotname = control.params['PlotName']
    except:
        cols = datafile.split('.')
        plotname = cols[0]
    try:
        verbose = control.params['Verbose']
    except:
        verbose = True

    if verbose==True:
        print("\n***************************************")
        print("    removeoutliers, version 0.0.7")
        print("***************************************")

    #--- Get Classes
    datasnooping = DataSnooping()
    observations = Observations()

    #--- Get data
    if observations.ts_format=='mom':
        mjd = observations.data.index.to_numpy()
        t   = (mjd-51544)/365.25 + 2000
    else:
        t   = observations.data.index.to_numpy()
    x = np.copy(observations.data['obs'].to_numpy())

    #--- Start the clock!
    start_time = time.time()

    #--- Define 'output' dictionary to create json file with results
    output = {}
    datasnooping.run(output)

    #--- Get filtered data
    x_new = observations.data['obs'].to_numpy()

    #--- Show graph?
    if graph==True or save_eps==True or save_png==True:
        fig = plt.figure(figsize=(6, 4), dpi=150)
        plt.plot(t, x, 'b-', label='observed')
        plt.plot(t, x_new, 'r-', label='filtered')
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

    #--- save cleaned time series to file
    fname_out = control.params['OutputFile']
    observations.write(fname_out)

    #--- Save dictionary 'output' as json file
    with open('removeoutliers.json','w') as fp:
        json.dump(output, fp, indent=4)

    #--- Show time lapsed
    if verbose==True:
        print("--- {0:8.3f} s ---\n".format(float(time.time() - start_time)))
