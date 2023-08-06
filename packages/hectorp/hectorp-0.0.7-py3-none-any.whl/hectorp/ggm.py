# ggm.py
#
# Create the first row of the covariance matrix for Generalised Gauss Markov
# noise.
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
# 12/1/2022 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
import sys
import math
from mpmath import *
from hectorp.control import Control
from hectorp.observations import Observations

#==============================================================================
# Subroutines
#==============================================================================


class GGM:

    def __init__(self,d_fixed=math.nan):
        """ initialise class
        """

        #--- Set precision mpmath
        mp.dps = 25

        #--- Get control parameters
        control = Control()

        #--- Remember the d value used to instantiate this class
        self.d_fixed = d_fixed

        #--- Check if 1-phi is given in control file
        try:
            self.phi_fixed = control.params['GGM_1mphi']
        except:
            self.phi_fixed = math.nan

        #--- Number of noise parameters
        self.Nparam = 2
        if not math.isnan(self.d_fixed):
            self.Nparam -= 1
        if not math.isnan(self.phi_fixed):
            self.Nparam -= 1



    def get_Nparam(self):
        """ Return the number of parameters in GGM noise model
        
        Returns:
            self.Nparam (int) : total number of parameters (free)
        """

        return self.Nparam



    def backward(self,a,b,c,z,F,Fp1):
        """ Compute backward recursion

        Args:
            a,b,c,z (double) : Hypergeometric function 2F1(a,b;c;z)
            Fp1 (double)     : 2F1(a+1,b;c+1;z)

        Returns:
            2F1(a-1,b;c-1;z)
        """

        return ((1.0-c+(b-a)*z)*F + (a*(c-b)*z)*Fp1/c)/(1.0-c)


    
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
        EPS = 1.0e-12

        #--- extract parameters to readable variables
        if self.Nparam==0:
            d     = self.d_fixed
            kappa = -2.0*d
            phi   = self.phi_fixed
            k_new = k
        elif self.Nparam==1:
            kappa = param[k]
            d     = -0.5*kappa
            phi   = self.phi_fixed
            k_new = k+1   # increase k for next model
        else:
            kappa = param[k+0]
            d     = -0.5*kappa
            phi   = param[k+1]
            k_new = k+2   # increase k for next model

        #--- Create first row vector of Covariance matrix
        t = np.zeros(m)

        #--- Create array with hypergeometric 2F1 values
        _2F1 = np.zeros(m)
       
        #--- for phi=0, we have pure power-law noise
        if fabs(phi)<EPS:
            if d>0.5:
                print("kappa< -1.0 ({0:f}) : non-stationary".format(kappa))
                print("1-phi: {0:f}".format(phi))
                sys.exit()
       
            #--- compute power-law noise 
            t[0] = math.gamma(1.0+kappa)/pow(math.gamma(1+0.5*kappa),2.0) 
            for i in range(1,m):
                t[i] = (i - 0.5*kappa - 1.0)/(i + 0.5*kappa) * t[i-1]

        #--- Not pure power-law noise
        else:
            #--- For d=0, _2F1 is always 1.0
            if fabs(d)<EPS:
                for i in range(0,m):
                    _2F1[i] = 1.0
            else:
                #--- Since phi is actually stored as 1-phi, I here need to
                #    put 1- (1-phi) = phi. DONT DELETE THIS COMMENT!!!
                z = math.pow(1-phi,2.0)
                k = m-1
                b = d
                a = d   + float(k)
                c = 1.0 + float(k)
                _2F1[m-1]= hyp2f1(a,b, c, z)
                a -= 1.0
                c -= 1.0
                _2F1[m-2]= hyp2f1(a,b, c, z)

                Fp1 = _2F1[m-1]
                F   = _2F1[m-2]
                for i in range(m-3,-1,-1):
                    _2F1[i] = self.backward(a,b,c,z,F,Fp1)
                    Fm1 = _2F1[i]

                    #--- prepare next round
                    a  -= 1.0
                    c  -= 1.0
                    Fp1 = F
                    F   = Fm1

        #--- finally, construct gamma_x
        scale = 1.0;
        for i in range(0,m):
            t[i]   = scale*_2F1[i]
            scale *= (d+float(i))*(1.0-phi)/(float(i)+1.0)
            if math.isnan(t[i]):
                print("Trouble in paradise!")
                print("i={0:d}, d={1:f}, 1-phi={2:e}".format(i,d,phi))
                sys.exit()
        
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

        if self.Nparam==0:
            penalty = 0.0 
        elif self.Nparam==1:
            kappa = param[k]
            if kappa<-3.0:
                penalty = (3.0 - kappa)*LARGE
                param[k] = -3.0
            elif kappa>0.01:
                penalty = (kappa - 0.01)*LARGE
                param[k] = 0.01
        else:
            d   = -0.5 * param[k]
            phi = param[k+1]

            #--- Extra checks to avoid danger zone
            if phi>0.0:
                y = math.log10(phi)
            else:
                y = 9.9e99         # will not be used

            #--- Check if log(1-phi) is below the line (2F1 is too large)
            safety_factor = 2.0
            if y < (4.0*d - 11.0 + safety_factor):
                penalty = ((4.0*d-11.0+safety_factor) - y)*LARGE
                param[k+1] = pow(10,4.0*d-11.0+safety_factor)

            #--- param[k+1] is always 1-phi. The following rarely occurs
            elif phi>0.999:
                penalty = (phi-0.999)*LARGE
                param[k+1] = 0.999

            #--- The following limit is most critical, stay away from zero!!
            #    Another complication is that at phi=0, you have power-law and
            #    then d_max=0.5. Thus, a jump down from 2. Allowing this is 
            #    asking for trouble. I put lower limit to 1.0e-6.
            elif phi<1.0e-6:
                penalty = (1.0e-6-phi)*LARGE
                param[k+1] = 1.0e-6
                
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

        if self.Nparam==0:
            d = self.d_fixed
            kappa = -2.0*d
            phi = self.phi_fixed
        else:
            kappa = noise_params[k]
            d     = -0.5*kappa
            if self.Nparam==1:
                phi = self.phi_fixed
            else:
                phi = noise_params[k+1]

        sigma /= math.pow(T,0.5*d)
        if verbose==True:
            print('sigma     = {0:7.4f} {1:s}/{2:s}^{3:.2f}'.format(sigma,
								unit,timeunit,0.5*d))

            if self.Nparam==0:
                print('d         = {0:7.4f} (fixed)'.format(d))
                print('kappa     = {0:7.4f} (fixed)'.format(kappa))
                print('1-phi     = {0:7.4f} (fixed)\n'.format(phi))
            elif self.Nparam==1:
                print('d         = {0:7.4f}'.format(d))
                print('kappa     = {0:7.4f}'.format(kappa))
                print('1-phi     = {0:7.4f} (fixed)\n'.format(phi))
            else:
                print('d         = {0:7.4f}'.format(d))
                print('kappa     = {0:7.4f}'.format(kappa))
                print('1-phi     = {0:7.4f}\n'.format(phi))

        output_single['d']     = d
        output_single['kappa'] = kappa
        output_single['1-phi'] = phi
        output_single['sigma'] = sigma

        return k+self.Nparam
