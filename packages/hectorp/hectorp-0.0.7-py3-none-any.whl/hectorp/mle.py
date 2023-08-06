# mle.py
#
# Class which computes the log-likelihood and searches for the maximum value.
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
#  6/6/2020 David Bugalho & Machiel Bos
# 12/2/2022 Machiel Bos
#===============================================================================

import numpy as np
import sys
import math
from hectorp.observations import Observations
from hectorp.designmatrix import DesignMatrix
from hectorp.covariance import Covariance
from hectorp.fullcov import FullCov
from hectorp.ammargrag import AmmarGrag
from hectorp.ols import OLS
from hectorp.control import Control
from scipy.optimize import minimize

#==============================================================================
# Subroutines
#==============================================================================

class MLE:

    def __init__(self):
        """ initialise class
        """

        #--- Get control parameters
        control = Control()
        try:
            self.verbose = control.params['Verbose']
        except:
            self.verbose = True

        #--- useRMLE
        try:
            self.useRMLE = control.params['useRMLE']
        except:
            self.useRMLE = False
        if self.verbose==True:
            print('useRMLE->',self.useRMLE)

        #--- Get other classes
        obs = Observations()
        des = DesignMatrix()
        self.cov = Covariance()

        #--- Copy observations and design matrix into class 
        self.x   = obs.data['obs'].to_numpy()
        self.H   = des.H
        self.F   = obs.F

        (m,k) = self.F.shape
        (m,n) = self.H.shape
        self.m = m 
        self.n = n 
        self.N = self.m - k

        #--- important variables
        self.sigma_eta = 0.0
        self.ln_L      = 0.0
        self.ln_det_I  = 0.0
        self.ln_det_C  = 0.0
        self.ln_det_HH = 0.0
        self.nit       = 0

        #--- Compute ln(det(H'*H)) [does not depend on noise / covariance]
        U = np.linalg.cholesky(self.H.T @ self.H)
        for i in range(0,self.n):
            self.ln_det_HH += math.log(U[i,i])
        self.ln_det_HH *= 2.0
 
        #--- FullCov or AmmarGrag
        if self.cov.Nmodels==1 and self.cov.noisemodel_names[0]=='White':
            self.method = OLS()
            if self.verbose==True:
                print('----------------\n  Ordinary LS\n----------------')
        elif obs.percentage_gaps>50:
            self.method = FullCov()
            if self.verbose==True:
                print('----------------\n  FullCov\n----------------')
        else:
            self.method = AmmarGrag()
            if self.verbose==True:
                print('----------------\n  AmmarGrag\n----------------')



    def compute_ln_det_I(self,C_theta):
        """ compute log(det(C_theta^{-1})), result stored in class variable

        Args:
            C_theta (matrix float nxn): inv(H'*invC*H)
        """

        #--- Compute ln_det_I 
        U = np.linalg.cholesky(C_theta)
        self.ln_det_I = 0.0
        for i in range(0,self.n):
            self.ln_det_I -= math.log(U[i,i])
        self.ln_det_I *= 2.0



    def log_likelihood(self,param,samenoise=False):
        """ Compute log likelihood vale

        Args:
            param (float array): fractions + noise model parameters

        Returns:
            value of log-likelihood (reversed sign)
        """

        if samenoise==False:
            #--- First, make sure noise parameters are inside range
            penalty = self.cov.compute_penalty(param)

            #--- Compute new covariance matrix
            t = self.cov.create_t(self.m,param)
        else:
            penalty = 0.0
            t = []

        #--- least-squares
        [theta,C_theta,self.ln_det_C,self.sigma_eta] = \
	     self.method.compute_leastsquares(t,self.H,self.x,self.F,samenoise)

        #--- Compute log-likelihood
        logL = -0.5 * (self.N*math.log(2*math.pi) + self.ln_det_C + \
			   2.0*(self.N)*math.log(self.sigma_eta) + self.N)

        #--- RMLE
        if self.useRMLE==True:
            C_theta *= math.pow(self.sigma_eta,2.0)
            self.compute_ln_det_I(C_theta)
            logL += -0.5*(self.ln_det_I - self.ln_det_HH)
       
        return -logL + penalty



    def estimate_parameters(self):
        """ Using Nelder-Mead, estimate least-squares + noise parameters
        """

        if self.cov.Nparam>0:
            #--- Create intial guess
            param0 = [0.1]*self.cov.Nparam

            #--- search for maximum (-minimum) log-likelihood value
            result=minimize(self.log_likelihood, param0, method='nelder-mead',\
		 		      options={'maxiter': 10000,'xatol':1.0e-6})

            #--- Check results
            if result.success==False:
                print('Minimisation failed! - {0:s}'.format(result.message))
                sys.exit()

            #--- store results
            self.ln_L    = -result.fun
            self.nit     = result.nit
            noise_params = result.x

        else:
            noise_params = []
            self.ln_L    = -self.log_likelihood(noise_params)
            self.nit     = 0
 

        #--- Now that noise parameters have been established, compute final
        #    values for the trajectory model
        t = self.cov.create_t(self.m,noise_params)
        [theta,C_theta,ln_det_C,self.sigma_eta] = \
		      self.method.compute_leastsquares(t,self.H,self.x,self.F)

        #--- Apply sigma_eta to get real C_theta
        C_theta *= pow(self.sigma_eta,2.0)

        #--- Compute final ln_det_I 
        self.compute_ln_det_I(C_theta)

        return [theta,C_theta,noise_params,self.sigma_eta]
							
   

    def test_new_offset(self):
        """ Add a new offset to each epoch and compute likelihood

        Returns:
            dln_new (array float): new log-likelihood - old log_likelihood
        """

        #--- Constant
        EPS = 1.0e-6

        #--- create array with offsets indices
        obs = Observations()
        offsets = obs.offsets
        [m,n] = self.H.shape
        offset_index = []
        for i in range(1,len(obs.data.index)):
            for j in range(0,len(offsets)):
                if obs.data.index[i-1]<offsets[j] and \
					obs.data.index[i]+EPS>offsets[j]:
                    if not i in offset_index:
                        offset_index.append(i)

        #--- Estimate noise parameters
        [theta,C_theta,noise_params,sigma_eta] = self.estimate_parameters()

        #--- Compute covariance matrix (again... but need t)
        t = self.cov.create_t(self.m,noise_params)

        #--- Compute log-likelihood
        ln_L = -self.log_likelihood(noise_params)

        #--- Add column and omit offset on first epoch (is nominal bias)
        self.H = np.c_[self.H, np.ones(self.m)]
        [m,n] = self.H.shape
        self.H[0,n-1] = 0.0

        #--- For rows 1 to m, compute log-likelihood improvement
        dln_L_new = [0.0]*self.m
        for i in range(1,len(obs.data.index)):
       
            #--- if not gap and not already an offset
            if np.isnan(obs.data.iloc[i,0])==False and i not in offset_index:
            
                #--- update ln(det(H'*H))
                if self.useRMLE==True:
                    U = np.linalg.cholesky(self.H.T @ self.H)
                    self.ln_det_HH = 0.0
                    for j in range(0,n):
                        self.ln_det_HH += math.log(U[j,j])
                    self.ln_det_HH *= 2.0

                #--- Compute log-likelihood
                dln_L_new[i] = -self.log_likelihood(noise_params,True) - ln_L
 
            #--- prepare next round
            self.H[i,n-1] = 0.0

        return dln_L_new 



    def show_results(self,output):
        """ Show the user some info on screen and save in json-output dict

        Args:
            output (dictionary) : where we store estimated values
        """

        #--- Information criteria
        k   = self.cov.Nparam + self.n + 1
        AIC = 2.0*k - 2.0*self.ln_L
        BIC = k*math.log(self.N) - 2.0*self.ln_L
        KIC = BIC + self.ln_det_I

        if self.verbose==True:
            print('Number of iterations : {0:d}'.format(self.nit))
            print('min log(L)           : {0:f}'.format(self.ln_L))
            print('ln_det_I             : {0:f}'.format(self.ln_det_I))
            print('ln_det_HH            : {0:f}'.format(self.ln_det_HH)) 
            print('ln_det_C             : {0:f}'.format(self.ln_det_C))
            print('AIC                  : {0:f}'.format(AIC))
            print('BIC                  : {0:f}'.format(BIC))
            print('KIC                  : {0:f}'.format(KIC))
            print('driving noise        : {0:f}'.format(self.sigma_eta))

        output['ln_L'] = self.ln_L
        output['ln_det_I'] = self.ln_det_I
        output['ln_det_HH'] = self.ln_det_HH
        output['driving_noise'] = self.sigma_eta
        output['ln_det_C'] = self.ln_det_C
        output['AIC'] = AIC
        output['BIC'] = BIC
        output['KIC'] = KIC
