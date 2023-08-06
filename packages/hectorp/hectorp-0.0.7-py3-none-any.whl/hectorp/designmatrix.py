# designmatrix.py
#
# Create design matrix
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
#  8/ 2/2019 Machiel Bos, Coimbra
# 29/12/2021 Machiel Bos, Santa Clara
#==============================================================================

import numpy as np
from mpmath import *
import sys
import math
from hectorp.control import Control
from hectorp.control import SingletonMeta
from hectorp.observations import Observations

#==============================================================================
# Class definitions 
#==============================================================================
    
class DesignMatrix(metaclass=SingletonMeta):

    def __init__(self):
        """Define the class variables
        """
        #--- get Control parameters (singleton)
        control = Control()
        try:
            self.verbose = control.params['Verbose']
        except:
            self.verbose = True

        #--- Get observations (singleton)
        self.ts = Observations()

        #--- small number
        EPS = 1.0e-4
    
        #--- Legacy stuff: 
        self.periods = []
        try:
            seasonal_signal  = control.params["seasonalsignal"]
            self.periods.append(365.25)
        except:
            pass
        try:
            halfseasonal_signal  = control.params["halfseasonalsignal"]
            self.periods.append(365.25/2.0)
        except:
            pass

        #--- How many periods and offsets do we habe?
        try:
            periodic_signals = control.params['periodicsignals']
        except:
            if self.verbose==True:
                print('No extra periodic signals are included.')
            periodic_signals = []

        if np.isscalar(periodic_signals)==True:
            self.periods.append(periodic_signals)
        else:
            for i in range(0,len(periodic_signals)):
                self.periods.append(periodic_signals[i])

        #--- Degree Polynomial
        try:
            degree_polynomial = control.params["DegreePolynomial"]
        except:
            print("No Polynomial degree set, using offset + linear trend")
            degree_polynomial = 1;
        if (degree_polynomial<0 or degree_polynomial>6):
            print("Only polynomial degrees between 0 and 6 are allowed")
            sys.exit()
      
        #--- length of arrays          
        n_periods      = len(self.periods)
        n_offsets      = len(self.ts.offsets)
        self.n_degrees = degree_polynomial+1
        
        #--- Number of observations
        m = len(self.ts.data.index)
        if m==0:
            print('Zero length of time series!? am crashing...')
            sys.exit()
       
        #--- Remember time halfway between start and end
        self.th = 0.5*(self.ts.data.index[0] + self.ts.data.index[-1])
 
        n = self.n_degrees + 2*n_periods + n_offsets
        self.H = np.zeros((m,n))
        for i in range(0,m):

            #--- Polynomial
            self.H[i,0] = 1.0
            t = self.ts.data.index[i] - self.th
            for j in range(1,self.n_degrees):
                self.H[i,j] = self.H[i,j-1]*t

            #--- Periodic Signal
            for j in range(0,n_periods):
                self.H[i,self.n_degrees+2*j+0] = \
                   math.cos(2*math.pi*i*self.ts.sampling_period/self.periods[j])
                self.H[i,self.n_degrees+2*j+1] = \
                   math.sin(2*math.pi*i*self.ts.sampling_period/self.periods[j])

            #--- Offsets
            for j in range(0,n_offsets):
                if self.ts.offsets[j]<self.ts.data.index[i]+EPS:
                    self.H[i,self.n_degrees+2*n_periods+j] = 1.0



    def compute_amp(self,i,theta,error):
        """ Compute amplitude of periodic signal

        Args:
            i (int) : position in array (index)
            theta (array float): array of cos/sin values
            error (array float): array of associated std values

        Returns:
            amp (float) : estimated amplitude
            amp_err (float) : propagated error
        """

        sigma = 0.5*(error[i] + error[i+1])
        nu  = math.sqrt(pow(theta[i],2.0) + pow(theta[i+1],2.0))
        L12 = hyp1f1(-0.5, 1.0, -pow(nu/sigma,2.0)/2.0)
        amp = float(math.sqrt(math.pi/2.0)*sigma*L12)
        amp_err = float(math.sqrt(2.0*pow(sigma,2.0) + pow(nu,2.0) - \
                  math.pi*pow(sigma,2.0)/2.0*pow(L12,2.0)))

        return [amp,amp_err]



    def compute_pha(self,i,theta,error):
        """ Use Monte Carlo to estimate mean phase and std

        Args:
            i (int) : position in array (index)
            theta (array float): array of cos/sin values
            error (array float): array of associated std values

        Returns:
            amp (float) : estimated amplitude
            amp_err (float) : propagated error
        """

        #--- constant
        deg = 180.0/math.pi

        #--- Mean error of cosine and sine
        sigma = 0.5*(error[i] + error[i+1])
        
        #--- store estimated phase-lag in vector v
        n = 10000
        v = np.empty([n])

        rng = np.random.default_rng()

        x = theta[i+0] + sigma*rng.standard_normal(n)
        y = theta[i+1] + sigma*rng.standard_normal(n)
        v = np.arctan2(y,x)

        pha = v.mean()*deg
        pha_err = v.std()*deg

        return [pha,pha_err]



    def show_results(self,output,theta,error):
        """ Show results from least-squares on screen and save to json-dict

        Args:
            output (dictionary): where the estimate values are saved (json)
            theta (float array) : least-squares estimated parameters
            error (float array) : STD of estimated parameters
        """

        control = Control()
        unit = control.params['PhysicalUnit']
        if self.ts.ts_format=='mom':
            ds = 365.25
            timeunit = 'yr'
        else:
            ds = 3600.0
            timeunit = 'h'

        if self.verbose==True:
            print("bias : {0:.3f} +/- {1:.3f} (at {2:.2f})".\
                                    format(theta[0],error[0],self.th))
							    
            if self.n_degrees>1:
                print("trend: {0:.3f} +/- {1:.3f} {2:s}/{3:s}".\
                             format(ds*theta[1],ds*error[1],unit,timeunit))
            if self.n_degrees>2:
                print("quadratic (half acceleration):" + \
                        "{0:.3f} +/- {1:.3f} {2:s}/{3:s}^2".\
                            format(ds*ds*theta[2],ds*ds*error[2],unit,timeunit))
            for j in range(3,self.n_degrees):
                print("degree {0:d}: {1:.3f} +/- {2:.3f} {3:s}/{4:s}^{0:d}".\
                  format(j,pow(ds,j)*theta[j],pow(ds,j)*error[j],unit,timeunit))
            i = self.n_degrees
            for j in range(0,len(self.periods)):
                [amp,amp_err] = self.compute_amp(i,theta,error)
                [pha,pha_err] = self.compute_pha(i,theta,error)

                print("cos {0:8.3f} : {1:.3f} +/- {2:.3f} {3:s}".format(\
			                  self.periods[j],theta[i],error[i],unit))
                i += 1
                print("sin {0:8.3f} : {1:.3f} +/- {2:.3f} {3:s}".format(\
			                  self.periods[j],theta[i],error[i],unit))
                i += 1
                print("amp {0:8.3f} : {1:.3f} +/- {2:.3f} {3:s}".format(\
			                                 self.periods[j],amp,amp_err,unit))
                print("pha {0:8.3f} : {1:.3f} +/- {2:.3f} degrees".format(\
			                                      self.periods[j],pha,pha_err))
            for j in range(0,len(self.ts.offsets)):
                print("offset at {0:10.4f} : {1:7.2f} +/- {2:5.2f} {3:s}".\
			format(\
		         self.ts.offsets[j],theta[i],error[i],unit)); i += 1

        #--- JSON
        if self.n_degrees>1:
            output['trend'] = ds*theta[1]
            output['trend_sigma'] = ds*error[1]
        if self.n_degrees>2:
            output['quadratic'] = ds*ds*theta[2]
            output['quadratic_sigma'] = ds*ds*error[2]
        for j in range(3,self.n_degrees):
            output['degree{0:3}'.format(j)] = pow(ds,j)*theta[j]
            output['degree{0:3}_sigma'.format(j)] = pow(ds,j)*error[j]

        i = self.n_degrees
        for j in range(0,len(self.periods)):
            [amp,amp_err] = self.compute_amp(i,theta,error)
            [pha,pha_err] = self.compute_pha(i,theta,error)
            output["amp_{0:.3f}".format(self.periods[j])]       = amp 
            output["amp_{0:.3f}_sigma".format(self.periods[j])] = amp_err
            output["pha_{0:.3f}".format(self.periods[j])]       = pha 
            output["pha_{0:.3f}_sigma".format(self.periods[j])] = pha_err

            output["cos_{0:.3f}".format(self.periods[j])] = theta[i] 
            output["cos_{0:.3f}_sigma".format(self.periods[j])] = error[i]
            i += 1 
            output["sin_{0:.3f}".format(self.periods[j])] = theta[i] 
            output["sin_{0:.3f}_sigma".format(self.periods[j])] = error[i]
            i += 1 
        output['jump_epochs'] = self.ts.offsets
        output['jump_sizes'] = theta[i:].tolist()
        output['jump_sigmas'] = error[i:].tolist()



    def add_mod(self,theta):
        """ Compute xhat and add it to the Panda Dataframe

        Args:
            theta (array float): contains estimated least-squares parameters

        """

        xhat = self.H @ theta
        self.ts.add_mod(xhat)
