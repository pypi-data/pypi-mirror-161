# powerlaw.py
#
# Create the first row of the covariance matrix for power-law noise models
# using Eq. (7) of Bos et al. (2008).
#
# Bos, MS, Fernandes, RMS, Williams, SDP & Bastos, L (2008). "Fast error 
# analysis of continuous GPS observations". Journal of Geodesy, 82(3), 157-166.
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
# 5/2/2021 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
import sys
import math
from hectorp.control import Control
from hectorp.observations import Observations

#==============================================================================
# Subroutines
#==============================================================================


class Powerlaw:

    def get_Nparam(self):
        """ Return the number of parameters in Power-Law noise model
        
        Returns:
            self.Nparam (int) : total number of parameters === 1 - kappa
        """

        return 1



    def create_t(self,m,k,param):
        """ Create first row of covariance matrix of power-law noise
    
        Args:
            m (int) : length of time series
            k (int) : index of param
            param (array float) : spectral index
        
        Returns:
            t (row (m,1)) : first row Toeplitz covariance matrix 
            k_new (int)   : shifted index in param array
        """

        #--- Constant
        EPS = 1.0e-6

        #--- Parse param
        kappa = param[k]
        k_new = k+1   # increase k for next model

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)

        t[0] = math.gamma(1.0+kappa)/pow(math.gamma(1+0.5*kappa),2.0) 
        for i in range(1,m):
            t[i] = (i - 0.5*kappa - 1.0)/(i + 0.5*kappa) * t[i-1]

        return t, k_new 



    def penalty(self,k,param):
        """ Computes penalty for power-law noise

        Args:
            k (int) : index of param
            param (array float) : spectral index
        
        Returns:
            penalty (float)
        """

        LARGE = 1.0e8
        penalty = 0.0 
        kappa = param[k]
        k += 1           # move one place for next model
        #--- Check range of parameters
        if kappa<-0.998:
            penalty += (-0.998 - kappa)*LARGE
            param[k-1] = -0.998 
        elif kappa>1.998:
            penalty += (kappa - 1.998)*LARGE
            kappa = 1.998
            param[k-1] = 1.998
        return penalty



    def show_results(self,output_single,k,noise_params,sigma):
        """ show estimated noiseparameters

        Args:
            output_single (dictionary) : where values for json file are saved
            k (int) : index where we should start reading noise_params
            noise_params (float-array) : fractions + noise model parameters
            sigma (float) : noise amplitude of power-law noise
        """
      
        #--- Get some info from other classes
        control = Control() 
        observations = Observations()
        unit = control.params['PhysicalUnit']
        try:
            verbose = control.params['Verbose']
        except:
            verbose = True

        if observations.ts_format=='mom':
            T = observations.sampling_period/365.25 # T fraction -> year
            timeunit = 'yr'
        elif observations.ts_format=='msf':
            T = observations.sampling_period/3600.0 # T fraction -> hour
            timeunit = 'h'
        else:
            print('unknown ts_format {0:s}'.format(observations.ts_format))
            sys.exit()

        kappa = noise_params[k]
        d     = -0.5*kappa
        sigma /= math.pow(T,0.5*d)

        if verbose==True: 
            print('sigma     = {0:7.4f} {1:s}/{2:s}^{3:.2f}'.\
						format(sigma,unit,timeunit,0.5*d))
            print('d         = {0:7.4f}'.format(d))
            print('kappa     = {0:7.4f}\n'.format(kappa))

        output_single['sigma'] = sigma
        output_single['d'] = d
        output_single['kappa'] = kappa

        return k+1 
