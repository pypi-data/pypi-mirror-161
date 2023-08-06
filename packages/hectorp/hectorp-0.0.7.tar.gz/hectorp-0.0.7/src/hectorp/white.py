# white.py
#
# Simple class providing the White noise model
#
#
# This file is part of Hector.
#
# Hector is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software 
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# Hector is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# Hector. If not, see <https://www.gnu.org/licenses/>.
#
# 5/2/2021 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
from hectorp.control import Control

#==============================================================================
# Subroutines
#==============================================================================


class White:

    def get_Nparam(self):
        """ Return the number of parameters in White noise model
        
        Returns
        -------
        self.Nparam (int) : total number of parameters === 0 - None!
        """

        return 0


        
    def create_t(self,m,k,param):
        """ Create first row of covariance matrix of white noise
    
        Arguments
        ---------
        m (int) : length of time series
        k (int) : index of param
        param (array float) : --- nothing ---
        
        Returns
        -------
        t (row (m,1)) : first row Toeplitz covariance matrix 
        k_new (int)   : shifted index in param array
        """

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)
        t[0] = 1.0

        return t, k


  
    def penalty(self,k,param):
        """ Computes penalty for white noise

        Arguments
        ---------
        k (int) : index of param
        param (array float) : --- nothing ---
        
        Returns
        -------
        penalty (float)
        """

        penalty = 0.0 
        return penalty



    def show_results(self,output,k,noise_params,sigma):
        """ show estimated noiseparameters

        Args:
            output_single (dictionary) : where values for json file are saved
            k (int) : index where we should start reading noise_params
            noise_params (float-array) : fractions + noise model parameters
            sigma (float) : noise amplitude of white noise
        """

        #--- Get some info from other classes
        control = Control()
        try:
            verbose = control.params['Verbose']
        except:
            verbose = True

        if verbose==True:
            unit = control.params['PhysicalUnit']
            print('sigma     = {0:7.4f} {1:s}'.format(sigma,unit))
            print('No noise parameters to show\n')

        return k # no shift in index

