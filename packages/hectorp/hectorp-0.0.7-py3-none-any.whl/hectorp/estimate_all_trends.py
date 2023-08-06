# -*- coding: utf-8 -*-
#
# This program find all files in ./obs_files and estimate all trends.
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
# 21/2/2021 Machiel Bos, Santa Clara
#===============================================================================

import os
import math
import time
import json
import argparse
from glob import glob
from pathlib import Path

#===============================================================================
# Subroutines
#===============================================================================


def create_removeoutliers_ctl_file(station):
    """ Create ctl file for removeoutlier

    Args:
        station : station name (including _0, _1 or _2) of the mom-file
    """

    directory = Path('pre_files')
    fname = str(directory / '{0:s}.mom'.format(station))

    #--- Create control.txt file for removeoutliers
    fp = open("removeoutliers.ctl", "w")
    fp.write("DataFile              {0:s}.mom\n".format(station))
    fp.write("DataDirectory         obs_files\n")
    fp.write("interpolate           no\n")
    fp.write("OutputFile            {0:s}\n".format(fname))
    fp.write("periodicsignals       365.25 182.625\n")
    fp.write("estimateoffsets       yes\n")
    fp.write("estimatepostseismic   yes\n")
    fp.write("estimateslowslipevent yes\n")
    fp.write("ScaleFactor           1.0\n")
    fp.write("PhysicalUnit          mm\n")
    fp.write("IQ_factor             3\n")
    fp.write("Verbose               no\n")
    fp.close()



def create_estimatetrend_ctl_file(station,noisemodels,useRMLE,noseasonal):
    """ Create estimatetrend.ctl

    Args:
        station (string) : name of station
        noisemodels (string) : PLWN, GGMWN, ...
        useRMLE (boolean): use or not use RMLE option
        noseasonal (boolean): do not include seasonal signal in estimation
    """

    directory = Path('mom_files')
    fname = str(directory / '{0:s}.mom'.format(station))

    #--- Create control.txt file for EstimateTrend
    fp = open("estimatetrend.ctl", "w")
    fp.write("DataFile            {0:s}.mom\n".format(station))
    fp.write("DataDirectory       pre_files\n")
    fp.write("OutputFile          {0:s}\n".format(fname))
    fp.write("interpolate         no\n")
    fp.write("PhysicalUnit        mm\n")
    fp.write("ScaleFactor         1.0\n")
    if noseasonal==False:
        fp.write("periodicsignals     365.25 182.625\n")
    fp.write("estimateoffsets     yes\n")
    if noisemodels == 'FNWN':
        fp.write("NoiseModels         FlickerGGM White\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'PLWN':
        fp.write("NoiseModels         GGM White\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'RWFNWN':
        fp.write("NoiseModels         RandomWalkGGM FlickerGGM White\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'RWFN':
        fp.write("NoiseModels         RandomWalkGGM FlickerGGM\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'WN':
        fp.write("NoiseModels         White\n")
    elif noisemodels == 'PL':
        fp.write("NoiseModels         GGM\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'FN':
        fp.write("NoiseModels         FlickerGGM\n")
        fp.write("GGM_1mphi           6.9e-06\n")
    elif noisemodels == 'GGM':
        fp.write("NoiseModels         GGM\n")
    elif noisemodels == 'GGMWN':
        fp.write("NoiseModels         GGM White\n")
    else:
        print("Unknown noise model: {0:s}".format(noisemodels))
        sys.exit()
    if useRMLE==True:
        fp.write("useRMLE             yes\n")
    else:
        fp.write("useRMLE             no\n")
    fp.write("Verbose               no\n")
    fp.close()



def create_estimatespectrum_ctl_file(station):
    """ Create ctl file for estimatespectrum

    Args:
        station : station name (including _0, _1 or _2) of the mom-file
    """

    #--- Create control.txt file for removeoutliers
    fp = open("estimatespectrum.ctl", "w")
    fp.write("DataFile              {0:s}.mom\n".format(station))
    fp.write("DataDirectory         mom_files\n")
    fp.write("interpolate           no\n")
    fp.write("ScaleFactor           1.0\n")
    fp.write("PhysicalUnit          mm\n")
    fp.write("Verbose               no\n")
    fp.close()



#===============================================================================
# Main program
#===============================================================================

def main():

    print("\n*******************************************")
    print("    estimate_all_trends, version 0.0.7")
    print("*******************************************\n")

    #--- Parse command line arguments in a bit more professional way
    parser = argparse.ArgumentParser(description= 'Estimate all trends')

    #--- List arguments that can be given 
    parser.add_argument('-n', dest='noisemodels', action='store',default='PLWN',
       required=False, help="noisemodel combination (PLWN, FL, etc.)")
    parser.add_argument('-s', dest='station', action='store',default='',
       required=False, help="single station name (without .mom extension)")
    parser.add_argument('-useRMLE', action='store_true',
                                    required=False, help="use RMLE option")
    parser.add_argument('-noseasonal', action='store_true',
                                    required=False, help="No seasonal signal")

    args = parser.parse_args()

    #--- parse command-line arguments
    noisemodels = args.noisemodels
    station = args.station
    useRMLE = args.useRMLE
    noseasonal = args.noseasonal

    #--- Start the clock!
    start_time = time.time()

    #--- Read station names in directory ./obs_files
    if len(station)==0:
        directory = Path('obs_files')
        fnames = glob(os.path.join(directory, '*.mom'))
   
        #--- Did we find files?
        if len(fnames)==0:
            print('Could not find any mom-file in obs_files')
            sys.exit()

        #--- Extract station names
        stations = []
        for fname in sorted(fnames):
            station = Path(fname).stem
            stations.append(station)

    else:
        stations = [station]

    #--- Does the pre-directory exists?
    if not os.path.exists('pre_files'):
       os.makedirs('pre_files')

    #--- Does the mom-directory exists?
    if not os.path.exists('mom_files'):
       os.makedirs('mom_files') 

    #--- Analyse station
    output = {}
    for station in stations:

        print(station)

        #--- Remove outliers    
        create_removeoutliers_ctl_file(station)
        os.system('removeoutliers')

        #--- Run estimatetrend
        create_estimatetrend_ctl_file(station,noisemodels,useRMLE,noseasonal)
        os.system('estimatetrend -png')

        #--- parse output
        if os.path.exists('estimatetrend.json')==False:
            print('There is no estimatetrend.json')
            sys.exit()
        try:
            fp_dummy = open('estimatetrend.json','r')
            results = json.load(fp_dummy)
            fp_dummy.close()
        except:
            print('Could not read estimatetrend.json')
            sys.exit()
        output[station] = results

        #--- Estimate Spectrum
        create_estimatespectrum_ctl_file(station)
        os.system('estimatespectrum -model -png')


    #--- Save dictionary 'output' as json file
    with open('hector_estimatetrend.json','w') as fp:
        json.dump(output, fp, indent=4)

    #--- Show time lapsed
    print("--- {0:8.3f} s ---\n".format(float(time.time() - start_time)))
