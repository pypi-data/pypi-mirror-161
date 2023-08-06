# covariance.py
#
# Create the first row of the covariance matrix for various noise models:
#  1) power-law noise using Eq. (7) of Bos et al. (2008).
#  2) white noise
#
# Bos, MS, Fernandes, RMS, Williams, SDP & Bastos, L (2008). "Fast error 
# analysis of continuous GPS observations". Journal of Geodesy, 82(3), 157-166.
#
#
# This file is part of HectorP 0.0.7.
#
# HectorP is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# HectorP is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# HectorP. If not, see <https://www.gnu.org/licenses/>.
#
# 18/ 5/2020 Machiel Bos, Santa Clara
# 29/12/2021 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
import sys
import math
from hectorp.white import White
from hectorp.ggm import GGM
from hectorp.powerlaw import Powerlaw
from hectorp.control import Control
from hectorp.control import SingletonMeta

#==============================================================================
# Subroutines
#==============================================================================


class Covariance(metaclass=SingletonMeta):


    def __init__(self):
        """ initialise class
        """

        #--- Get control parameters
        control = Control()
        try:
            self.verbose = control.params['Verbose']
        except:
            self.verbose = True

        try:
            self.noisemodel_names = control.params['NoiseModels']
            if isinstance(self.noisemodel_names,list)==False:
                self.noisemodel_names = [self.noisemodel_names]
        except Exception as e:
            print(e)
            sys.exit()

        #--- Create list of noise model class instances
        self.noisemodels = []
        i = 0
        for noisemodel_name in self.noisemodel_names:
            if noisemodel_name in ['FlickerGGM','RandomWalkGGM','GGM']:
                ClassName = getattr(sys.modules[__name__], 'GGM')
                if noisemodel_name=='FlickerGGM':
                    class_ = ClassName(0.5)
                elif noisemodel_name=='RandomWalkGGM':
                    class_ = ClassName(1.0)
                else: 
                    class_ = ClassName(math.nan)
            else:
                ClassName = getattr(sys.modules[__name__], noisemodel_name)
                class_ = ClassName() 

            self.noisemodels.append(class_)
            if self.verbose==True:
                print('{0:d}) {1:s}'.format(i,noisemodel_name))
            i += 1

        self.Nmodels = len(self.noisemodels)
        self.Nparam = self.Nmodels-1  # weight parameters

        #--- Do we need to estimate additional noise parameters?
        for noisemodel in self.noisemodels:
            self.Nparam += noisemodel.get_Nparam()
        if self.verbose==True:
            print('Nparam : {0:d}'.format(self.Nparam))           


    def get_Nparam(self):
        """ Return the number of parameters to estimate numerically
        
        Returns:
            self.Nparam (int) : total number of parameters 
        """

        return self.Nparam


        
    def compute_fraction(self,i,param):
        """ Compute fraction of noise model i

        Args:
            i (int) : index of noise model
            param (array float) : parameters describing weight of noise models
        
        Returns:
            fraction (float) : fraction of noise model
        """

        #--- Constant
        hpi = 2.0*math.atan(1.0)

        #--- compute fraction
        if self.Nmodels==1:
            return 1.0
        else:
            fraction = 1.0
            for j in range(0,i):
                fraction *= math.sin(hpi*param[j]);
            if i<self.Nmodels-1:
                fraction *= math.cos(hpi*param[i]);

        #--- Some range checks
        if fraction>1.0:
            fraction = 1.0

        return pow(fraction,2.0)
   


    def compute_penalty(self,param):
        """ penalty for each fraction outside the [0:1] range

        Args:
            param (list float) : fractions of each noise model (Nmodels-1)

        Returns:
            penalty value (float)
        """

        #--- Constant
        LARGE = 1.0e8
 
        #--- first fractions
        penalty = 0.0
        for i in range(0,len(self.noisemodels)-1):
            if param[i]<0.0:
                penalty += (0.0-param[i])*LARGE
                param[i] = 0.0
            elif param[i]>1.0:
                penalty += (param[i]-1.0)*LARGE
                param[i] = 1.0

        #--- Extra penalties for noise model parameters
        k = len(self.noisemodels)-1
        for noisemodel in self.noisemodels:
            penalty += noisemodel.penalty(k,param)

        return penalty



    def create_t(self,m,param):
        """

        Args:
            m (int) : length of time series
            param (array float) : array of parameters to estimate

        Returns:
            t (array float) : first row of covariance matrix
        """

        #--- Create empty autocovariance array
        t = np.zeros(m)

        #--- Add autocovariance of each noise model
        k = self.Nmodels-1
        for i in range(0,self.Nmodels):
            fraction = self.compute_fraction(i,param)
            t_part,k_new = self.noisemodels[i].create_t(m,k,param)

            t += fraction * t_part
            k  = k_new

        return t



    def show_results(self,output,noise_params,sigma_eta):
        """ show estimated noiseparameters

        Args:
            output (dictionary) : where values for json file are saved
            noise_params (float-array) : fractions + noise model parameters
            sigma_eta (float) : driving noise value
        """

        if self.verbose==True:
            print('\nNoise Models\n------------')
        k = self.Nmodels-1
        output_block = {}
        for i in range(0,len(self.noisemodels)):
            noisemodel = self.noisemodels[i]
            output_single = {}
            fraction = self.compute_fraction(i,noise_params)

            if self.verbose==True:
                print('{0:s}:'.format(self.noisemodel_names[i]))
                print('fraction  = {0:7.5f}'.format(fraction))

            sigma = math.sqrt(fraction)*sigma_eta
            output_single['fraction'] = fraction
            output_single['sigma'] = sigma

            k = noisemodel.show_results(output_single,k,noise_params,sigma)

            output_block[self.noisemodel_names[i]] = output_single

        output['NoiseModel'] = output_block
