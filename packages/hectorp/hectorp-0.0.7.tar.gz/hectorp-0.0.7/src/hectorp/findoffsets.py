# -*- coding: utf-8 -*-
#
# Perform cycles of offset detection for a single station [optionally 3D]
#  1) Compute noise and SLT model parameters
#  2) Compute for each epoch the new log-likelihood when an offset is added
#     but maintaining the noise parameters constant.
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
# 2/1/2022 Machiel Bos, Santa Clara
#===============================================================================

import os
import math
import time
import json
import argparse
import numpy as np
from hectorp.control import Control
from hectorp.control import SingletonMeta
from hectorp.observations import Observations
from hectorp.designmatrix import DesignMatrix
from hectorp.covariance import Covariance
from hectorp.mle import MLE

#===============================================================================
# Subroutines
#===============================================================================

def create_ctl_file(fname,station,noisemodels,useRMLE):
    """ Create findoffsets.ctl

    Args:
        fname (string) : name of ctl-file
        station (string) : name of station
        noisemodels (string) : PLWN, GGMWN, ...
        useRMLE (boolean) : use RMLE in analyses or not
    """

    #--- Create control.txt file for EstimateTrend
    fp = open(fname, "w")
    fp.write("DataFile            {0:s}.mom\n".format(station))
    fp.write("DataDirectory       ./raw_files\n")
    fp.write("OutputFile          ./obs_files/{0:s}.mom\n".format(station))
    fp.write("PhysicalUnit        mm\n")
    fp.write("ScaleFactor         1.0\n")
    fp.write("periodicsignals     365.25 182.625\n")
    fp.write("estimateoffsets     yes\n")
    if noisemodels == 'FNWN':
        fp.write("NoiseModels         FlickerGGM White\n")
    elif noisemodels == 'PLWN':
        fp.write("NoiseModels         GGM White\n")
    elif noisemodels == 'RWFNWN':
        fp.write("NoiseModels         RandomWalkGGM FlickerGGM White\n")
    elif noisemodels == 'WN':
        fp.write("NoiseModels         White\n")
    elif noisemodels == 'PL':
        fp.write("NoiseModels         GGM\n")
    elif noisemodels == 'FL':
        fp.write("NoiseModels         FlickerGGM\n")
    else:
        print("Unknown noise model: {0:s}".format(noisemodels))
        sys.exit()
    fp.write("GGM_1mphi           6.9e-06\n")
    if useRMLE==True:
        fp.write("useRMLE             yes\n")
    else:
        fp.write("useRMLE             no\n")
    fp.close()

        

#===============================================================================
# Main program
#===============================================================================

def main():

    print("\n***************************************")
    print("    findoffsets, version 0.0.7")
    print("***************************************")

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Find offsets in time series')

    #--- List arguments that can be given 
    parser.add_argument('-s', dest='station', action='store', required=True,
        default='findoffset.ctl', help="The name of the ctl-file")
    parser.add_argument('-t', dest='threshold', action='store', required=False,
        default='20.0', help="The MLE difference considered significant") 
    parser.add_argument('-threeD', action='store_true',
       required=False, help="process east, north and up at same time")
    parser.add_argument('-n', dest='noisemodels', action='store',default='PLWN',
       required=False, help="noisemodel combination (PLWN, FL, etc.)")
    parser.add_argument('-verbose', action='store_true', 
       required=False, help="Verbosity (save values each step in file)")
    parser.add_argument('-i', required=False, default='findoffset.ctl', \
                                      dest='fname', help='Name of control file')
    parser.add_argument('-useRMLE', action='store_true',
                                    required=False, help="use RMLE option")

    args = parser.parse_args()

    #--- parse command-line arguments
    use_3D      = args.threeD
    useRMLE     = args.useRMLE
    station     = args.station
    threshold   = float(args.threshold)
    noisemodels = args.noisemodels
    verbose     = args.verbose
    fname       = args.fname

    #--- If use_3D then already create correct filenames
    if use_3D==True:
        stations = []
        for i in range(3):
            stations.append('{0:s}_{1:d}.dat'.format(station,i))
    else:
        stations = [station]

    #--- Start the clock!
    start_time = time.time()

    #--- Create and read control parameters into dictionary (singleton class)
    create_ctl_file(fname,stations[0],noisemodels,useRMLE)
    control = Control(fname)

    #--- Just create Observations to get number of observations m
    observations = Observations()
    m            = observations.m

    #--- For each time series, compute new MLE for each possible offset and sum
    #    the results.
    j = 0
    new_offsets = []
    while True:

        #--- array to store log-likelihood differences (new - old) values
        dln_L_sum = np.zeros(m)

        for station in stations:

            #--- each time series, start with a clean instantiation of classes
            SingletonMeta.clear_all()
            create_ctl_file(fname,station,noisemodels,useRMLE)
            control = Control(fname)
            observations = Observations()
            for t in new_offsets:
                observations.add_offset(t) # add new offsets to class
            covariance   = Covariance()
            mle          = MLE()
  
            #--- Test for this time series the effect of adding offset at each t
            dln_L = mle.test_new_offset()

            #--- Show information on screen
            if verbose==True:
                max_value = max(dln_L)
                index     = dln_L.index(max_value)
                t         = observations.data.index[index] 
                print('==> {0:s} - best offset at {1:9.2f} : {2:9.3f}'.\
						format(station,t,max_value))

            #--- Simply sum delta log-likelihoods 
            dln_L_sum += dln_L 

        max_value = max(dln_L_sum)
        result = np.where(dln_L_sum==max_value)
        index = result[0][0]
        t = observations.data.index[index] 
        print('************************************************************')
        print('best offset at {0:9.2f} (index {1:d}) : {2:9.3f}'.
					format(t,index,max_value))
        print('************************************************************')

        if verbose==True:
            with open('findoffset_{0:d}.out'.format(j),'w') as fp:
                for i in range(0,m):
                    if not math.isnan(observations.data.iloc[i,0]):
                        fp.write('{0:11.5f} {1:10.5f}\n'.\
					format(observations.data.index[i],
								dln_L_sum[i]))

        #--- If significant, store the found offset
        if max_value>threshold:
            new_offsets.append(t)
        else:
            break

        #--- prepare next round
        j += 1


    #--- Save dictionary 'output' as json file
    output = {}
    output['offsets'] = new_offsets
    with open('findoffsets.json','w') as fp:
        json.dump(output, fp, indent=4)

    #--- Save result to obs_files directory
    fname_out = control.params['OutputFile']
    observations.write(fname_out)

    #--- Show time lapsed
    print("--- {0:8.3f} seconds ---\n".format(float(time.time() - start_time)))
